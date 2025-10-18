import {execSync} from 'child_process';
import {copyFileSync, existsSync} from 'fs';

function buildWithVite() {
    console.log('🔨 Building with Vite...');

    // Build all three entry points separately
    console.log('📦 Building sidepanel...');
    execSync('npx vite build', {stdio: 'inherit'});

    console.log('🔧 Building background script...');
    execSync('BUILD_TARGET=background npx vite build', {stdio: 'inherit'});

    console.log('📝 Building content script...');
    execSync('BUILD_TARGET=contentScript npx vite build', {stdio: 'inherit'});

    copyStaticFiles();
}

function buildWithBun() {
    console.log('🔨 Building with Bun...');

    const builds = [
        {input: './src/sidepanel/main.tsx', output: './dist/main.js'},
        {input: './src/background/background.ts', output: './dist/background.js'},
        {input: './src/content-script/contentScript.ts', output: './dist/contentScript.js'}
    ];

    builds.forEach(({input, output}) => {
        execSync(`bun build ${input} --outfile ${output} --target browser --minify`, {stdio: 'inherit'});
    });

    copyStaticFiles();
}

function copyStaticFiles() {
    // Copy static files
    if (existsSync('./public/manifest.json')) {
        copyFileSync('./public/manifest.json', './dist/manifest.json');
        console.log('📄 Copied manifest.json');
    }
    if (existsSync('./public/sidepanel.html')) {
        copyFileSync('./public/sidepanel.html', './dist/sidepanel.html');
        console.log('📄 Copied sidepanel.html');
    }
    if (existsSync('./src/sidepanel/styles.css')) {
        copyFileSync('./src/sidepanel/styles.css', './dist/main.css');
        console.log('🎨 Copied styles.css');
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