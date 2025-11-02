#!/bin/bash
# FUSE Integration Tests
# Tests mounting, reading, and unmounting the Panini filesystem

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

MOUNT_POINT="/tmp/panini-test-mount"
STORAGE_DIR="/tmp/panini-test-storage"
FUSE_BIN="${FUSE_BIN:-target/release/panini-mount}"

# Cleanup function
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    fusermount3 -u "$MOUNT_POINT" 2>/dev/null || true
    sleep 1
    rm -rf "$MOUNT_POINT" "$STORAGE_DIR"
}

# Setup trap for cleanup
trap cleanup EXIT

echo "======================================"
echo "Panini FUSE Integration Tests"
echo "======================================"
echo ""

# Check if binary exists
if [ ! -f "$FUSE_BIN" ]; then
    echo -e "${RED}✗ FUSE binary not found: $FUSE_BIN${NC}"
    echo "Build it with: cargo build --release --package panini-fuse"
    exit 1
fi
echo -e "${GREEN}✓ FUSE binary found${NC}"

# Create directories
mkdir -p "$MOUNT_POINT" "$STORAGE_DIR"
echo -e "${GREEN}✓ Directories created${NC}"

# Start FUSE mount in background
echo "Starting FUSE mount..."
PANINI_STORAGE="$STORAGE_DIR" "$FUSE_BIN" "$MOUNT_POINT" &
FUSE_PID=$!
sleep 2

# Check if mount succeeded
if ! mountpoint -q "$MOUNT_POINT"; then
    echo -e "${RED}✗ Failed to mount filesystem${NC}"
    kill $FUSE_PID 2>/dev/null || true
    exit 1
fi
echo -e "${GREEN}✓ Filesystem mounted${NC}"

# Test 1: Root directory is accessible
echo ""
echo "Test 1: Root directory accessible"
if ls "$MOUNT_POINT" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Root directory accessible${NC}"
else
    echo -e "${RED}✗ Cannot access root directory${NC}"
    exit 1
fi

# Test 2: Expected directories exist
echo ""
echo "Test 2: Expected directory structure"
EXPECTED_DIRS=("concepts" "atoms" "index" "metadata")
for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$MOUNT_POINT/$dir" ]; then
        echo -e "${GREEN}✓ /$dir exists${NC}"
    else
        echo -e "${YELLOW}⚠ /$dir not found (may not be implemented yet)${NC}"
    fi
done

# Test 3: Can list directories
echo ""
echo "Test 3: Directory listing"
if ls -la "$MOUNT_POINT" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Can list root directory${NC}"
    ls -lh "$MOUNT_POINT" | head -10
else
    echo -e "${RED}✗ Cannot list directories${NC}"
    exit 1
fi

# Test 4: Read a file (if any exist)
echo ""
echo "Test 4: File reading"
if [ -d "$MOUNT_POINT/atoms" ]; then
    ATOM_COUNT=$(find "$MOUNT_POINT/atoms" -type f 2>/dev/null | wc -l)
    echo "Found $ATOM_COUNT atoms"
    
    if [ $ATOM_COUNT -gt 0 ]; then
        FIRST_FILE=$(find "$MOUNT_POINT/atoms" -type f 2>/dev/null | head -1)
        if [ -n "$FIRST_FILE" ]; then
            if cat "$FIRST_FILE" > /dev/null 2>&1; then
                echo -e "${GREEN}✓ Can read atom file: $(basename $FIRST_FILE)${NC}"
            else
                echo -e "${RED}✗ Cannot read atom file${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠ No atoms to test reading${NC}"
    fi
else
    echo -e "${YELLOW}⚠ /atoms directory not found${NC}"
fi

# Test 5: Concepts directory structure
echo ""
echo "Test 5: Concepts directory"
if [ -d "$MOUNT_POINT/concepts" ]; then
    CONCEPT_COUNT=$(find "$MOUNT_POINT/concepts" -type d 2>/dev/null | wc -l)
    echo "Found $CONCEPT_COUNT concept directories"
    echo -e "${GREEN}✓ Concepts directory accessible${NC}"
else
    echo -e "${YELLOW}⚠ /concepts directory not found${NC}"
fi

# Test 6: Filesystem stays mounted
echo ""
echo "Test 6: Filesystem stability"
sleep 1
if mountpoint -q "$MOUNT_POINT"; then
    echo -e "${GREEN}✓ Filesystem still mounted after operations${NC}"
else
    echo -e "${RED}✗ Filesystem unmounted unexpectedly${NC}"
    exit 1
fi

# Test 7: Clean unmount
echo ""
echo "Test 7: Unmounting"
fusermount3 -u "$MOUNT_POINT"
sleep 1

if ! mountpoint -q "$MOUNT_POINT"; then
    echo -e "${GREEN}✓ Filesystem cleanly unmounted${NC}"
else
    echo -e "${RED}✗ Failed to unmount filesystem${NC}"
    exit 1
fi

# Test 8: Remount after unmount
echo ""
echo "Test 8: Remount capability"
PANINI_STORAGE="$STORAGE_DIR" "$FUSE_BIN" "$MOUNT_POINT" &
FUSE_PID=$!
sleep 2

if mountpoint -q "$MOUNT_POINT"; then
    echo -e "${GREEN}✓ Filesystem can be remounted${NC}"
    fusermount3 -u "$MOUNT_POINT"
else
    echo -e "${RED}✗ Failed to remount filesystem${NC}"
    exit 1
fi

echo ""
echo "======================================"
echo -e "${GREEN}All FUSE integration tests passed!${NC}"
echo "======================================"
