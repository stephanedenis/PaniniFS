# Panini E2E Tests

End-to-end tests for the Panini filesystem project using Playwright.

## Setup

```bash
cd e2e
npm install
npx playwright install
```

## Running Tests

### All tests
```bash
npm test
```

### Specific test suite
```bash
npx playwright test tests/smoke.spec.js
npx playwright test tests/research.spec.js
npx playwright test tests/modules.spec.js
```

### With UI mode (debugging)
```bash
npm run test:ui
```

### Against custom URL
```bash
BASE_URL=http://localhost:3000 npm test
```

### Run local integration tests (API + FUSE)
```bash
./tests/run-all.sh
```

### Run only FUSE tests
```bash
./tests/fuse-integration.sh
```

### Run only API tests
```bash
# Start API server first
PANINI_STORAGE=/tmp/test cargo run --bin panini-api &

# Run tests
API_URL=http://localhost:3030 npx playwright test tests/api.spec.js
```

## Test Suites

### Live Site Tests (Playwright)

#### Smoke Tests (`smoke.spec.js`)
- Homepage loads successfully
- Navigation links are present
- Valid HTML response
- No console errors

#### Research Tests (`research.spec.js`)
- Research section accessibility
- Research pages return valid status codes
- Metadata validation

#### Modules Tests (`modules.spec.js`)
- Modules index accessibility
- Module listings structure
- Module navigation
- Proper metadata

### Local Integration Tests

#### API Tests (`api.spec.js`)
- Health and status endpoints
- Deduplication: upload, search, stats
- Dhātu emotional classification: classify, search, resonance, stats
- Error handling and validation

#### FUSE Tests (`fuse-integration.sh`)
- Mount filesystem successfully
- Directory structure (/concepts, /atoms, /index)
- Read atom files
- Unmount cleanly
- Remount capability

#### Complete Suite (`run-all.sh`)
- Builds all required binaries
- Starts API server
- Runs all API + FUSE tests
- Automatic cleanup

## CI Integration

Tests run automatically on:
- Push to master branch (if e2e files change)
- Scheduled hourly checks
- Manual workflow dispatch

## Notes

- Tests are designed to tolerate 404s during development
- Server errors (5xx) will fail the tests
- Tests run against live site by default (`https://paninifs.org`)
- Can be configured to run against local dev server
