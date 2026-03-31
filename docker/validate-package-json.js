#!/usr/bin/env node
// Validate all package.json files in the current directory tree.
// Fails with exit code 1 if any file contains invalid JSON (e.g. merge conflict markers).
// Uses only built-in Node.js modules so it runs before npm install.

const fs = require('fs');
const path = require('path');

function findPackageJsonFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    if (entry.isDirectory() && entry.name !== 'node_modules') {
      return findPackageJsonFiles(path.join(dir, entry.name));
    }
    return entry.name === 'package.json' ? [path.join(dir, entry.name)] : [];
  });
}

const files = findPackageJsonFiles('.');
let allValid = true;

files.forEach((filePath) => {
  try {
    JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (e) {
    console.error(
      `ERROR: ${filePath} is invalid JSON. Check for merge conflict markers (<<<<<<< HEAD).`
    );
    allValid = false;
  }
});

if (!allValid) {
  process.exit(1);
}

console.log(`All ${files.length} package.json file(s) are valid JSON.`);
