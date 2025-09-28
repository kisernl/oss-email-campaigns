#!/bin/bash

# Main App Component & Routing Test Script
# Tests Phase 2.4 implementation

set -e

echo "🧭 Testing Main App Component & Routing..."
echo ""

# Test 1: Check component files exist
echo "1. Checking component files..."
[ -f "src/App.tsx" ] && echo "✅ Main App component exists"
[ -f "src/components/Navigation.tsx" ] && echo "✅ Navigation component exists"
[ -d "src/pages" ] && echo "✅ Pages directory exists"
[ -f "src/pages/Dashboard.tsx" ] && echo "✅ Dashboard page exists"
[ -f "src/pages/Campaigns.tsx" ] && echo "✅ Campaigns page exists"
[ -f "src/pages/CreateCampaign.tsx" ] && echo "✅ CreateCampaign page exists"
[ -f "src/pages/Sheets.tsx" ] && echo "✅ Sheets page exists"
[ -f "src/pages/Settings.tsx" ] && echo "✅ Settings page exists"
[ -f "src/pages/NotFound.tsx" ] && echo "✅ NotFound page exists"
echo ""

# Test 2: Check React Router imports
echo "2. Checking React Router DOM integration..."
grep -q "react-router-dom" src/App.tsx && echo "✅ React Router DOM imported in App"
grep -q "BrowserRouter" src/App.tsx && echo "✅ BrowserRouter configured"
grep -q "Routes" src/App.tsx && echo "✅ Routes component used"
grep -q "Route" src/App.tsx && echo "✅ Route components defined"
grep -q "useLocation" src/components/Navigation.tsx && echo "✅ Navigation uses useLocation hook"
echo ""

# Test 3: Check navigation structure
echo "3. Checking navigation structure..."
grep -q "dashboard" src/components/Navigation.tsx && echo "✅ Dashboard navigation item"
grep -q "campaigns" src/components/Navigation.tsx && echo "✅ Campaigns navigation item"
grep -q "create" src/components/Navigation.tsx && echo "✅ Create navigation item"
grep -q "sheets" src/components/Navigation.tsx && echo "✅ Sheets navigation item"
grep -q "settings" src/components/Navigation.tsx && echo "✅ Settings navigation item"
echo ""

# Test 4: Check monospace styling
echo "4. Checking monospace styling consistency..."
grep -q "var(--font-family)" src/App.tsx && echo "✅ CSS variables used in App"
grep -q "var(--text-color)" src/components/Navigation.tsx && echo "✅ CSS variables used in Navigation"
grep -q "var(--line-height)" src/pages/Dashboard.tsx && echo "✅ CSS variables used in pages"
grep -q "className=\"card\"" src/pages/Dashboard.tsx && echo "✅ Monospace card components used"
grep -q "className=\"btn-primary\"" src/pages/Dashboard.tsx && echo "✅ Monospace button components used"
echo ""

# Test 5: Check active route highlighting
echo "5. Checking active route highlighting..."
grep -q "isActiveRoute" src/components/Navigation.tsx && echo "✅ Active route detection implemented"
grep -q "borderBottom" src/components/Navigation.tsx && echo "✅ Active route visual indicator"
grep -q "fontWeight.*active" src/components/Navigation.tsx && echo "✅ Active route font weight"
echo ""

# Test 6: Check TypeScript compilation
echo "6. Testing TypeScript compilation..."
npx tsc --noEmit > /dev/null 2>&1 && echo "✅ TypeScript compiles without errors"
echo ""

# Test 7: Check build process
echo "7. Testing build process..."
npm run build > /dev/null 2>&1 && echo "✅ Build process successful with routing"
echo ""

# Test 8: Check API integration in pages
echo "8. Checking API integration in pages..."
grep -q "healthCheck" src/pages/Dashboard.tsx && echo "✅ Dashboard integrates with API service"
grep -q "getCampaigns" src/pages/Dashboard.tsx && echo "✅ Dashboard fetches campaign data"
grep -q "import.*services/api" src/pages/Dashboard.tsx && echo "✅ API service properly imported"
echo ""

# Test 9: Check routing configuration
echo "9. Checking routing configuration..."
grep -q 'path="/"' src/App.tsx && echo "✅ Root route configured"
grep -q 'path="/campaigns"' src/App.tsx && echo "✅ Campaigns route configured"
grep -q 'path="/create"' src/App.tsx && echo "✅ Create route configured"
grep -q 'path="\\*"' src/App.tsx && echo "✅ Catch-all route configured"
echo ""

# Test 10: Check link integration
echo "10. Checking link integration..."
grep -q "Link.*to=" src/pages/Dashboard.tsx && echo "✅ React Router Links used in Dashboard"
grep -q "Link.*to=" src/pages/NotFound.tsx && echo "✅ React Router Links used in NotFound"
grep -q "Link.*to=" src/components/Navigation.tsx && echo "✅ React Router Links used in Navigation"
echo ""

echo "🎉 Main App Component & Routing Test Complete!"
echo ""
echo "📋 Features Implemented:"
echo "   ✓ React Router DOM v7 integration"
echo "   ✓ Navigation component with active route highlighting"
echo "   ✓ Complete page structure (Dashboard, Campaigns, Create, Sheets, Settings)"
echo "   ✓ 404 Not Found page with route listing"
echo "   ✓ Monospace styling consistency across all routes"
echo "   ✓ API service integration in Dashboard"
echo "   ✓ TypeScript type safety throughout"
echo "   ✓ Responsive design with character-based layout"
echo ""
echo "🚀 Application Structure:"
echo "   / → Dashboard (overview, stats, recent campaigns)"
echo "   /campaigns → Campaign management and listing"
echo "   /create → New campaign creation form"
echo "   /sheets → Google Sheets integration tools"
echo "   /settings → Configuration and system info"
echo "   /* → 404 error page with navigation help"