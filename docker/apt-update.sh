#!/bin/sh
# SAHOOL apt-get update with mirror-first fallback and retry
# Usage: COPY docker/apt-update.sh /usr/local/bin/
#        RUN apt-update.sh && apt-get install -y --no-install-recommends <packages>
#
# Strategy: mirror-first fallback chain
#   Aliyun → Tencent → Tsinghua → USTC → official deb.debian.org
# Reason: in restricted/slow-network environments the official repo is often
# reachable for the small metadata fetch in apt-get update but then drops during
# the larger .deb downloads in apt-get install. Always using a mirror avoids this.
# Running against several mirrors in sequence also protects against a single
# mirror going down mid-build (e.g. cases where local apt-update.sh drifts out
# of git and picks an unreliable mirror like mirrors.huaweicloud.com).
#
# Supports: Debian bookworm (DEB822 and legacy sources.list). The fallback
# chain — including `deb.debian.org` — is Debian-specific. If the Dockerfile
# base image is Ubuntu, override SAHOOL_APT_MIRRORS with a chain ending in
# `archive.ubuntu.com` (see env-override section below).
#
# Environment overrides (all optional):
#   SAHOOL_APT_MIRRORS        space-separated list; defaults to the chain above
#   SAHOOL_APT_MAX_RETRIES    per-mirror retry count; default 3
#   SAHOOL_APT_UPDATE_TIMEOUT per-attempt wall clock (seconds); default 120
#   SAHOOL_APT_TOTAL_BUDGET   hard overall wall clock (seconds); default 600
#                             (exit 1 once exceeded; set to 0 to disable)

set -e

# Validate a SAHOOL_APT_* env override is a non-negative integer. Catches
# typos like SAHOOL_APT_MAX_RETRIES=foo (or empty) before they reach `[`/
# `timeout` and abort the build under set -e with a confusing parse error.
_validate_int() {
    _name=$1
    _value=$2
    case "$_value" in
        ''|*[!0-9]*)
            echo "ERROR: ${_name}='${_value}' is not a non-negative integer." >&2
            echo "       Set ${_name} to a whole number (e.g. ${_name}=120)." >&2
            exit 1
            ;;
    esac
}

MAX_RETRIES="${SAHOOL_APT_MAX_RETRIES:-3}"
_validate_int SAHOOL_APT_MAX_RETRIES "$MAX_RETRIES"
RETRY_DELAY=5
# Hard wall-clock limit per apt-get update attempt. Mirrors delivering at
# 863 B/s can hold the build for 10+ minutes; 120 seconds abandons them fast
# enough to try the next mirror without unacceptable total build time. Bumped
# from 90s to 120s because deb.debian.org metadata fetch in APAC can legitimately
# take 100+ seconds on a cold connection.
UPDATE_TIMEOUT="${SAHOOL_APT_UPDATE_TIMEOUT:-120}"
_validate_int SAHOOL_APT_UPDATE_TIMEOUT "$UPDATE_TIMEOUT"

# Hard overall wall-clock cap across ALL mirrors and retries. Without this,
# the worst case (all mirrors slow + all retries backing off) is
#   MIRRORS × (MAX_RETRIES × UPDATE_TIMEOUT + exponential-backoff sleeps)
# which at defaults (5, 3, 120) works out to roughly 5 × (360 + 15) ≈ 1875 s
# ≈ 31 minutes — long enough to stall a parallel Compose build of 70 services
# even when each individual apt-get call is eventually going to succeed on a
# later mirror. 600 s lets the default chain try every mirror at least once
# at its full 120s timeout, then fail the build fast so operators can triage.
#
# Enforcement is "true hard cap": each per-attempt `timeout` and inter-retry
# `sleep` is bounded to MIN(configured, remaining-budget) so the script never
# overshoots by more than ~1 second of overhead per check.
TOTAL_BUDGET="${SAHOOL_APT_TOTAL_BUDGET:-600}"
_validate_int SAHOOL_APT_TOTAL_BUDGET "$TOTAL_BUDGET"
START_TS=$(date +%s)

# Mirrors attempted in order. Each entry is an apt mirror host that serves
# /debian and /debian-security. Aliyun first because it has the broadest
# geographic coverage; Tencent second as a strong APAC fallback; Tsinghua
# and USTC are academic mirrors with excellent availability inside China;
# deb.debian.org is the final fallback (always works, but can be slow).
#
# To add or reorder mirrors, set SAHOOL_APT_MIRRORS at build time — no code
# change needed.
MIRRORS="${SAHOOL_APT_MIRRORS:-mirrors.aliyun.com mirrors.cloud.tencent.com mirrors.tuna.tsinghua.edu.cn mirrors.ustc.edu.cn deb.debian.org}"

# Write apt resilience config early so subsequent `apt-get install` calls in
# the Dockerfile benefit from higher per-connection retries (10) and longer
# timeouts — critical when mirrors serve metadata fine but time out on large
# .deb downloads (e.g. openssl 1.4 MB from mirrors.aliyun.com/debian-security).
#
# NOTE: `apt-get update` below intentionally overrides Retries=1 via `-o` so
# it fails fast and hands off to the next mirror in our fallback chain. Letting
# apt's own 10x retry kick in would multiply the per-mirror wall clock by 10
# and defeat the whole point of the chain.
mkdir -p /etc/apt/apt.conf.d
printf 'Acquire::http::Timeout "120";\nAcquire::https::Timeout "120";\nAcquire::Retries "10";\nAPT::Get::Assume-Yes "true";\n' \
    > /etc/apt/apt.conf.d/99sahool-resilience

