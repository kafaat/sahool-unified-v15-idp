#!/bin/sh
# SAHOOL apt-get update with mirror-first fallback, retry, and multi-mirror install fallback
# Usage: COPY docker/apt-update.sh /usr/local/bin/
#        RUN apt-update.sh && apt-get install -y --no-install-recommends <packages>
#
# Strategy (two phases):
#   Phase 1 – Update: try each mirror with MAX_RETRIES attempts until one succeeds for
#             apt-get update (metadata download).
#   Phase 2 – Fallback registration: after the primary mirror succeeds, append the
#             remaining mirrors as additional sources and re-run apt-get update
#             (--no-list-cleanup keeps what we already fetched). This means
#             apt-get install sees ALL mirrors for .deb downloads and automatically
#             retries with the next mirror if one drops an I/O error mid-download —
#             without any changes to individual service Dockerfiles.
#
# Supports: Debian (bookworm+, DEB822 & legacy), Ubuntu (archive.ubuntu.com)

set -e

# One attempt per mirror — we have 5 mirrors, so retrying the same failing one
# wastes time that is better spent trying the next mirror in the list.
MAX_RETRIES=1
# Hard wall-clock limit per apt-get update attempt.
# Connection setup on constrained networks can take ~60 s before any data flows;
# bookworm/main Packages is ~8.8 MB and can take >180 s on a slow link, so use
# 360 s to give enough headroom for connection + full index download.
UPDATE_TIMEOUT=360

# Write apt resilience config early so both apt-get update AND apt-get install
# benefit from higher retries and longer per-connection timeouts.
mkdir -p /etc/apt/apt.conf.d
# Acquire::Languages=none  — skip translation/i18n index files (saves ~5-20 MB of downloads)
# Acquire::Pdiffs=false    — always fetch full indexes instead of incremental diffs
# Pipeline-Depth=0         — disable HTTP pipelining (avoids I/O errors on some mirrors)
# Retry::Delay=10          — wait 10 s between per-file retries (avoids hammering a slow mirror)
printf 'Acquire::http::Timeout "180";\nAcquire::https::Timeout "180";\nAcquire::Retries "5";\nAcquire::Retry::Delay "10";\nAcquire::http::Pipeline-Depth "0";\nAcquire::Languages "none";\nAcquire::Pdiffs "false";\nAPT::Get::Assume-Yes "true";\n' \
    > /etc/apt/apt.conf.d/99sahool-resilience

# ─────────────────────────────────────────────────────────────────────────────
# Mirror list – ordered by reliability for apt-get install (large .deb files).
# Tencent first because Aliyun's debian-security endpoint has been observed to
# time out on large downloads (>1 MB) even when apt-get update succeeds.
# ─────────────────────────────────────────────────────────────────────────────
ALL_MIRRORS="mirrors.cloud.tencent.com mirrors.aliyun.com mirrors.ustc.edu.cn mirrors.huaweicloud.com deb.debian.org"

# ─────────────────────────────────────────────────────────────────────────────
# Helper: rewrite the primary URI in sources to point at mirror_host.
# Works for DEB822 (bookworm debian.sources / ubuntu.sources) and legacy
# sources.list. Each call REPLACES whatever mirror is currently primary.
# ─────────────────────────────────────────────────────────────────────────────
_ALL_MIRROR_HOSTS="deb.debian.org archive.ubuntu.com security.ubuntu.com mirrors.aliyun.com mirrors.cloud.tencent.com mirrors.ustc.edu.cn mirrors.huaweicloud.com"

