# Kong SSL/TLS Certificates

This directory contains SSL/TLS certificates for Kong API Gateway HTTPS support.

## Quick Start (Development)

Generate self-signed certificates for local development:

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout server.key \
  -out server.crt \
  -days 365 \
  -subj "/C=SA/ST=Riyadh/L=Riyadh/O=SAHOOL/OU=Development/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

chmod 600 server.key
chmod 644 server.crt
```

## Production (Let's Encrypt)

For production, use Let's Encrypt with Certbot:

```bash
certbot certonly --standalone -d api.sahool.app
cp /etc/letsencrypt/live/api.sahool.app/fullchain.pem server.crt
cp /etc/letsencrypt/live/api.sahool.app/privkey.pem server.key
```

## Security Notes

- Never commit private keys to version control
- Use `.gitignore` to exclude sensitive files
- Rotate certificates before expiration
