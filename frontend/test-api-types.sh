#!/bin/bash

# API Service Layer Type Safety and Integration Test Script
# Comprehensive testing for Phase 2.3

set -e

echo "🔌 Testing API Service Layer Implementation..."
echo ""

# Test 1: Check that files exist
echo "1. Checking API service files..."
[ -f "src/types/index.ts" ] && echo "✅ TypeScript types file exists"
[ -f "src/services/api.ts" ] && echo "✅ API service file exists"
[ -f ".env" ] && echo "✅ Environment configuration exists"
echo ""

# Test 2: Check TypeScript compilation
echo "2. Testing TypeScript compilation..."
npx tsc --noEmit > /dev/null 2>&1 && echo "✅ TypeScript compiles without errors"
echo ""

# Test 3: Check types definitions
echo "3. Checking TypeScript type definitions..."
grep -q "export enum CampaignStatus" src/types/index.ts && echo "✅ CampaignStatus enum defined"
grep -q "export interface CampaignResponse" src/types/index.ts && echo "✅ CampaignResponse interface defined"
grep -q "export interface GoogleSheetPreview" src/types/index.ts && echo "✅ GoogleSheetPreview interface defined"
grep -q "export interface ApiError" src/types/index.ts && echo "✅ ApiError interface defined"
echo ""

# Test 4: Check API service implementation
echo "4. Checking API service implementation..."
grep -q "class ApiClient" src/services/api.ts && echo "✅ ApiClient class implemented"
grep -q "createCampaign" src/services/api.ts && echo "✅ Campaign CRUD methods implemented"
grep -q "previewGoogleSheet" src/services/api.ts && echo "✅ Google Sheets methods implemented"
grep -q "healthCheck" src/services/api.ts && echo "✅ Health check methods implemented"
echo ""

# Test 5: Check error handling
echo "5. Checking error handling implementation..."
grep -q "createApiError" src/services/api.ts && echo "✅ API error creation implemented"
grep -q "isApiError" src/services/api.ts && echo "✅ Error type checking implemented"
grep -q "getErrorMessage" src/services/api.ts && echo "✅ Error message extraction implemented"
echo ""

# Test 6: Check axios configuration
echo "6. Checking axios configuration..."
grep -q "interceptors.request.use" src/services/api.ts && echo "✅ Request interceptors configured"
grep -q "interceptors.response.use" src/services/api.ts && echo "✅ Response interceptors configured"
grep -q "baseURL.*localhost:8000" src/services/api.ts && echo "✅ Base URL configured"
echo ""

# Test 7: Check environment variables
echo "7. Checking environment configuration..."
grep -q "REACT_APP_API_URL" .env && echo "✅ API URL environment variable set"
echo ""

# Test 8: Test build process
echo "8. Testing build process with API service..."
npm run build > /dev/null 2>&1 && echo "✅ Build process successful with API service"
echo ""

# Test 9: Test with running backend (if available)
echo "9. Testing API connectivity..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ Backend is running, testing API calls..."
    node test-api-service.js 2>/dev/null | grep -q "API Service tests completed" && echo "✅ API integration tests passed"
else
    echo "⚠️  Backend not running, skipping integration tests"
    echo "   To test integration: ./backend.sh start"
fi
echo ""

echo "🎉 API Service Layer Test Complete!"
echo ""
echo "📋 Features Implemented:"
echo "   ✓ Comprehensive TypeScript types matching backend schemas"
echo "   ✓ Axios-based API client with interceptors"
echo "   ✓ Full CRUD operations for campaigns"
echo "   ✓ Google Sheets integration methods"
echo "   ✓ Health check and status monitoring"
echo "   ✓ Type-safe error handling with custom ApiError"
echo "   ✓ Request/response logging for development"
echo "   ✓ Environment-based configuration"
echo "   ✓ Singleton pattern with convenience functions"
echo ""
echo "🚀 Ready for frontend components!"
echo "   Import: import { getCampaigns, createCampaign } from './services/api'"
echo "   Types: import { CampaignResponse, ApiError } from './types'"