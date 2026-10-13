# SECURITY.md

## API Key Management
- `MCP_API_KEY` is required for all tool endpoints.
- Minimum length: 32 bytes (generated via `secrets.token_urlsafe(32)`).
- Rotate by regenerating the key, updating the environment variable, and restarting the service. Old keys are immediately invalid.

## Certificate Rotation (mTLS)
Run the extended script:
```bash
./deploy/rotate_certs.sh
```
This generates a new client certificate, updates the CA serial, and can be hot-reloaded via Caddy.

## Logging
All tool calls emit JSON logs containing:
- timestamp
- thread_id (if present)
- tool name
- success/failure
- duration_ms

Configure Docker logging volume in `deploy/docker-compose.yml`.

## Network
- Bind MCP server to internal network only.
- Terminate TLS at Caddy.
- Enforce mTLS for any external client.
