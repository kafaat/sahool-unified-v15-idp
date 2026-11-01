import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../../../', import.meta.url));
const webRequire = createRequire(path.join(root, 'apps/web/package.json'));
const maplibreRoot = path.dirname(webRequire.resolve('maplibre-gl/package.json'));

export default defineConfig({
  root: fileURLToPath(new URL('.', import.meta.url)),
  plugins: [react()],
  // Preserve the ESM worker URL relative to MapLibre's distributed module.
  optimizeDeps: { exclude: ['maplibre-gl'] },
  define: { 'process.env.NEXT_PUBLIC_SENTRY_DSN': 'undefined' },
  resolve: {
    dedupe: ['react', 'react-dom'],
    alias: [
      { find: /^@\/lib\/api$/, replacement: fileURLToPath(new URL('./api.ts', import.meta.url)) },
      { find: /^maplibre-gl$/, replacement: path.join(maplibreRoot, 'dist/maplibre-gl.mjs') },
      { find: 'maplibre-gl/dist', replacement: path.join(maplibreRoot, 'dist') },
      { find: '@', replacement: path.join(root, 'apps/web/src') },
    ],
  },
  server: { host: '127.0.0.1', port: 4178, strictPort: true, fs: { allow: [root] } },
});
