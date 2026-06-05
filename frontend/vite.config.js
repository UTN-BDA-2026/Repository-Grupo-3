import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      'react': path.resolve(__dirname, 'node_modules/react'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom'),
    }
  },
  server: {
    proxy: {
      '/api': {
        // Apuntamos a localhost (donde está Traefik) y forzamos el Host header
        target: 'http://localhost:80',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});