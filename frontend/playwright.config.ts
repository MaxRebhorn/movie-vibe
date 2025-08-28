import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',       // folder with tests
  timeout: 30 * 1000,       // max test time
  retries: 0,               // retry failed tests
  use: {
    headless: true,         // run in headless mode by default
    viewport: { width: 1280, height: 720 },
    actionTimeout: 5000,
    ignoreHTTPSErrors: true,
    video: 'retain-on-failure', // record video on failure
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
