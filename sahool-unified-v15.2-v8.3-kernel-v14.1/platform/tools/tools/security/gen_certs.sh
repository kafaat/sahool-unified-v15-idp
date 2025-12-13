#!/usr/bin/env bash
set -euo pipefail

# Generates a local CA + service certs for mTLS (dev/prod bootstrap).
# Output: ./secrets/pki/

OUT_DIR="${1:-secrets/pki}"
mkdir -p "$OUT_DIR"

need(){ command -v "$1" >/dev/null 2>&1 || { echo "Missing $1"; exit 1; }; }
need openssl

echo "==> Generating CA"
openssl req -x509 -newkey rsa:4096 -days 3650 -nodes   -keyout "$OUT_DIR/ca.key" -out "$OUT_DIR/ca.crt"   -subj "/CN=sahool-local-ca"

gen_cert(){
  local name="$1"
  echo "==> Generating cert for $name"
  openssl req -newkey rsa:2048 -nodes     -keyout "$OUT_DIR/${name}.key" -out "$OUT_DIR/${name}.csr"     -subj "/CN=${name}"
  openssl x509 -req -in "$OUT_DIR/${name}.csr" -CA "$OUT_DIR/ca.crt" -CAkey "$OUT_DIR/ca.key" -CAcreateserial     -out "$OUT_DIR/${name}.crt" -days 825
  rm -f "$OUT_DIR/${name}.csr"
}

gen_cert "nats"
gen_cert "image-diagnosis-service"
gen_cert "disease-risk-service"
gen_cert "irrigation-advisor-service"
gen_cert "advisor-core-service"
gen_cert "equipment-service"

echo "✅ PKI generated in $OUT_DIR"
