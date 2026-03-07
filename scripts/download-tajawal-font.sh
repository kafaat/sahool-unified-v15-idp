#!/usr/bin/env bash
# Download Tajawal font files for self-hosting (offline-first)
# تحميل ملفات خط تجوال للاستضافة الذاتية
set -euo pipefail

FONT_DIR_WEB="apps/web/public/fonts"
FONT_DIR_ADMIN="apps/admin/public/fonts"
BASE_URL="https://fonts.gstatic.com/s/tajawal/v9"

WEIGHTS=("400" "500" "700")
FILES=("mI8cfspOoMOjmlQBVwz1.woff2" "mI8YfspOoMOjmlQBRwxi1A.woff2" "mI8anspOoMOjmlQBcj3XaQ.woff2")
NAMES=("Tajawal-Regular" "Tajawal-Medium" "Tajawal-Bold")

mkdir -p "$FONT_DIR_WEB" "$FONT_DIR_ADMIN"

for i in "${!WEIGHTS[@]}"; do
    weight="${WEIGHTS[$i]}"
    name="${NAMES[$i]}"
    echo "Downloading ${name}.woff2 (weight ${weight})..."
    curl -fsSL "${BASE_URL}/${FILES[$i]}" -o "${FONT_DIR_WEB}/${name}.woff2"
    cp "${FONT_DIR_WEB}/${name}.woff2" "${FONT_DIR_ADMIN}/${name}.woff2"
done

echo "Tajawal font files downloaded to ${FONT_DIR_WEB} and ${FONT_DIR_ADMIN}"
