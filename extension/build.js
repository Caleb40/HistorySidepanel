import { execSync } from 'child_process';
import { existsSync, copyFileSync } from 'fs';

function buildWithVite() {
  console.log('🔨 Building with Vite...');
  execSync('npx vite build', { stdio: 'inherit' });
}

function buildWithBun() {
  console.log('🔨 Building with Bun...');

  const builds = [
    { input: './src/sidepanel/main.tsx', output: './dist/main.js' },
    { input: './src/background/background.ts', output: './dist/background.js' },
    { input: './src/content-script/contentScript.ts', output: './dist/contentScript.js' }
  ];

  builds.forEach(({ input, output }) => {
    execSync(`bun build ${input} --outfile ${output} --target browser --minify`, { stdio: 'inherit' });
  });

  // Copy static files
  if (existsSync('./public/manifest.json')) {
    copyFileSync('./public/manifest.json', './dist/manifest.json');
  }
  if (existsSync('./public/sidepanel.html')) {
    copyFileSync('./public/sidepanel.html', './dist/sidepanel.html');
  }
  if (existsSync('./src/sidepanel/styles.css')) {
    copyFileSync('./src/sidepanel/styles.css', './dist/main.css');
  }
}

// Detect available package manager
const hasBun = !!process.versions.bun;
const hasNpm = !!process.env.npm_execpath;

if (hasBun) {
  buildWithBun();
} else if (hasNpm) {
  buildWithVite();
} else {
  console.log('⚠️  No package manager detected. Trying Vite...');
  buildWithVite();
}