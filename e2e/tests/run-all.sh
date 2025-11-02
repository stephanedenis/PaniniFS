#!/bin/bash
# Run all E2E tests (API + FUSE)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "======================================"
echo "Panini E2E Test Suite"
echo "======================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check if panini-api binary exists
if [ ! -f "$PROJECT_ROOT/target/release/panini-api" ]; then
    echo "Building panini-api..."
    cd "$PROJECT_ROOT"
    cargo build --release --package panini-api
fi

# Check if panini-mount (FUSE) binary exists
if [ ! -f "$PROJECT_ROOT/target/release/panini-mount" ]; then
    echo "Building panini-fuse..."
    cd "$PROJECT_ROOT"
    cargo build --release --package panini-fuse
fi

echo "✓ All binaries ready"
echo ""

# Start API server
echo "Starting API server..."
export PANINI_STORAGE="/tmp/panini-e2e-storage"
mkdir -p "$PANINI_STORAGE"

"$PROJECT_ROOT/target/release/panini-api" > /tmp/panini-api-e2e.log 2>&1 &
API_PID=$!
echo "API server started (PID: $API_PID)"

# Wait for API to be ready
sleep 3
if ! curl -s http://localhost:3030/health > /dev/null; then
    echo "ERROR: API server failed to start"
    cat /tmp/panini-api-e2e.log
    kill $API_PID 2>/dev/null || true
    exit 1
fi
echo "✓ API server ready"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up..."
    kill $API_PID 2>/dev/null || true
    rm -rf "$PANINI_STORAGE"
}
trap cleanup EXIT

# Run API tests
echo "======================================"
echo "Running API Integration Tests"
echo "======================================"
cd "$SCRIPT_DIR/.."
export API_URL="http://localhost:3030"

if npx playwright test tests/api.spec.js; then
    echo "✓ API tests passed"
else
    echo "✗ API tests failed"
    exit 1
fi

echo ""

# Run FUSE tests
echo "======================================"
echo "Running FUSE Integration Tests"
echo "======================================"
export FUSE_BIN="$PROJECT_ROOT/target/release/panini-mount"

if bash "$SCRIPT_DIR/fuse-integration.sh"; then
    echo "✓ FUSE tests passed"
else
    echo "✗ FUSE tests failed"
    exit 1
fi

echo ""
echo "======================================"
echo "✓ All E2E tests passed successfully!"
echo "======================================"
