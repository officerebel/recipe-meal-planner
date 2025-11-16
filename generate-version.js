#!/usr/bin/env node

const fs = require('fs');
const { execSync } = require('child_process');

// Get git commit hash
let commit = 'unknown';
try {
  commit = execSync('git rev-parse --short HEAD').toString().trim();
} catch (e) {
  console.log('Could not get git commit hash');
}

// Get git branch
let branch = 'unknown';
try {
  branch = execSync('git rev-parse --abbrev-ref HEAD').toString().trim();
} catch (e) {
  console.log('Could not get git branch');
}

// Get package version
const packageJson = JSON.parse(fs.readFileSync('./frontend/package.json', 'utf8'));
const version = packageJson.version || '1.0.0';

// Generate version file
const versionContent = `// Auto-generated version file - DO NOT EDIT
// Generated at build time

export const version = {
  version: '${version}',
  commit: '${commit}',
  branch: '${branch}',
  buildTime: '${new Date().toISOString()}',
  environment: process.env.NODE_ENV || 'production'
}

export default version
`;

fs.writeFileSync('./frontend/src/version.js', versionContent);
console.log(`✅ Version file generated: v${version} (${commit}) on ${branch}`);
