import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8000',
      '/tasks': 'http://localhost:8000',
      '/users': 'http://localhost:8000',
      '/ai': 'http://localhost:8000',
      '/stats': 'http://localhost:8000',
      '/metrics': 'http://localhost:8000',
    }
  }
})
