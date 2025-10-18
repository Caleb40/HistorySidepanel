import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import {resolve} from 'path';

const buildTarget = process.env.BUILD_TARGET;
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    emptyOutDir: buildTarget === 'main',
    rollupOptions: {
      // @ts-ignore
      input: getInput(),
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]',
        format: 'iife'
      }
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

function getInput() {
  switch (buildTarget) {
    case 'background':
      return {background: resolve(__dirname, 'src/background/background.ts')};
    case 'contentScript':
      return {contentScript: resolve(__dirname, 'src/content-script/contentScript.ts')};
    default:
      return {main: resolve(__dirname, 'src/sidepanel/main.tsx')};
  }
}