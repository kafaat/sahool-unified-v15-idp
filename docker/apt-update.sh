#!/bin/sh
# SAHOOL apt-get update with mirror fallback
# Usage: COPY docker/apt-update.sh /usr/local/bin/
#        RUN apt-update.sh && apt-get install -y --no-install-recommends <packages>
#
# Falls back to mirrors when default repos are unreachable (DNS/network)
# Supports: Debian (bookworm+, DEB822 & legacy), Ubuntu (archive.ubuntu.com)

set -e

switch_to_mirror() {
    echo "Switching apt sources to Aliyun mirror..."
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
}

# Check if default repos are reachable BEFORE apt-get update.
# apt-get update can succeed from cache even when DNS is broken,
# causing apt-get install to fail later when downloading .deb files.
dns_ok=true
if ! timeout 10 getent hosts deb.debian.org >/dev/null 2>&1 && \
   ! timeout 10 getent hosts archive.ubuntu.com >/dev/null 2>&1; then
    dns_ok=false
    echo "Cannot resolve default apt repos, switching to mirror..."
    switch_to_mirror
fi

if apt-get update; then
    exit 0
fi

echo "apt-get update failed with default sources, attempting mirror fallback..."

# apt-get update failed — switch mirrors if we haven't already
if [ "$dns_ok" = true ]; then
    switch_to_mirror
fi

apt-get update
