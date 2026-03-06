#!/bin/sh
# SAHOOL apt-get update with mirror fallback
# Usage: COPY docker/apt-update.sh /usr/local/bin/
#        RUN apt-update.sh && apt-get install -y --no-install-recommends <packages>
#
# Falls back to mirrors when default repos are unreachable (DNS/network)
# Supports: Debian (bookworm+, DEB822 & legacy), Ubuntu (archive.ubuntu.com)

set -e

if apt-get update 2>/dev/null; then
    exit 0
fi

echo "apt-get update failed, switching to Aliyun mirror..."

# Debian DEB822 format (bookworm+)
if [ -f /etc/apt/sources.list.d/debian.sources ]; then
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources
# Ubuntu DEB822 format (noble+)
elif [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then
    sed -i 's|archive.ubuntu.com|mirrors.aliyun.com|g; s|security.ubuntu.com|mirrors.aliyun.com|g' /etc/apt/sources.list.d/ubuntu.sources
# Legacy sources.list (Debian or Ubuntu)
elif [ -f /etc/apt/sources.list ]; then
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g; s|archive.ubuntu.com|mirrors.aliyun.com|g; s|security.ubuntu.com|mirrors.aliyun.com|g' /etc/apt/sources.list
fi

apt-get update
