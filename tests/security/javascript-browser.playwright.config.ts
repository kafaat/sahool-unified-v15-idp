import { defineConfig } from '@playwright/test';
import path from 'node:path';

const evidenceDirectory = path.resolve(__dirname, '../../test-results');

export default defineConfig({
  testDir: './browser',
  testMatch: '*.spec.ts',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30_000,
  // Playwright clears outputDir before a run; keep other scanner/test reports.
  outputDir: path.join(evidenceDirectory, 'browser-artifacts'),
  reporter: [['list'], ['junit', { outputFile: path.join(evidenceDirectory, 'javascript-security-browser.xml') }]],
  use: {
    baseURL: 'http://127.0.0.1:4178',
    viewport: { width: 1000, height: 700 },
    trace: 'retain-on-failure',
    launchOptions: {
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined,
      args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
    },
  },
  webServer: {
    command: 'node node_modules/vite/bin/vite.js --config tests/security/browser/vite.config.mts',
    cwd: '../..',
    url: 'http://127.0.0.1:4178',
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
