// CORS and API Integration Test
// Run this in browser console: copy and paste into console at http://localhost:5175

const API_BASE_URL = 'http://localhost:5000';

async function testCORS() {
    console.log('🧪 Starting CORS Tests...\n');

    // Test 1: OPTIONS preflight
    console.log('Test 1: OPTIONS Preflight');
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'OPTIONS',
        });
        console.log('✓ OPTIONS Status:', response.status);
        console.log('CORS Headers:', {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        });
    } catch (error) {
        console.error('✗ OPTIONS Error:', error.message);
    }

    console.log('\n---\n');

    // Test 2: Signup
    console.log('Test 2: Signup Endpoint');
    try {
        const randomNum = Math.floor(Math.random() * 10000);
        const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: `testuser${randomNum}`,
                email: `test${randomNum}@test.com`,
                password: 'test123',
                phone: '1234567890'
            })
        });
        const data = await response.json();
        console.log('✓ Signup Status:', response.status);
        console.log('Response:', data);
        
        if (data.token) {
            window.testAuthToken = data.token;
            console.log('✓ Token saved to window.testAuthToken');
        }
    } catch (error) {
        console.error('✗ Signup Error:', error.message);
    }

    console.log('\n---\n');

    // Test 3: Protected endpoint
    if (window.testAuthToken) {
        console.log('Test 3: Protected Endpoint (Active Cycle)');
        try {
            const response = await fetch(`${API_BASE_URL}/api/rindm/active-cycle`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${window.testAuthToken}`
                }
            });
            const data = await response.json();
            console.log('✓ Active Cycle Status:', response.status);
            console.log('Response:', data);
        } catch (error) {
            console.error('✗ Active Cycle Error:', error.message);
        }
    } else {
        console.log('Test 3: Skipped (no auth token)');
    }

    console.log('\n✅ Tests complete!');
}

// Run tests
testCORS();
