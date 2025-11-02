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

## Test Suites

### Smoke Tests (`smoke.spec.js`)
- Homepage loads successfully
- Navigation links are present
- Valid HTML response
- No console errors

### Research Tests (`research.spec.js`)
- Research section accessibility
- Research pages return valid status codes
- Metadata validation

### Modules Tests (`modules.spec.js`)
- Modules index accessibility
- Module listings structure
- Module navigation
- Proper metadata

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
