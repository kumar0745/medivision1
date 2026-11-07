import hmac
import os
import socket
import struct

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

SCANNER_TOKEN = os.environ.get("SCANNER_TOKEN", "")
MAX_BYTES = int(os.environ.get("MAX_SCAN_BYTES", str(8 * 1024 * 1024)))
CLAMD_HOST = os.environ.get("CLAMD_HOST", "127.0.0.1")
CLAMD_PORT = int(os.environ.get("CLAMD_PORT", "3310"))

if len(SCANNER_TOKEN) < 32:
    raise RuntimeError("SCANNER_TOKEN must be a unique secret with at least 32 characters.")

app = FastAPI(title="MediVision private malware scanner", docs_url=None, redoc_url=None)


def clamd_request(command: bytes, timeout: float = 5.0) -> bytes:
    with socket.create_connection((CLAMD_HOST, CLAMD_PORT), timeout=timeout) as client:
        client.settimeout(timeout)
        client.sendall(b"n" + command + b"\n")
        return client.recv(4096)


def scan_with_clamd(content: bytes) -> str:
    with socket.create_connection((CLAMD_HOST, CLAMD_PORT), timeout=20.0) as client:
        client.settimeout(30.0)
        client.sendall(b"nINSTREAM\n")
        for offset in range(0, len(content), 1024 * 1024):
            chunk = content[offset:offset + 1024 * 1024]
            client.sendall(struct.pack("!I", len(chunk)))
            client.sendall(chunk)
        client.sendall(struct.pack("!I", 0))
        return client.recv(4096).decode("utf-8", errors="replace").strip()


@app.get("/health")
def health():
    try:
        result = clamd_request(b"PING")
        if b"PONG" not in result:
            raise RuntimeError("Unexpected ClamAV response")
    except Exception:
        raise HTTPException(503, "ClamAV daemon is unavailable or still loading signatures.")
    return {"status": "ok", "engine": "ClamAV"}


@app.post("/scan")
async def scan(request: Request, authorization: str | None = Header(default=None)):
    expected = f"Bearer {SCANNER_TOKEN}"
    if not authorization or not hmac.compare_digest(authorization, expected):
        raise HTTPException(401, "Unauthorized scanner request.")

    declared = request.headers.get("content-length")
    if declared:
        try:
            if int(declared) > MAX_BYTES:
                raise HTTPException(413, "File exceeds scanner size limit.")
        except ValueError:
            raise HTTPException(400, "Invalid content length.")

    content = await request.body()
    if not content:
        raise HTTPException(400, "Empty files cannot be scanned.")
    if len(content) > MAX_BYTES:
        raise HTTPException(413, "File exceeds scanner size limit.")

    try:
        result = await run_in_threadpool(scan_with_clamd, content)
    except Exception:
        raise HTTPException(503, "ClamAV could not complete the scan.")

    if "FOUND" in result:
        return JSONResponse(status_code=422, content={"clean": False, "engine": "ClamAV"})
    if "OK" not in result:
        raise HTTPException(503, "ClamAV returned an inconclusive result.")
    return {"clean": True, "engine": "ClamAV"}
