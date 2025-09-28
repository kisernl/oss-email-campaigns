/**
 * Frontend Validation Testing
 * Simulates form validation and API integration testing
 */

const axios = require('axios');

const BACKEND_URL = 'http://localhost:8000';
const TEST_SHEET_ID = '11LduXy_X23yGUPD7W4uWh8SdIcUzPUcWsvza-g9uBFw';

console.log('🧪 Frontend Validation Testing');
console.log('===============================\n');

async function testFormValidation() {
    console.log('📝 Testing Form Validation...');
    
    // Test 1: Empty form submission (should fail)
    try {
        const response = await axios.post(`${BACKEND_URL}/api/campaigns/`, {});
        console.log('   ❌ Empty form validation failed - request should have been rejected');
    } catch (error) {
        if (error.response && error.response.status === 422) {
            console.log('   ✅ Empty form correctly rejected with validation errors');
        } else {
            console.log('   ⚠️  Unexpected error:', error.message);
        }
    }
    
    // Test 2: Missing required fields
    try {
        const response = await axios.post(`${BACKEND_URL}/api/campaigns/`, {
            name: 'Test Campaign'
            // Missing subject, message, google_sheet_id
        });
        console.log('   ❌ Partial form validation failed - should require all fields');
    } catch (error) {
        if (error.response && error.response.status === 422) {
            console.log('   ✅ Partial form correctly rejected with validation errors');
        } else {
            console.log('   ⚠️  Unexpected error:', error.message);
        }
    }
    
    // Test 3: Invalid Google Sheet ID
    try {
        const response = await axios.post(`${BACKEND_URL}/api/campaigns/`, {
            name: 'Test Campaign',
            subject: 'Test Subject',
            message: 'Test Message',
            google_sheet_id: 'invalid-id'
        });
        console.log('   ❌ Invalid sheet ID validation failed');
    } catch (error) {
        if (error.response && error.response.status === 422) {
            console.log('   ✅ Invalid sheet ID correctly rejected');
        } else {
            console.log('   ⚠️  Unexpected error:', error.message);
        }
    }
}

async function testGoogleSheetPreview() {
    console.log('\n📋 Testing Google Sheet Preview...');
    
    try {
        const response = await axios.get(`${BACKEND_URL}/api/sheets/${TEST_SHEET_ID}/preview`);
        const data = response.data;
        
        console.log(`   ✅ Sheet preview successful:`);
        console.log(`      - Sheet name: ${data.sheet_name}`);
        console.log(`      - Total rows: ${data.total_rows}`);
        console.log(`      - Valid emails: ${data.valid_emails}`);
        console.log(`      - Headers: [${data.headers.join(', ')}]`);
        
        if (data.valid_emails > 0) {
            console.log('   ✅ Sheet contains valid email addresses');
        } else {
            console.log('   ⚠️  Sheet has no valid email addresses');
        }
        
        return true;
    } catch (error) {
        console.log('   ❌ Google Sheet preview failed:', error.message);
        return false;
    }
}

