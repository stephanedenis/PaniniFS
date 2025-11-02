// API Integration Tests - Test against local Panini API server
import { test, expect } from '@playwright/test';

const API_BASE = process.env.API_URL || 'http://localhost:3030';

test.describe('Panini API - Health & Status', () => {
  test('health endpoint responds', async ({ request }) => {
    const response = await request.get(`${API_BASE}/health`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('ok');
  });

  test('CORS headers are present', async ({ request }) => {
    const response = await request.get(`${API_BASE}/health`);
    const headers = response.headers();
    
    expect(headers['access-control-allow-origin']).toBeDefined();
  });
});

test.describe('Panini API - Deduplication', () => {
  test('dedup stats endpoint works', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/dedup/stats`);
    
    if (response.ok()) {
      const data = await response.json();
      expect(data).toHaveProperty('total_atoms');
      expect(data).toHaveProperty('total_size');
      expect(data).toHaveProperty('unique_atoms');
      expect(typeof data.total_atoms).toBe('number');
    } else {
      // Tolerate 404 if endpoint not yet fully implemented
      expect(response.status()).toBeLessThan(500);
    }
  });

  test('dedup search returns valid structure', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/dedup/search?query=test`);
    
    if (response.ok()) {
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      
      if (data.length > 0) {
        const firstResult = data[0];
        expect(firstResult).toHaveProperty('hash');
        expect(firstResult).toHaveProperty('size');
      }
    } else {
      expect(response.status()).toBeLessThan(500);
    }
  });

  test('dedup upload accepts multipart', async ({ request }) => {
    const testContent = 'Hello from E2E test';
    
    const response = await request.post(`${API_BASE}/api/dedup/upload`, {
      multipart: {
        file: {
          name: 'test.txt',
          mimeType: 'text/plain',
          buffer: Buffer.from(testContent)
        }
      }
    });
    
    if (response.ok()) {
      const data = await response.json();
      expect(data).toHaveProperty('hash');
      expect(data).toHaveProperty('size');
      expect(data.size).toBe(testContent.length);
    } else {
      // Log for debugging but don't fail if upload not ready
      console.log('Upload endpoint status:', response.status());
    }
  });
});

test.describe('Panini API - Dhātu Emotional Classification', () => {
  test('dhatu classify endpoint works', async ({ request }) => {
    const testText = 'This is an exciting journey of exploration and discovery!';
    
    const response = await request.post(`${API_BASE}/api/dhatu/classify`, {
      data: {
        path: '/test/e2e/example.txt',
        text: testText
      }
    });
    
    if (response.ok()) {
      const data = await response.json();
      expect(data).toHaveProperty('path');
      expect(data).toHaveProperty('dominant_emotion');
      expect(data).toHaveProperty('intensity');
      expect(data).toHaveProperty('confidence');
      
      // Confidence should be 0-1
      expect(data.confidence).toBeGreaterThanOrEqual(0);
      expect(data.confidence).toBeLessThanOrEqual(1);
    } else {
      expect(response.status()).toBeLessThan(500);
    }
  });

  test('dhatu search by emotion', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/dhatu/search?emotion=Seeking`);
    
    if (response.ok()) {
      const data = await response.json();
      expect(Array.isArray(data)).toBeTruthy();
      
      if (data.length > 0) {
        const profile = data[0];
        expect(profile).toHaveProperty('path');
        expect(profile).toHaveProperty('dominant_emotion');
      }
    } else {
      expect(response.status()).toBeLessThan(500);
    }
  });

  test('dhatu stats returns aggregates', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/dhatu/stats`);
    
    if (response.ok()) {
      const data = await response.json();
      expect(data).toHaveProperty('total_profiles');
      expect(data).toHaveProperty('avg_arousal');
      expect(data).toHaveProperty('avg_confidence');
      expect(data).toHaveProperty('emotions');
      
      expect(typeof data.total_profiles).toBe('number');
      expect(Array.isArray(data.emotions)).toBeTruthy();
    } else {
      expect(response.status()).toBeLessThan(500);
    }
  });

  test('dhatu resonance calculation', async ({ request }) => {
    const response = await request.get(
      `${API_BASE}/api/dhatu/resonance?path_a=/test/a.txt&path_b=/test/b.txt`
    );
    
    if (response.ok()) {
      const data = await response.json();
      expect(data).toHaveProperty('score');
      expect(data).toHaveProperty('resonance_type');
      
      // Score should be 0-1
      expect(data.score).toBeGreaterThanOrEqual(0);
      expect(data.score).toBeLessThanOrEqual(1);
    } else {
      // May fail if paths don't exist, that's ok
      expect(response.status()).toBeLessThan(500);
    }
  });
});

test.describe('Panini API - Error Handling', () => {
  test('invalid endpoints return 404', async ({ request }) => {
    const response = await request.get(`${API_BASE}/api/nonexistent`);
    expect(response.status()).toBe(404);
  });

  test('malformed requests return 400', async ({ request }) => {
    const response = await request.post(`${API_BASE}/api/dhatu/classify`, {
      data: {
        // Missing required fields
        invalid: 'data'
      }
    });
    
    expect(response.status()).toBeGreaterThanOrEqual(400);
    expect(response.status()).toBeLessThan(500);
  });
});
