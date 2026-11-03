#!/usr/bin/env bash
# Builds and runs the image on the local Docker daemon. No registry login and no cloud.
# Removes the images it built. A base image it had to pull is removed too.
# Skips the Docker part, saying so, if the daemon isn't running.
set -uo pipefail
cd "$(dirname "$0")"

echo "== manifests (parsed and checked, never deployed)"
uv run --quiet --no-project --python 3.14 --with pyyaml python check_manifests.py || exit 1

if ! docker info >/dev/null 2>&1; then
    echo "== docker daemon not running: image build and run SKIPPED"
    exit 0
fi

IMAGE=backend-lab-api:verify
BASE=$(sed -n 's/^FROM \([^ ]*\) AS test$/\1/p' Dockerfile)
PULLED=0
docker image inspect "$BASE" >/dev/null 2>&1 || PULLED=1
cleanup() {
    docker rm -f backend-lab-graceful backend-lab-shell >/dev/null 2>&1
    docker image rm -f "$IMAGE" >/dev/null 2>&1
    if [ "$PULLED" = 1 ]; then docker image rm -f "$BASE" >/dev/null 2>&1; fi
}
trap cleanup EXIT

echo "== build (the test stage must pass for the image to exist)"
docker build -q -t "$IMAGE" . >/dev/null || { echo "build FAILED"; exit 1; }
echo "  built; size $(docker image inspect "$IMAGE" --format '{{.Size}}' | awk '{printf "%.0f MB", $1/1e6}')"
echo "  user: $(docker image inspect "$IMAGE" --format '{{.Config.User}}')"
if docker run --rm "$IMAGE" sh -c 'test ! -e test_server.py'; then
    echo "  tests are not in the final image"
else
    echo "  FAIL: tests shipped in the image"; exit 1
fi

try_stop() {   # name, extra run arguments ...
    local name=$1; shift
    docker run -d --name "$name" --read-only --cap-drop=ALL -p 127.0.0.1::8080 "$@" >/dev/null || return 1
    local port; port=$(docker port "$name" 8080/tcp | sed 's/.*://')
    for _ in $(seq 1 50); do
        curl -fs "http://127.0.0.1:$port/readyz" >/dev/null && break
        sleep 0.1
    done
    local out; out=$(mktemp)
    curl -s -o "$out" -w '%{http_code}' --max-time 20 "http://127.0.0.1:$port/slow?ms=2000" >"$out.code" 2>/dev/null &
    local client=$!
    sleep 0.5
    local start; start=$(date +%s)
    docker stop -t 4 "$name" >/dev/null
    local took=$(( $(date +%s) - start ))
    wait "$client"
    local code; code=$(cat "$out.code")
    echo "  stop took ${took}s, exit code $(docker inspect "$name" --format '{{.State.ExitCode}}'), running request got HTTP ${code:-none}"
    rm -f "$out" "$out.code"
    docker rm -f "$name" >/dev/null
}

echo "== SIGTERM during a 2 s request, exec form (python is PID 1)"
try_stop backend-lab-graceful -e DRAIN_SECONDS=0.5 "$IMAGE"
echo "== the same, with a shell as PID 1 (grace period 4 s)"
try_stop backend-lab-shell "$IMAGE" sh -c 'python server.py; echo server exited'
echo "verify OK"
