#!/bin/bash
echo "Building Quasar frontend..."
npm ci
npm run build
echo "Build complete!"