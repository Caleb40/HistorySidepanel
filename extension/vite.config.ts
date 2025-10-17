import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/sidepanel/main.tsx'),
        background: resolve(__dirname, 'src/background/background.ts'),
        contentScript: resolve(__dirname, 'src/content-script/contentScript.ts')
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]'
      },
      external: ['react', 'react-dom'] // Externalize React to reduce bundle size
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  define: {
    'process.env.NODE_ENV': '"production"'
  }
});