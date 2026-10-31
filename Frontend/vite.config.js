import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8081',
        changeOrigin: true,
        configure: proxy => {
          proxy.on('proxyReq', proxyRequest => proxyRequest.removeHeader('origin'))
        },
      },
    },
  },
  // Prevent Vite from loading unrelated PostCSS/Tailwind configs
  // from parent folders (e.g. a postcss.config.mjs in Downloads).
  // This project uses plain CSS, not Tailwind CSS.
  css: {
    postcss: {
      plugins: [],
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
    // Resultados: test-reports/index.html (abrir con `npx vite preview --outDir test-reports`)
    reporters: ['default', 'html'],
    outputFile: { html: './test-reports/index.html' },
    // Cobertura: coverage/index.html
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/**/*.{js,jsx}'],
      exclude: ['src/main.jsx', 'src/test/**', 'src/**/*.test.{js,jsx}'],
    },
  },
})
