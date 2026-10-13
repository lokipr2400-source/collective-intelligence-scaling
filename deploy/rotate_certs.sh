#!/bin/bash
set -e
CERT_DIR="./certs"
BACKUP_DIR="./certs/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp "$CERT_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true

echo "Generating new client certificate..."
openssl genrsa -out "$CERT_DIR/client.key" 4096
openssl req -new -key "$CERT_DIR/client.key" -out "$CERT_DIR/client.csr" \
  -subj "/C=US/ST=Philadelphia/L=Philadelphia/O=QUADRA/CN=langgraph-agent-$(date +%s)"
openssl x509 -req -in "$CERT_DIR/client.csr" \
  -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial \
  -out "$CERT_DIR/client.crt" -days 90 -sha256
rm "$CERT_DIR/client.csr"

echo "New client certificate issued. Restart Caddy or reload config to apply."
echo "Old certificates backed up to $BACKUP_DIR"
