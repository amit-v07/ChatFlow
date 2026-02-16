#!/usr/bin/env python3
"""
Test script for ChatApp JWT Authentication API

Tests all authentication endpoints:
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh
- GET  /api/auth/me
"""

import requests
import json
from typing import Dict, Optional

BASE_URL = "http://localhost:8000"
headers = {"Content-Type": "application/json"}


def print_section(title: str):
    """Pretty print section headers."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_response(response: requests.Response):
    """Pretty print API response."""
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_health_check():
    """Test health check endpoint."""
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    return response.status_code == 200


def test_register(email: str, password: str) -> bool:
    """Test user registration."""
    print_section(f"2. Register User: {email}")
    
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        headers=headers,
        json=data
    )
    print_response(response)
    return response.status_code == 201


def test_login(email: str, password: str) -> Optional[Dict[str, str]]:
    """Test user login and return tokens."""
    print_section(f"3. Login User: {email}")
    
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        headers=headers,
        json=data
    )
    print_response(response)
    
    if response.status_code == 200:
        return response.json()
    return None


def test_get_current_user(access_token: str):
    """Test getting current user info with access token."""
    print_section("4. Get Current User (/me)")
    
    auth_headers = {
        **headers,
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=auth_headers
    )
    print_response(response)
    return response.status_code == 200


def test_refresh_token(refresh_token: str) -> Optional[Dict[str, str]]:
    """Test token refresh."""
    print_section("5. Refresh Access Token")
    
    params = {"refresh_token": refresh_token}
    
    response = requests.post(
        f"{BASE_URL}/api/auth/refresh",
        headers=headers,
        params=params
    )
    print_response(response)
    
    if response.status_code == 200:
        return response.json()
    return None


def test_unauthorized_access():
    """Test accessing protected route without token."""
    print_section("6. Test Unauthorized Access (No Token)")
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )
    print_response(response)
    return response.status_code == 401


def test_invalid_token():
    """Test accessing protected route with invalid token."""
    print_section("7. Test Invalid Token")
    
    auth_headers = {
        **headers,
        "Authorization": "Bearer invalid_token_here"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=auth_headers
    )
    print_response(response)
    return response.status_code == 401


def test_duplicate_registration(email: str, password: str):
    """Test registering with an already existing email."""
    print_section(f"8. Test Duplicate Registration: {email}")
    
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        headers=headers,
        json=data
    )
    print_response(response)
    return response.status_code == 400


def run_all_tests():
    """Run all authentication tests."""
    print("\n" + "=" * 60)
    print("  ChatApp JWT Authentication Test Suite")
    print("=" * 60)
    
    test_email = "testuser@example.com"
    test_password = "SecurePassword123!"
    
    results = []
    
    # 1. Health check
    results.append(("Health Check", test_health_check()))
    
    # 2. Register new user
    results.append(("Register User", test_register(test_email, test_password)))
    
    # 3. Login and get tokens
    tokens = test_login(test_email, test_password)
    results.append(("Login User", tokens is not None))
    
    if tokens:
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        
        # 4. Get current user info
        results.append(("Get Current User", test_get_current_user(access_token)))
        
        # 5. Refresh token
        new_tokens = test_refresh_token(refresh_token)
        results.append(("Refresh Token", new_tokens is not None))
    
    # 6. Test unauthorized access
    results.append(("Unauthorized Access", test_unauthorized_access()))
    
    # 7. Test invalid token
    results.append(("Invalid Token", test_invalid_token()))
    
    # 8. Test duplicate registration
    results.append(("Duplicate Registration", test_duplicate_registration(test_email, test_password)))
    
    # Print summary
    print_section("Test Results Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} | {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server.")
        print("Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
