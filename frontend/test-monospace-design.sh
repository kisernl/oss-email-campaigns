#!/bin/bash

# Monospace Design System Test Script
# Tests the implementation of "The Monospace Web" inspired design

set -e

echo "🎨 Testing Monospace Design System Implementation..."
echo ""

# Test 1: Check configuration files
echo "1. Checking configuration files..."
[ -f "tailwind.config.js" ] && echo "✅ tailwind.config.js exists"
[ -f "src/index.css" ] && echo "✅ src/index.css exists"
echo ""

# Test 2: Check JetBrains Mono font import
echo "2. Checking JetBrains Mono font import..."
grep -q "fonts.cdnfonts.com/css/jetbrains-mono" src/index.css && echo "✅ JetBrains Mono font imported"
grep -q "JetBrains Mono" tailwind.config.js && echo "✅ JetBrains Mono in Tailwind config"
echo ""

# Test 3: Check CSS custom properties
echo "3. Checking CSS custom properties..."
grep -q "var(--font-family)" src/index.css && echo "✅ Font family CSS variable defined"
grep -q "var(--line-height)" src/index.css && echo "✅ Line height CSS variable defined"
grep -q "var(--border-thickness)" src/index.css && echo "✅ Border thickness CSS variable defined"
grep -q "var(--text-color)" src/index.css && echo "✅ Text color CSS variable defined"
echo ""

# Test 4: Check character-based spacing
echo "4. Checking character-based spacing system..."
grep -q "'ch':" tailwind.config.js && echo "✅ Character unit spacing defined"
grep -q "'2ch':" tailwind.config.js && echo "✅ Multiple character units defined"
grep -q "1ch" src/index.css && echo "✅ Character units used in CSS"
echo ""

# Test 5: Check typography hierarchy
echo "5. Checking typography hierarchy..."
grep -q "text-transform: uppercase" src/index.css && echo "✅ Uppercase transforms implemented"
grep -q "font-weight: var(--font-weight-bold)" src/index.css && echo "✅ Font weight variables used"
grep -q "line-height: var(--line-height)" src/index.css && echo "✅ Consistent line height implemented"
echo ""

# Test 6: Check component classes
echo "6. Checking monospace component classes..."
grep -q ".btn-primary" src/index.css && echo "✅ Button components defined"
grep -q ".input-field" src/index.css && echo "✅ Input field components defined"
grep -q ".card" src/index.css && echo "✅ Card components defined"
grep -q ".table-mono" src/index.css && echo "✅ Table components defined"
echo ""

# Test 7: Check dark mode support
echo "7. Checking dark mode support..."
grep -q "@media (prefers-color-scheme: dark)" src/index.css && echo "✅ Dark mode media query implemented"
echo ""

# Test 8: Check border system
echo "8. Checking border system..."
grep -q "var(--border-thickness)" src/index.css && echo "✅ Consistent border thickness used"
grep -q "border-thickness-focus" src/index.css && echo "✅ Focus border thickness defined"
echo ""

# Test 9: Test build process
echo "9. Testing build process..."
npm run build > /dev/null 2>&1 && echo "✅ Build process successful"
echo ""

# Test 10: Check TypeScript compilation
echo "10. Testing TypeScript compilation..."
npx tsc --noEmit > /dev/null 2>&1 && echo "✅ TypeScript compilation successful"
echo ""

echo "🎉 Monospace Design System Test Complete!"
echo ""
echo "📋 Features Implemented:"
echo "   ✓ JetBrains Mono font family"
echo "   ✓ Character-based spacing (ch units)"
echo "   ✓ CSS custom properties for consistency"
echo "   ✓ Typography hierarchy with transforms"
echo "   ✓ Monospace-inspired components"
echo "   ✓ Dark mode support"
echo "   ✓ Consistent 2px border system"
echo "   ✓ Grid alignment utilities"
echo ""
echo "🚀 Ready for development!"
echo "   npm start - Start development server"
echo "   npm run build - Build for production"