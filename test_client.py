#!/usr/bin/env python3
"""
Test client for bb-agent-manager
Tests all endpoints and functionality
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"🏥 Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False

def test_tools():
    """Test tool discovery"""
    try:
        response = requests.get(f"{BASE_URL}/agent/mcp/tools", timeout=10)
        print(f"🔧 Tools Discovery: {response.status_code}")
        if response.status_code == 200:
            tools = response.json()
            print(f"   Found {len(tools.get('tools', []))} tools:")
            for tool in tools.get('tools', []):
                print(f"     • {tool['name']}: {tool['description']}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_devdocs_tool():
    """Test devdocs tool directly"""
    payload = {
        "name": "update_devdocs",
        "arguments": {
            "files": ["src/test_file.py", "tests/test_example.py"],
            "summary": "Added test functionality with comprehensive error handling",
            "component_reuse_notes": "Error handling patterns and test utilities can be reused across projects"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/agent/mcp/invoke", json=payload, timeout=15)
        print(f"📚 DevDocs Tool: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_git_tool():
    """Test git operations tool"""
    payload = {
        "name": "create_pr",
        "arguments": {
            "title": "Test PR from bb-agent-manager",
            "body": "This is a test PR created by the bb-agent-manager test client"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/agent/mcp/invoke", json=payload, timeout=10)
        print(f"🔀 Git Tool: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_labs_tool():
    """Test Labs integration tool (requires API token)"""
    payload = {
        "name": "labs_upsert_task",
        "arguments": {
            "product_uuid": "test-product-uuid",
            "title": "Test task from bb-agent-manager",
            "description": "This is a test task created by the bb-agent-manager test client",
            "pr_url": "https://github.com/Buildly-Labs/bb-agent-manager/pull/1",
            "labels": ["test", "automation", "bb-agent"]
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/agent/mcp/invoke", json=payload, timeout=15)
        print(f"🏢 Labs Tool: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def test_chat():
    """Test the chat endpoint with tool usage"""
    payload = {
        "provider": "gemini",
        "messages": [
            {
                "role": "system",
                "content": "You are the Buildly Agent. Use available tools to help with development tasks. When asked to document changes, use the update_devdocs tool."
            },
            {
                "role": "user",
                "content": "I just implemented a new authentication system. Please document this change and note that the auth middleware can be reused in other projects."
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/agent/chat", json=payload, timeout=30)
        print(f"💬 Chat Endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Response: {result.get('content', 'No content')[:200]}...")
            return True
        else:
            print(f"   ❌ Failed: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 BB Agent Manager Test Suite")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    for i in range(5):
        if test_health():
            break
        if i < 4:
            print(f"   Retrying in 2 seconds... ({i+1}/5)")
            time.sleep(2)
        else:
            print("❌ Server not responding. Make sure test_server.py is running.")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Run tests
    tests = [
        ("Tool Discovery", test_tools),
        ("DevDocs Tool", test_devdocs_tool),
        ("Git Tool", test_git_tool),
        ("Labs Tool", test_labs_tool),
        ("Chat with Tools", test_chat),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"   💥 Exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check configuration and try again.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