switch_to_mirror() {
    mirror_host="${1:-mirrors.aliyun.com}"
    echo "Switching apt primary source to ${mirror_host}..."

    # Build sed expression that replaces ANY known mirror with the new one.
    _sed_expr=""
    for _h in $_ALL_MIRROR_HOSTS; do
        _sed_expr="${_sed_expr}s|${_h}|${mirror_host}|g; "
    done

    if [ -f /etc/apt/sources.list.d/debian.sources ]; then
        sed -i "${_sed_expr}" /etc/apt/sources.list.d/debian.sources
    elif [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then
        sed -i "${_sed_expr}" /etc/apt/sources.list.d/ubuntu.sources
    elif [ -f /etc/apt/sources.list ]; then
        sed -i "${_sed_expr}" /etc/apt/sources.list
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper: append the remaining mirrors as additional sources so apt-get install
# can automatically fail over to a working mirror when a .deb download fails.
# We append using DEB822 stanzas (debian.sources) or legacy deb lines.
# After appending, a quick --no-list-cleanup update registers the new sources.
# ─────────────────────────────────────────────────────────────────────────────
add_fallback_mirrors() {
    primary_mirror="$1"
    echo "Registering fallback mirrors for apt-get install resilience..."

    # Determine what suites/components the primary source covers so we replicate
    # the same structure for each fallback.  We read it directly from the file.
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then
        # DEB822 — parse Suites and Components from the existing file.
        _suites=$(grep -i '^Suites:' /etc/apt/sources.list.d/debian.sources | head -1 | sed 's/^Suites: *//')
        _components=$(grep -i '^Components:' /etc/apt/sources.list.d/debian.sources | head -1 | sed 's/^Components: *//')
        [ -z "$_suites" ]     && _suites="bookworm bookworm-updates"
        [ -z "$_components" ] && _components="main"

        for _m in $ALL_MIRRORS; do
            [ "$_m" = "$primary_mirror" ] && continue
            printf '\nTypes: deb\nURIs: https://%s/debian\nSuites: %s\nComponents: %s\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg\n' \
                "$_m" "$_suites" "$_components" \
                >> /etc/apt/sources.list.d/debian.sources
        done

    elif [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then
        _suites=$(grep -i '^Suites:' /etc/apt/sources.list.d/ubuntu.sources | head -1 | sed 's/^Suites: *//')
        _components=$(grep -i '^Components:' /etc/apt/sources.list.d/ubuntu.sources | head -1 | sed 's/^Components: *//')
        [ -z "$_suites" ]     && _suites="noble noble-updates"
        [ -z "$_components" ] && _components="main restricted universe"

        for _m in $ALL_MIRRORS; do
            [ "$_m" = "$primary_mirror" ] && continue
            printf '\nTypes: deb\nURIs: https://%s/ubuntu\nSuites: %s\nComponents: %s\n' \
                "$_m" "$_suites" "$_components" \
                >> /etc/apt/sources.list.d/ubuntu.sources
        done

    elif [ -f /etc/apt/sources.list ]; then
        # Legacy sources.list — detect distro from existing lines and append.
        if grep -q "ubuntu" /etc/apt/sources.list; then
            _base_url="archive.ubuntu.com/ubuntu"
            _suite=$(grep -m1 '^deb ' /etc/apt/sources.list | awk '{print $3}')
            _components=$(grep -m1 '^deb ' /etc/apt/sources.list | cut -d' ' -f4-)
            [ -z "$_suite" ]      && _suite="noble"
            [ -z "$_components" ] && _components="main restricted universe"
            for _m in $ALL_MIRRORS; do
                [ "$_m" = "$primary_mirror" ] && continue
                printf 'deb https://%s/ubuntu %s %s\n' "$_m" "$_suite" "$_components" \
                    >> /etc/apt/sources.list
            done
        else
            _suite=$(grep -m1 '^deb ' /etc/apt/sources.list | awk '{print $3}')
            _components=$(grep -m1 '^deb ' /etc/apt/sources.list | cut -d' ' -f4-)
            [ -z "$_suite" ]      && _suite="bookworm"
            [ -z "$_components" ] && _components="main"
            for _m in $ALL_MIRRORS; do
                [ "$_m" = "$primary_mirror" ] && continue
                printf 'deb https://%s/debian %s %s\n' "$_m" "$_suite" "$_components" \
                    >> /etc/apt/sources.list
            done
        fi
    fi

    # Register the new fallback sources without discarding existing lists.
    # -qq suppresses most output; errors are still shown.
    echo "Running apt-get update --no-list-cleanup to register fallback mirrors..."
    timeout "${UPDATE_TIMEOUT}" apt-get update --no-list-cleanup \
        -o Acquire::Languages=none \
        -o Acquire::Pdiffs=false \
        -qq 2>&1 || true   # non-fatal: primary already succeeded
}

# ─────────────────────────────────────────────────────────────────────────────
# try_apt_update: run apt-get update with retries, validate no partial fetches.
# Returns 0 only if apt-get update succeeds WITHOUT "W: Failed to fetch" lines.
# ─────────────────────────────────────────────────────────────────────────────
try_apt_update() {
    _delay=5
    attempt=1
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
        echo "apt-get update attempt ${attempt}/${MAX_RETRIES} (timeout ${UPDATE_TIMEOUT}s)..."
        update_output=$(timeout "${UPDATE_TIMEOUT}" apt-get update \
            -o Acquire::Retries=1 \
            -o Acquire::Languages=none \
            -o Acquire::Pdiffs=false \
            2>&1) && rc=0 || rc=$?
        echo "$update_output"

        if [ "$rc" -eq 0 ]; then
            if echo "$update_output" | grep -qi "W: Failed to fetch"; then
                echo "Warning: apt-get update returned 0 but some index files failed to download."
                rc=1
            else
                return 0
            fi
        fi

        if [ "$attempt" -lt "$MAX_RETRIES" ]; then
            echo "Retrying in ${_delay}s..."
            sleep "$_delay"
            _delay=$((_delay * 2))
        fi
        attempt=$((attempt + 1))
    done
    return 1
}

# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: find the first mirror that serves apt-get update successfully.
# Phase 2: register the remaining mirrors as install-time fallbacks.
# ─────────────────────────────────────────────────────────────────────────────
for mirror in $ALL_MIRRORS; do
    switch_to_mirror "$mirror"
    if try_apt_update; then
        add_fallback_mirrors "$mirror"
        exit 0
    fi
    echo "Mirror ${mirror} failed, trying next..."
done

echo "apt-update.sh: all mirrors exhausted — apt-get update failed." >&2
exit 1
