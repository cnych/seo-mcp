import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

# Test if we can import the modules
try:
    from seo_mcp.keywords import get_keyword_ideas
    print("✅ Successfully imported get_keyword_ideas")
except Exception as e:
    print(f"❌ Failed to import get_keyword_ideas: {e}")

# Test if we can get the API key
api_key = os.environ.get("CAPSOLVER_API_KEY")
if api_key:
    print(f"✅ API key found (length: {len(api_key)})")
else:
    print("❌ No API key found")

# Test if we can call the original function directly
if api_key:
    try:
        print("🔄 Testing original get_keyword_ideas function...")
        # This should work since the MCP server works
        site_url = "https://ahrefs.com/keyword-generator/?country=gb&input=test%20seo"
        
        # Let's use the original get_capsolver_token function from the MCP server
        from seo_mcp.server import get_capsolver_token
        token = get_capsolver_token(site_url)
        
        if token:
            print(f"✅ Got token: {token[:20]}...")
            result = get_keyword_ideas(token, "test seo", "gb", "Google")
            print(f"✅ Got results: {len(result) if result else 0} keywords")
        else:
            print("❌ Failed to get token")
            
    except Exception as e:
        print(f"❌ Error testing: {e}")