# Seconds remaining in TOTAL_BUDGET. Returns a very large number when the
# budget is disabled (TOTAL_BUDGET=0) so callers can use MIN() unconditionally
# and let the configured value win in the unbounded case.
remaining_budget() {
    if [ "$TOTAL_BUDGET" -le 0 ]; then
        echo 2147483647
        return
    fi
    _elapsed=$(( $(date +%s) - START_TS ))
    _remain=$(( TOTAL_BUDGET - _elapsed ))
    [ "$_remain" -lt 0 ] && _remain=0
    echo "$_remain"
}

# Exit immediately if the total wall-clock budget has been exceeded. Called
# between mirror attempts and before each retry so a pathological network
# can't hold the build longer than the operator wants.
check_total_budget() {
    [ "$TOTAL_BUDGET" -le 0 ] && return 0
    if [ "$(remaining_budget)" -le 0 ]; then
        _elapsed=$(( $(date +%s) - START_TS ))
        echo "ERROR: apt-update total budget (${TOTAL_BUDGET}s) exhausted after ${_elapsed}s; failing fast." >&2
        echo "       Override with SAHOOL_APT_TOTAL_BUDGET=<seconds> or 0 to disable." >&2
        exit 1
    fi
}

switch_to_mirror() {
    mirror_host="${1:-mirrors.aliyun.com}"
    echo "Switching apt sources to ${mirror_host}..."

    # Pick the first file that exists and rewrite every known mirror host in
    # it to the chosen one. Listing all candidate hosts — including ones that
    # may sneak in via locally modified apt-update.sh drift, like
    # mirrors.huaweicloud.com — keeps each fallback attempt deterministic.
    _target=""
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then
        _target=/etc/apt/sources.list.d/debian.sources
    elif [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then
        _target=/etc/apt/sources.list.d/ubuntu.sources
    elif [ -f /etc/apt/sources.list ]; then
        _target=/etc/apt/sources.list
    fi
    [ -z "$_target" ] && return 0

    sed -i \
        -e "s|deb.debian.org|${mirror_host}|g" \
        -e "s|archive.ubuntu.com|${mirror_host}|g" \
        -e "s|security.ubuntu.com|${mirror_host}|g" \
        -e "s|mirrors.aliyun.com|${mirror_host}|g" \
        -e "s|mirrors.cloud.tencent.com|${mirror_host}|g" \
        -e "s|mirrors.tuna.tsinghua.edu.cn|${mirror_host}|g" \
        -e "s|mirrors.ustc.edu.cn|${mirror_host}|g" \
        -e "s|mirrors.huaweicloud.com|${mirror_host}|g" \
        "$_target"
}

# try_apt_update runs apt-get update with retries and validates the result.
# Returns 0 only if apt-get update succeeds WITHOUT partial fetch warnings.
# Each per-attempt `timeout` and inter-retry `sleep` is bounded by the
# remaining TOTAL_BUDGET so the cap is a true hard wall-clock limit.
try_apt_update() {
    attempt=1
    delay="$RETRY_DELAY"
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
        check_total_budget
        # Bound this attempt's timeout to MIN(UPDATE_TIMEOUT, remaining-budget)
        # so a near-exhausted budget can't be overshot by a fresh 120s timer.
        _attempt_timeout=$(remaining_budget)
        [ "$_attempt_timeout" -gt "$UPDATE_TIMEOUT" ] && _attempt_timeout=$UPDATE_TIMEOUT
        echo "apt-get update attempt ${attempt}/${MAX_RETRIES} (timeout ${_attempt_timeout}s)..."
        update_output=$(timeout "${_attempt_timeout}" apt-get update -o Acquire::Retries=1 2>&1) && rc=0 || rc=$?
        echo "$update_output"

        if [ "$rc" -eq 0 ]; then
            # apt-get update returns 0 even when some index files fail to download.
            # Those show up as "W: Failed to fetch" warnings. Detect and treat as failure.
            if echo "$update_output" | grep -qi "W: Failed to fetch"; then
                echo "Warning: apt-get update returned 0 but some index files failed to download."
                rc=1
            else
                return 0
            fi
        fi

        if [ "$attempt" -lt "$MAX_RETRIES" ]; then
            # Bound the backoff sleep to remaining budget too — sleeping past
            # the cap would just waste time before the next check_total_budget
            # exits anyway.
            _sleep=$delay
            _remain=$(remaining_budget)
            [ "$_sleep" -gt "$_remain" ] && _sleep=$_remain
            if [ "$_sleep" -gt 0 ]; then
                echo "Retrying in ${_sleep}s..."
                sleep "$_sleep"
            fi
            delay=$((delay * 2))
        fi
        attempt=$((attempt + 1))
    done
    return 1
}

# Mirror-first strategy: iterate through the mirror list until one succeeds.
# Each mirror gets its own retry loop (MAX_RETRIES attempts with exponential
# backoff), and the outer loop short-circuits if the total wall-clock budget
# is blown. Typical success is under 15s on the first mirror; worst case is
# bounded by TOTAL_BUDGET rather than by mirror × retries × timeout math.
for _mirror in $MIRRORS; do
    check_total_budget
    switch_to_mirror "$_mirror"
    if try_apt_update; then
        exit 0
    fi
    echo "${_mirror} failed, trying next mirror..."
done

echo "ERROR: all mirrors (${MIRRORS}) failed to respond to apt-get update." >&2
exit 1
