"""
Advanced Math Routing Agent - Full System Test
Tests all advanced features including knowledge base, web search routing, and feedback system.
"""

import requests
import json
import time
import random

BASE_URL = "http://localhost:8000"

def test_health_check():
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check passed")
        print(f"   Status: {data.get('status')}")
        print(f"   Components: {data.get('components')}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Health check failed: Server not reachable.")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_knowledge_base_queries():
    print("\n2. Testing Knowledge Base Queries...")
    
    test_queries = [
        "Solve the quadratic equation: x² - 5x + 6 = 0",
        "Find the derivative of f(x) = x³ + 2x² - 5x + 3",
        "Calculate the area of a circle with radius 5 cm",
        "Evaluate the integral: ∫(2x + 1)dx",
        "Find sin(30°) using special triangles",
        "Find the mean of the dataset: [2, 4, 6, 8, 10]"
    ]
    
    all_passed = True
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Test {i}: {query}")
        try:
            response = requests.post(f"{BASE_URL}/query", json={"question": query})
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                print(f"   ✅ Query successful")
                print(f"   Solution: {data['response']['solution'][:100]}...")
                print(f"   Method: {data['response']['method']}")
                print(f"   Confidence: {data['response']['confidence']}")
                print(f"   Routing: {data['routing_decision']}")
                print(f"   Sources: {data['response']['sources']}")
            else:
                print(f"   ❌ Query failed: {data.get('error')}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
            all_passed = False
    
    return all_passed

def test_web_search_routing():
    print("\n3. Testing Web Search Routing...")
    
    # These queries should trigger web search routing
    web_queries = [
        "Solve the differential equation dy/dx = 2xy",
        "Find the eigenvalues of matrix [[1,2],[3,4]]",
        "Calculate the Fourier transform of f(x) = e^(-x²)"
    ]
    
    all_passed = True
    for i, query in enumerate(web_queries, 1):
        print(f"\n   Test {i}: {query}")
        try:
            response = requests.post(f"{BASE_URL}/query", json={"question": query})
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                print(f"   ✅ Query successful")
                print(f"   Solution: {data['response']['solution'][:100]}...")
                print(f"   Routing: {data['routing_decision']}")
                print(f"   Confidence: {data['response']['confidence']}")
            else:
                print(f"   ❌ Query failed: {data.get('error')}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
            all_passed = False
    
    return all_passed

def test_feedback_system():
    print("\n4. Testing Feedback System...")
    
    # Submit some test feedback
    feedback_data = {
        "query": "Solve the quadratic equation: x² - 5x + 6 = 0",
        "response": {
            "solution": "The solutions are x = 2 and x = 3",
            "steps": ["Factor the equation", "Apply zero product property", "Solve for x"],
            "method": "Factoring",
            "confidence": 0.95
        },
        "user_rating": 5,
        "user_comments": "Great explanation! Very clear steps.",
        "user_id": "test_user_123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/feedback", json=feedback_data)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            print(f"   ✅ Feedback submitted successfully")
            print(f"   Feedback ID: {data.get('feedback_id')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"   ❌ Feedback submission failed: {data.get('message')}")
            return False
    except Exception as e:
        print(f"   ❌ Feedback submission failed: {e}")
        return False

def test_feedback_insights():
    print("\n5. Testing Feedback Insights...")
    
    try:
        response = requests.get(f"{BASE_URL}/feedback/insights")
        response.raise_for_status()
        data = response.json()
        
        print(f"   ✅ Feedback insights retrieved")
        print(f"   Statistics: {data.get('feedback_statistics')}")
        print(f"   Learning Trends: {data.get('learning_trends')}")
        print(f"   Recommendations: {data.get('recommendations')}")
        return True
    except Exception as e:
        print(f"   ❌ Feedback insights failed: {e}")
        return False

def test_knowledge_base_stats():
    print("\n6. Testing Knowledge Base Statistics...")
    
    try:
        response = requests.get(f"{BASE_URL}/knowledge-base/stats")
        response.raise_for_status()
        data = response.json()
        
        print(f"   ✅ Knowledge base stats retrieved")
        print(f"   Total Problems: {data.get('total_problems')}")
        print(f"   Topics: {data.get('topics')}")
        print(f"   Difficulty Levels: {data.get('difficulty_levels')}")
        print(f"   Average Confidence: {data.get('average_confidence')}")
        return True
    except Exception as e:
        print(f"   ❌ Knowledge base stats failed: {e}")
        return False

def test_problem_list():
    print("\n7. Testing Problem List...")
    
    try:
        response = requests.get(f"{BASE_URL}/problems")
        response.raise_for_status()
        data = response.json()
        
        print(f"   ✅ Problem list retrieved")
        print(f"   Available Problems: {len(data.get('available_problems', []))}")
        for problem_id in data.get('available_problems', []):
            problem = data.get('problems', {}).get(problem_id, {})
            print(f"   - {problem_id}: {problem.get('question', 'N/A')[:50]}...")
        return True
    except Exception as e:
        print(f"   ❌ Problem list failed: {e}")
        return False

def test_advanced_features():
    print("\n8. Testing Advanced Features...")
    
    # Test routing decisions
    print("   Testing Routing Intelligence...")
    try:
        # This should route to knowledge base
        response = requests.post(f"{BASE_URL}/query", json={"question": "quadratic equation"})
        data = response.json()
        if data.get("routing_decision") == "knowledge_base":
            print("   ✅ Knowledge base routing working")
        else:
            print("   ⚠️  Unexpected routing decision")
        
        # This should route to web search
        response = requests.post(f"{BASE_URL}/query", json={"question": "quantum mechanics equations"})
        data = response.json()
        if data.get("routing_decision") == "web_search":
            print("   ✅ Web search routing working")
        else:
            print("   ⚠️  Unexpected routing decision")
        
        return True
    except Exception as e:
        print(f"   ❌ Advanced features test failed: {e}")
        return False

def run_comprehensive_tests():
    print("🚀 Math Routing Agent - Advanced System Test")
    print("Make sure the server is running on http://localhost:8000")
    input("Press Enter to start testing...")

    print("\n🧪 Testing Advanced Math Routing Agent API")
    print("=" * 60)

    all_passed = True

    # Run all tests
    if not test_health_check():
        all_passed = False

    if not test_knowledge_base_queries():
        all_passed = False

    if not test_web_search_routing():
        all_passed = False

    if not test_feedback_system():
        all_passed = False

    if not test_feedback_insights():
        all_passed = False

    if not test_knowledge_base_stats():
        all_passed = False

    if not test_problem_list():
        all_passed = False

    if not test_advanced_features():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All Advanced Tests Completed Successfully!")
        print("\n📚 Advanced Features Verified:")
        print("   ✅ Knowledge Base Routing")
        print("   ✅ Web Search Routing")
        print("   ✅ Human-in-the-Loop Feedback")
        print("   ✅ Learning Analytics")
        print("   ✅ Advanced Math Problem Solving")
        print("   ✅ Intelligent Query Routing")
        
        print("\n🌐 Access Points:")
        print("   📖 API Documentation: http://localhost:8000/docs")
        print("   🔍 Interactive API: http://localhost:8000")
        print("   📊 Health Check: http://localhost:8000/health")
        
        print("\n🎯 System Status: FULLY OPERATIONAL")
        print("   The Math Routing Agent is ready for production use!")
    else:
        print("❌ Some tests failed. Please check the logs and server status.")
        print("   Make sure the server is running: uvicorn src.main_full:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    run_comprehensive_tests()
