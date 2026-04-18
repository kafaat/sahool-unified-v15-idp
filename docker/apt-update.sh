#!/bin/sh
# SAHOOL apt-get update with mirror-first fallback and retry
# Usage: COPY docker/apt-update.sh /usr/local/bin/
#        RUN apt-update.sh && apt-get install -y --no-install-recommends <packages>
#
# Strategy: mirror-first (Aliyun → Tencent → official deb.debian.org)
# Reason: in restricted/slow-network environments the official repo is often
# reachable for the small metadata fetch in apt-get update but then drops during
# the larger .deb downloads in apt-get install. Always using a mirror avoids this.
#
# Supports: Debian (bookworm+, DEB822 & legacy), Ubuntu (archive.ubuntu.com)

set -e

MAX_RETRIES=3
RETRY_DELAY=5

switch_to_mirror() {
    mirror_host="${1:-mirrors.aliyun.com}"
    echo "Switching apt sources to ${mirror_host}..."
    # Debian DEB822 format (bookworm+)
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then
        sed -i "s|deb.debian.org|${mirror_host}|g; \
                s|mirrors.aliyun.com|${mirror_host}|g; \
                s|mirrors.cloud.tencent.com|${mirror_host}|g" \
            /etc/apt/sources.list.d/debian.sources
    # Ubuntu DEB822 format (noble+)
    elif [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then
        sed -i "s|archive.ubuntu.com|${mirror_host}|g; \
                s|security.ubuntu.com|${mirror_host}|g; \
                s|mirrors.aliyun.com|${mirror_host}|g; \
                s|mirrors.cloud.tencent.com|${mirror_host}|g" \
            /etc/apt/sources.list.d/ubuntu.sources
    # Legacy sources.list (Debian or Ubuntu)
    elif [ -f /etc/apt/sources.list ]; then
        sed -i "s|deb.debian.org|${mirror_host}|g; \
                s|archive.ubuntu.com|${mirror_host}|g; \
                s|security.ubuntu.com|${mirror_host}|g; \
                s|mirrors.aliyun.com|${mirror_host}|g; \
                s|mirrors.cloud.tencent.com|${mirror_host}|g" \
            /etc/apt/sources.list
    fi
}

# try_apt_update runs apt-get update with retries and validates the result.
# Returns 0 only if apt-get update succeeds WITHOUT partial fetch warnings.
try_apt_update() {
    attempt=1
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
        echo "apt-get update attempt ${attempt}/${MAX_RETRIES}..."
        update_output=$(apt-get update -o Acquire::Retries=3 2>&1) && rc=0 || rc=$?
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
            echo "Retrying in ${RETRY_DELAY}s..."
            sleep "$RETRY_DELAY"
            RETRY_DELAY=$((RETRY_DELAY * 2))
        fi
        attempt=$((attempt + 1))
    done
    return 1
}

# Mirror-first strategy: always switch to a fast/reliable mirror before apt-get update.
# This ensures both apt-get update AND apt-get install use the same mirror — avoiding
# the failure mode where update succeeds (small files) but install fails (large .deb).

# Attempt 1: Aliyun mirror (primary)
switch_to_mirror "mirrors.aliyun.com"
if try_apt_update; then
    exit 0
fi

echo "Aliyun mirror failed, attempting Tencent mirror..."

# Attempt 2: Tencent mirror
switch_to_mirror "mirrors.cloud.tencent.com"
if try_apt_update; then
    exit 0
fi

echo "Tencent mirror failed, attempting official deb.debian.org..."

# Attempt 3: official repos as last resort
switch_to_mirror "deb.debian.org"
try_apt_update
