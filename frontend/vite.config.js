import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/entity-types': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/export-list': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
