import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/chat': 'http://localhost:8000',
      '/ai': 'http://localhost:8000',
      '/quiz': 'http://localhost:8000',
      '/resources': 'http://localhost:8000',
      '/question-bank': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    }
  }
})
