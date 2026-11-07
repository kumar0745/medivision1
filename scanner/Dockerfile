FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends clamav clamav-daemon ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/scanner
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY clamd.conf /etc/clamav/clamd.conf
COPY scanner.py start.sh ./
RUN chmod 755 /srv/scanner/start.sh \
    && mkdir -p /run/clamav /var/log/clamav /var/lib/clamav \
    && chown -R clamav:clamav /run/clamav /var/log/clamav /var/lib/clamav

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=8s --start-period=180s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=5).read()"
CMD ["/srv/scanner/start.sh"]
