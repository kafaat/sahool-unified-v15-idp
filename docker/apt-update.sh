#!/bin/sh
# SAHOOL apt-get update with mirror fallback
# Usage: COPY docker/apt-update.sh /usr/local/bin/
#        RUN apt-update.sh && apt-get install -y --no-install-recommends <packages>
#
# Falls back to mirrors.aliyun.com when deb.debian.org is unreachable (DNS/network)
# Handles both DEB822 format (bookworm+) and legacy sources.list

set -e

if apt-get update 2>/dev/null; then
    exit 0
fi

echo "apt-get update failed, switching to Aliyun mirror..."

# Try DEB822 format first (Debian bookworm+), then legacy sources.list
if [ -f /etc/apt/sources.list.d/debian.sources ]; then
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources
elif [ -f /etc/apt/sources.list ]; then
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list
fi

apt-get update
