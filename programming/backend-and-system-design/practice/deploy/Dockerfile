# Pinned by digest, because tags can move. Take a new digest on purpose, to update.
FROM python:3.14-slim@sha256:930e1abba7c4e8f96ed93e8012c35d174d7732752731bbd5e8e757d7ec6f3966 AS test
WORKDIR /src
COPY app/ .
# The build fails here if the tests fail, so a bad commit never becomes an image.
RUN python -m unittest -q test_server

FROM python:3.14-slim@sha256:930e1abba7c4e8f96ed93e8012c35d174d7732752731bbd5e8e757d7ec6f3966 AS runtime
WORKDIR /srv
# Copied from the test stage: an image cannot exist unless those tests passed.
COPY --from=test /src/server.py .
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
USER 65534:65534
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=2s --start-period=2s --retries=3 \
    CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/healthz', timeout=1)"]
# Exec form: python is PID 1 and gets SIGTERM directly. A shell as PID 1 may not pass it on.
CMD ["python", "server.py"]
