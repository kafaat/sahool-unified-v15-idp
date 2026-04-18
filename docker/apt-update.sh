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
# Supports: Debian (bookworm+, DEB822 & legacy), Ubuntu (archive.ubuntu.com)

set -e

MAX_RETRIES=3
RETRY_DELAY=5
# Hard wall-clock limit per apt-get update attempt. Mirrors delivering at
# 863 B/s can hold the build for 10+ minutes; 120 seconds abandons them fast
# enough to try the next mirror without unacceptable total build time. Bumped
# from 90s to 120s because deb.debian.org metadata fetch in APAC can legitimately
# take 100+ seconds on a cold connection.
UPDATE_TIMEOUT=120

# Mirrors attempted in order. Each entry is an apt mirror host that serves
# /debian and /debian-security. Aliyun first because it has the broadest
# geographic coverage; Tencent second as a strong APAC fallback; Tsinghua
# and USTC are academic mirrors with excellent availability inside China;
# deb.debian.org is the final fallback (always works, but can be slow).
#
# To add or reorder mirrors, edit this list — no other change needed.
MIRRORS="mirrors.aliyun.com mirrors.cloud.tencent.com mirrors.tuna.tsinghua.edu.cn mirrors.ustc.edu.cn deb.debian.org"

# Write apt resilience config early so both apt-get update AND apt-get install
# benefit from higher retries and longer per-connection timeouts.
# This is critical when mirrors serve metadata (small files) fine but time out
# on large .deb downloads (e.g. openssl 1.4 MB from mirrors.aliyun.com/debian-security).
mkdir -p /etc/apt/apt.conf.d
printf 'Acquire::http::Timeout "120";\nAcquire::https::Timeout "120";\nAcquire::Retries "10";\nAPT::Get::Assume-Yes "true";\n' \
    > /etc/apt/apt.conf.d/99sahool-resilience

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
try_apt_update() {
    attempt=1
    delay="$RETRY_DELAY"
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
        echo "apt-get update attempt ${attempt}/${MAX_RETRIES} (timeout ${UPDATE_TIMEOUT}s)..."
        update_output=$(timeout "${UPDATE_TIMEOUT}" apt-get update -o Acquire::Retries=1 2>&1) && rc=0 || rc=$?
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
            echo "Retrying in ${delay}s..."
            sleep "$delay"
            delay=$((delay * 2))
        fi
        attempt=$((attempt + 1))
    done
    return 1
}

# Mirror-first strategy: iterate through the mirror list until one succeeds.
# Each mirror gets its own retry loop (MAX_RETRIES attempts with backoff).
# Total worst-case budget: len(MIRRORS) × MAX_RETRIES × UPDATE_TIMEOUT
# = 5 × 3 × 120s = 1800s, but typical success is under 15s on the first mirror.
for _mirror in $MIRRORS; do
    switch_to_mirror "$_mirror"
    if try_apt_update; then
        exit 0
    fi
    echo "${_mirror} failed, trying next mirror..."
done

echo "ERROR: all mirrors (${MIRRORS}) failed to respond to apt-get update." >&2
exit 1