async function testCampaignCreation() {
    console.log('\n🚀 Testing Campaign Creation (End-to-End)...');
    
    const campaignData = {
        name: 'validation-test-campaign',
        description: 'Automated validation test',
        subject: 'Hello {{name}}, validation test',
        message: 'Hi {{name}},\n\nThis is a validation test.\n\nCompany: {{company}}\n\nBest regards,\nTest Suite',
        google_sheet_id: TEST_SHEET_ID,
        google_sheet_range: 'A:Z',
        send_immediately: false
    };
    
    try {
        // Create campaign
        const createResponse = await axios.post(`${BACKEND_URL}/api/campaigns/`, campaignData);
        const campaign = createResponse.data;
        
        console.log(`   ✅ Campaign created successfully (ID: ${campaign.id})`);
        console.log(`      - Name: ${campaign.name}`);
        console.log(`      - Status: ${campaign.status}`);
        console.log(`      - Recipients: ${campaign.total_recipients}`);
        
        // Test campaign retrieval
        const getResponse = await axios.get(`${BACKEND_URL}/api/campaigns/${campaign.id}`);
        console.log('   ✅ Campaign retrieval successful');
        
        // Test campaign in list
        const listResponse = await axios.get(`${BACKEND_URL}/api/campaigns/`);
        const foundCampaign = listResponse.data.find(c => c.id === campaign.id);
        if (foundCampaign) {
            console.log('   ✅ Campaign appears in campaign list');
        } else {
            console.log('   ❌ Campaign not found in campaign list');
        }
        
        // Test sending in test mode
        const sendResponse = await axios.post(`${BACKEND_URL}/api/campaigns/${campaign.id}/send`, {
            send_immediately: true,
            test_mode: true
        });
        console.log('   ✅ Campaign sending initiated successfully');
        
        // Wait a moment for background task to complete
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Check final status
        const finalResponse = await axios.get(`${BACKEND_URL}/api/campaigns/${campaign.id}`);
        const finalCampaign = finalResponse.data;
        
        console.log(`   ✅ Campaign final status: ${finalCampaign.status}`);
        console.log(`      - Emails sent: ${finalCampaign.emails_sent}`);
        console.log(`      - Success rate: ${finalCampaign.success_rate}%`);
        
        if (finalCampaign.status === 'completed' && finalCampaign.emails_sent > 0) {
            console.log('   ✅ End-to-end campaign flow successful');
        } else {
            console.log('   ⚠️  Campaign may not have completed properly');
        }
        
        // Check email records
        const emailsResponse = await axios.get(`${BACKEND_URL}/api/campaigns/${campaign.id}/emails`);
        const emails = emailsResponse.data;
        
        if (emails.length > 0) {
            console.log(`   ✅ Email records created (${emails.length} emails)`);
            console.log(`      - Sample personalized subject: "${emails[0].personalized_subject}"`);
            
            // Check template variable replacement
            if (emails[0].personalized_subject.includes('{{') || emails[0].personalized_message.includes('{{')) {
                console.log('   ⚠️  Template variables may not have been replaced');
            } else {
                console.log('   ✅ Template variables replaced correctly');
            }
        } else {
            console.log('   ❌ No email records created');
        }
        
        // Clean up
        await axios.delete(`${BACKEND_URL}/api/campaigns/${campaign.id}`);
        console.log('   ✅ Test campaign cleaned up');
        
        return true;
    } catch (error) {
        console.log('   ❌ Campaign creation failed:', error.message);
        return false;
    }
}

async function testApiService() {
    console.log('\n🔧 Testing API Service Integration...');
    
    try {
        // Test health endpoint
        const healthResponse = await axios.get(`${BACKEND_URL}/api/health`);
        if (healthResponse.data.status === 'healthy') {
            console.log('   ✅ Health check API working');
        } else {
            console.log('   ⚠️  Health check returned non-healthy status');
        }
        
        // Test campaigns endpoint
        const campaignsResponse = await axios.get(`${BACKEND_URL}/api/campaigns/`);
        console.log(`   ✅ Campaigns list API working (${campaignsResponse.data.length} campaigns)`);
        
        // Test API error handling
        try {
            await axios.get(`${BACKEND_URL}/api/campaigns/99999`);
            console.log('   ⚠️  Expected 404 error not thrown');
        } catch (notFoundError) {
            if (notFoundError.response && notFoundError.response.status === 404) {
                console.log('   ✅ 404 error handling working correctly');
            }
        }
        
        return true;
    } catch (error) {
        console.log('   ❌ API service integration failed:', error.message);
        return false;
    }
}

// Run all tests
async function runAllTests() {
    try {
        await testFormValidation();
        const sheetOk = await testGoogleSheetPreview();
        
        if (sheetOk) {
            await testCampaignCreation();
        } else {
            console.log('\n⚠️  Skipping campaign creation test due to sheet preview failure');
        }
        
        await testApiService();
        
        console.log('\n===============================');
        console.log('✅ Frontend Validation Testing Complete');
        console.log('===============================\n');
        
        console.log('📋 MANUAL BROWSER TESTING NEEDED:');
        console.log('1. Open http://localhost:3000');
        console.log('2. Navigate between all pages');
        console.log('3. Test form interactions');
        console.log('4. Verify responsive design');
        console.log('5. Test campaign grid layout');
        console.log('6. Verify status indicators and progress bars');
        
    } catch (error) {
        console.error('❌ Test runner failed:', error.message);
        process.exit(1);
    }
}

runAllTests();