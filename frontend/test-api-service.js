/**
 * API Service Test Script
 * Tests the TypeScript API service with running backend
 */

const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Simple test functions to verify API connectivity
async function testHealth() {
  try {
    const response = await axios.get(`${BASE_URL}/api/health`);
    console.log('✅ Health check:', response.data.status);
    return true;
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
    return false;
  }
}

async function testCampaigns() {
  try {
    const response = await axios.get(`${BASE_URL}/api/campaigns/`);
    console.log(`✅ Campaigns list: ${response.data.length} campaigns found`);
    return true;
  } catch (error) {
    console.error('❌ Campaigns list failed:', error.message);
    return false;
  }
}

async function testCreateCampaign() {
  try {
    const campaignData = {
      name: 'API Test Campaign',
      description: 'Test campaign created via API service',
      subject: 'Test Subject',
      message: 'Hello {{name}}, this is a test message.',
      google_sheet_id: '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
      google_sheet_range: 'A:Z',
      send_immediately: false
    };
    
    const response = await axios.post(`${BASE_URL}/api/campaigns/`, campaignData);
    console.log(`✅ Campaign created: ID ${response.data.id}`);
    return response.data.id;
  } catch (error) {
    console.error('❌ Campaign creation failed:', error.response?.data || error.message);
    return null;
  }
}

async function testGoogleSheets() {
  try {
    const response = await axios.post(`${BASE_URL}/api/sheets/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/validate`);
    console.log('✅ Google Sheets validation:', response.data.message);
    return true;
  } catch (error) {
    console.error('❌ Google Sheets validation failed:', error.message);
    return false;
  }
}

async function runTests() {
  console.log('🧪 Testing API Service Layer...\n');
  
  const healthOk = await testHealth();
  if (!healthOk) {
    console.log('\n❌ Backend not available. Please start the backend first.');
    return;
  }
  
  await testCampaigns();
  const campaignId = await testCreateCampaign();
  await testGoogleSheets();
  
  if (campaignId) {
    try {
      await axios.delete(`${BASE_URL}/api/campaigns/${campaignId}`);
      console.log('✅ Test campaign cleaned up');
    } catch (error) {
      console.log('⚠️  Failed to clean up test campaign');
    }
  }
  
  console.log('\n🎉 API Service tests completed!');
}

runTests().catch(console.error);