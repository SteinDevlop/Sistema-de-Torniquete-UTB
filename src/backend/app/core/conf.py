from backend.app.core.auth import encode_token
"""
Create a test token for authentication in the test environment.
"""
test_token = encode_token({"sub": "001", "scope": "system"})
headers = {"Authorization": f"Bearer {test_token}"}