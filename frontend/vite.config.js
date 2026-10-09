/**
 * Configuración de Vite (servidor de desarrollo y compilación) y de Vitest (pruebas).
 *
 * En desarrollo, las solicitudes a /api se redirigen al backend de Flask
 * (puerto 5000). Así el navegador ve un único origen y no hace falta
 * configurar CORS, igual que en producción, donde Nginx cumple ese rol (ADR-0002).
 */
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5000',
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/pruebas/configuracion.js',
    coverage: {
      provider: 'v8',
      include: ['src/**/*.{js,jsx}'],
      exclude: ['src/main.jsx', 'src/pruebas/**'],
    },
  },
})
