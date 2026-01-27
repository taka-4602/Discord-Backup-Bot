"""
Simple test to verify Flask routes work correctly
"""
import sys
import os

# Add the v8 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock the v8path module before importing ninFlaskV8
class MockV8Path:
    BOTTOKEN = "test_token"
    CLIENT_ID = "test_client_id"
    CLIENT_SECRET = "test_client_secret"
    REDIRECT_URI = "http://localhost:5000/"

sys.modules['v8path'] = MockV8Path()

# Mock asyncEAGM module
class MockEAGM:
    def __init__(self, bot_token=None, client_id=None, client_secret=None, redirect_uri=None):
        pass

class MockEAGMError(Exception):
    pass

sys.modules['asyncEAGM'] = type('module', (), {
    'EAGM': MockEAGM,
    'EAGMError': MockEAGMError
})()

# Now import the Flask app
from ninFlaskV8 import app

# Create a test client
client = app.test_client()

def test_index_page():
    """Test the index/landing page loads"""
    response = client.get('/')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert b'Discord Backup Bot' in response.data, "Landing page should contain 'Discord Backup Bot'"
    print("✓ Index page loads successfully")

def test_setup_page():
    """Test the setup page loads"""
    response = client.get('/setup')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.data.decode('utf-8')
    assert 'setup' in data.lower() or 'セットアップ' in data
    print("✓ Setup page loads successfully")

def test_faq_page():
    """Test the FAQ page loads"""
    response = client.get('/faq')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.data.decode('utf-8')
    assert 'faq' in data.lower() or 'よくある質問' in data
    print("✓ FAQ page loads successfully")

def test_pricing_page():
    """Test the pricing page loads"""
    response = client.get('/pricing')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.data.decode('utf-8')
    assert 'pricing' in data.lower() or '料金' in data
    print("✓ Pricing page loads successfully")

def test_navigation_links():
    """Test that navigation includes all required links"""
    response = client.get('/')
    data = response.data.decode('utf-8')
    assert 'setup' in data.lower() or 'セットアップ' in data
    assert 'faq' in data.lower() or 'よくある質問' in data
    assert 'pricing' in data.lower() or '料金' in data
    print("✓ Navigation links are present")

def test_ad_integration():
    """Test that ExoClick ad script is present"""
    response = client.get('/')
    data = response.data.decode('utf-8')
    # Check for ExoClick ad script
    assert 'magsrv.com' in data or 'ad-provider.js' in data or 'ad-container' in data
    print("✓ Ad integration is present")

if __name__ == '__main__':
    print("Running Flask route tests...\n")
    try:
        test_index_page()
        test_setup_page()
        test_faq_page()
        test_pricing_page()
        test_navigation_links()
        test_ad_integration()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
