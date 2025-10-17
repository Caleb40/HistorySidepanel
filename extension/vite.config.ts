export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: 'src/sidepanel/main.tsx',
        background: 'src/background/background.ts',
        contentScript: 'src/content-script/contentScript.ts'
      },
      output: {
        entryFileNames: '[name].js'
      }
    }
  }
})