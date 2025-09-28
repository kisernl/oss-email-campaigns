/**
 * Debug Campaign Status - Quick test of API endpoints
 */

const axios = require('axios');

const BACKEND_URL = 'http://localhost:8000';

async function debugCampaignStatus() {
    console.log('🔍 Campaign Status Debug Tool');
    console.log('==============================\n');
    
    try {
        // Test campaign list endpoint
        console.log('📋 Testing campaign list endpoint...');
        const listResponse = await axios.get(`${BACKEND_URL}/api/campaigns/`);
        const campaigns = listResponse.data;
        
        console.log(`Found ${campaigns.length} campaigns:\n`);
        
        for (const campaign of campaigns.slice(0, 5)) { // Show top 5
            console.log(`Campaign ID ${campaign.id}: "${campaign.name}"`);
            console.log(`  List Status: ${campaign.status}`);
            console.log(`  Emails: ${campaign.emails_sent}/${campaign.total_recipients}`);
            console.log(`  Success Rate: ${campaign.success_rate}%`);
            
            // Get detailed status
            try {
                const detailResponse = await axios.get(`${BACKEND_URL}/api/campaigns/${campaign.id}`);
                const detail = detailResponse.data;
                
                console.log(`  Detail Status: ${detail.status}`);
                console.log(`  Error Message: ${detail.error_message || 'None'}`);
                
                // Check for status mismatch
                if (campaign.status !== detail.status) {
                    console.log(`  ⚠️  STATUS MISMATCH! List: ${campaign.status}, Detail: ${detail.status}`);
                } else {
                    console.log(`  ✅ Status consistent`);
                }
                
            } catch (detailError) {
                console.log(`  ❌ Error getting details: ${detailError.message}`);
            }
            
            console.log('');
        }
        
        // Test with cache-busting
        console.log('🔄 Testing with cache-busting...');
        const cacheBustUrl = `${BACKEND_URL}/api/campaigns/?_t=${Date.now()}`;
        const cacheBustResponse = await axios.get(cacheBustUrl);
        
        if (JSON.stringify(cacheBustResponse.data) === JSON.stringify(campaigns)) {
            console.log('✅ Cache-busting returns same data (no caching issue)');
        } else {
            console.log('⚠️  Cache-busting returns different data (potential caching issue)');
        }
        
    } catch (error) {
        console.error('❌ Debug failed:', error.message);
    }
}

// Test specific campaign status transitions
async function testCampaignFlow() {
    console.log('\n🧪 Testing Campaign Status Flow');
    console.log('================================\n');
    
    try {
        // Create a test campaign
        const campaignData = {
            name: 'debug-status-test',
            description: 'Testing status transitions',
            subject: 'Debug Test {{name}}',
            message: 'Debug test message for {{name}} from {{company}}',
            google_sheet_id: '11LduXy_X23yGUPD7W4uWh8SdIcUzPUcWsvza-g9uBFw',
            google_sheet_range: 'A:Z',
            send_immediately: false
        };
        
        console.log('📝 Creating test campaign...');
        const createResponse = await axios.post(`${BACKEND_URL}/api/campaigns/`, campaignData);
        const campaign = createResponse.data;
        
        console.log(`✅ Campaign created: ID ${campaign.id}, Status: ${campaign.status}`);
        
        // Send the campaign
        console.log('📤 Sending campaign...');
        const sendResponse = await axios.post(`${BACKEND_URL}/api/campaigns/${campaign.id}/send`, {
            send_immediately: true,
            test_mode: true
        });
        
        console.log(`✅ Send initiated: ${sendResponse.data.message}`);
        
        // Monitor status changes
        for (let i = 0; i < 10; i++) {
            await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms
            
            const statusResponse = await axios.get(`${BACKEND_URL}/api/campaigns/${campaign.id}`);
            const currentStatus = statusResponse.data.status;
            
            console.log(`   Status check ${i + 1}: ${currentStatus} (${statusResponse.data.emails_sent}/${statusResponse.data.total_recipients} sent)`);
            
            if (currentStatus === 'completed' || currentStatus === 'failed') {
                console.log(`✅ Final status reached: ${currentStatus}`);
                if (statusResponse.data.error_message) {
                    console.log(`   Error: ${statusResponse.data.error_message}`);
                }
                break;
            }
        }
        
        // Clean up
        await axios.delete(`${BACKEND_URL}/api/campaigns/${campaign.id}`);
        console.log('🗑️  Test campaign cleaned up');
        
    } catch (error) {
        console.error('❌ Campaign flow test failed:', error.message);
    }
}

// Run debug
async function main() {
    await debugCampaignStatus();
    await testCampaignFlow();
    
    console.log('\n💡 RECOMMENDATIONS:');
    console.log('1. Check frontend for proper API calls');
    console.log('2. Verify CampaignList component refreshes after actions');
    console.log('3. Check browser network tab for API request timing');
    console.log('4. Clear browser cache if status mismatches persist');
}

main().catch(console.error);