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
})
