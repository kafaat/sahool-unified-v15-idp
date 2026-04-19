#!/bin/sh
# SAHOOL pip install with mirror-first fallback and per-mirror retry
# Usage: COPY docker/pip-install.sh /usr/local/bin/
#        RUN pip-install.sh -r requirements.txt
#        RUN pip-install.sh -c constraints.txt -r requirements.txt
#        RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1"
#
# Strategy: Aliyun → Tsinghua → Tencent → official PyPI
# Each mirror is tried up to MAX_RETRIES times with exponential back-off before
# moving to the next mirror. This handles transient failures (IncompleteRead,
# JSONDecodeError on the index, connection drops mid-download) that the bare ||
# chain cannot recover from because it never retries the same mirror.
#
# All arguments are forwarded verbatim to pip install (e.g. -r, -c, package names).

set -e

# Retries per mirror before moving to the next one.
MAX_RETRIES=3
# Base sleep between retries (seconds); doubles each attempt.
BASE_DELAY=10
# Per-request pip timeout in seconds.
PIP_TIMEOUT=600
# Per-request pip retry count (for individual chunk re-downloads within one attempt).
PIP_RETRIES=5

# pip install args forwarded from caller
INSTALL_ARGS="$*"

if [ -z "$INSTALL_ARGS" ]; then
    echo "Usage: pip-install.sh [pip install args...]" >&2
    exit 1
fi

# try_mirror <index_url> <trusted_host> [extra_trusted_host]
# Tries pip install up to MAX_RETRIES times against the given index URL.
# Returns 0 on first success, 1 if all retries fail.
try_mirror() {
    _index_url="$1"
    _trusted_host="$2"
    _extra_trusted_host="${3:-}"

    attempt=1
    delay=$BASE_DELAY
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
        echo "pip install attempt ${attempt}/${MAX_RETRIES} via ${_index_url} ..."

        if [ -n "$_extra_trusted_host" ]; then
            # shellcheck disable=SC2086
            pip install --no-cache-dir \
                --timeout="${PIP_TIMEOUT}" \
                --retries="${PIP_RETRIES}" \
                --prefer-binary \
                -i "${_index_url}" \
                --trusted-host "${_trusted_host}" \
                --trusted-host "${_extra_trusted_host}" \
                $INSTALL_ARGS && return 0
        else
            # shellcheck disable=SC2086
            pip install --no-cache-dir \
                --timeout="${PIP_TIMEOUT}" \
                --retries="${PIP_RETRIES}" \
                --prefer-binary \
                -i "${_index_url}" \
                --trusted-host "${_trusted_host}" \
                $INSTALL_ARGS && return 0
        fi

        if [ "$attempt" -lt "$MAX_RETRIES" ]; then
            echo "Attempt ${attempt} failed. Retrying in ${delay}s ..."
            sleep "$delay"
            delay=$((delay * 2))
        fi
        attempt=$((attempt + 1))
    done

    echo "All ${MAX_RETRIES} attempts via ${_index_url} failed."
    return 1
}

# Mirror 1: Alibaba Cloud (Aliyun) — primary
echo "=== pip-install.sh: trying Aliyun mirror ==="
if try_mirror \
    "https://mirrors.aliyun.com/pypi/simple/" \
    "mirrors.aliyun.com"; then
    exit 0
fi

echo "=== pip-install.sh: Aliyun failed, trying Tsinghua (TUNA) mirror ==="
# Mirror 2: Tsinghua University (TUNA) — secondary
if try_mirror \
    "https://pypi.tuna.tsinghua.edu.cn/simple/" \
    "pypi.tuna.tsinghua.edu.cn"; then
    exit 0
fi

echo "=== pip-install.sh: TUNA failed, trying Tencent Cloud mirror ==="
# Mirror 3: Tencent Cloud — tertiary
if try_mirror \
    "https://mirrors.cloud.tencent.com/pypi/simple" \
    "mirrors.cloud.tencent.com"; then
    exit 0
fi

echo "=== pip-install.sh: Tencent failed, trying official PyPI ==="
# Mirror 4: Official PyPI — last resort
if try_mirror \
    "https://pypi.org/simple" \
    "pypi.org" \
    "files.pythonhosted.org"; then
    exit 0
fi

echo "pip-install.sh: all mirrors exhausted — installation failed." >&2
exit 1
