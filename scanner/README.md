# MediVision private ClamAV scanner

This service is deliberately separate from Vercel Functions. It runs ClamAV in the same container as a small authenticated FastAPI service.

## Build and run locally

```bash
docker build -t medivision-clamav ./scanner
docker run --rm -p 8080:8080 \
  -e SCANNER_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')" \
  medivision-clamav
```

The command above generates a one-time local token for the container. For a remote host, use a secret manager rather than shell history, and do not expose the scanner directly to the public internet.

## Routes

- `GET /health`: returns 200 only after ClamAV responds to PING.
- `POST /scan`: requires `Authorization: Bearer <SCANNER_TOKEN>`, raw file bytes, and returns a clean verdict only when clamd explicitly returns OK.
- The scanner rejects empty files and files larger than `MAX_SCAN_BYTES` (default 8 MiB).
- Malware verdicts return 422. Scanner errors and inconclusive verdicts return 503.

The ClamAV TCP daemon listens only on loopback in this container. It is not exposed as a container port; the FastAPI API is the only network entrypoint.

## Backend Vercel configuration

Set the following **encrypted** environment variables on the FastAPI backend project:

- `MALWARE_SCANNER_URL`: private HTTPS origin of this scanner service.
- `MALWARE_SCANNER_TOKEN`: the exact same high-entropy token as `SCANNER_TOKEN`.

The backend sends file bytes to `POST /scan` and only stores the attachment after receiving HTTP 200 with `{"clean":true,"engine":"ClamAV"}`. Any timeout, missing service, malformed answer, unknown engine or infected result blocks the upload.

## Operational controls

- Put the scanner behind private networking or allow-list access from the backend only.
- Use TLS between the backend and scanner.
- Rotate the shared token in both services as one coordinated change.
- Monitor `/health`, signature-update logs and the container restart count.
- ClamAV signatures update in the container. The first signature download can take time; the health check remains 503 until clamd is ready.
- Run an EICAR test file in a private, non-production environment before enabling real uploads. Never place EICAR or malware samples in the production application.

The scanner is an integration scaffold in this repository; it is not deployed by the existing two Vercel projects.
