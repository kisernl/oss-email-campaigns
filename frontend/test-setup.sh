#!/bin/bash

# Frontend Setup Test Script
# Tests that React + TypeScript + Tailwind are properly configured

set -e

echo "🧪 Testing Frontend Setup..."
echo ""

# Test TypeScript compilation
echo "1. Testing TypeScript compilation..."
npx tsc --noEmit
echo "✅ TypeScript compilation successful"
echo ""

# Test build process
echo "2. Testing build process..."
npm run build > /dev/null 2>&1
echo "✅ Build process successful"
echo ""

# Check required files
echo "3. Checking configuration files..."
[ -f "tailwind.config.js" ] && echo "✅ tailwind.config.js exists"
[ -f "postcss.config.js" ] && echo "✅ postcss.config.js exists"
[ -f "tsconfig.json" ] && echo "✅ tsconfig.json exists"
echo ""

# Check dependencies
echo "4. Checking installed dependencies..."
npm list --depth=0 | grep -q "tailwindcss" && echo "✅ Tailwind CSS installed"
npm list --depth=0 | grep -q "axios" && echo "✅ Axios installed"
npm list --depth=0 | grep -q "react-router-dom" && echo "✅ React Router installed"
npm list --depth=0 | grep -q "typescript" && echo "✅ TypeScript installed"
echo ""

echo "🎉 Frontend setup verification complete!"
echo ""
echo "To start development:"
echo "  npm start"
echo ""
echo "To build for production:"
echo "  npm run build"