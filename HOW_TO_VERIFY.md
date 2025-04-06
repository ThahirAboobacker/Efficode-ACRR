# How to Verify the System

This guide will help you verify that the entire Efficode-ACRR system is working correctly.

## Backend Status

The backend server should be running on port 5500. You can verify this by:

1. Opening a browser and navigating to `http://localhost:5500/health`
2. You should see a message: `{"message":"Server is running","status":"ok"}`

## Frontend Status

The frontend application should be running on port 3000. To access it:

1. Open a browser and navigate to `http://localhost:3000`
2. You should see the main application interface

## Testing the API Connection

To verify that the frontend can connect to the backend API:

1. Navigate to `http://localhost:3000/test-api`
2. This will open the API Test Component that directly tests the connection
3. The component will automatically check the health endpoint and show the status
4. Click "Test Optimization" to send a test request to the backend
5. You should see the optimized code returned from the backend

## Testing the Main Application

After verifying the connection works:

1. Go back to the main application at `http://localhost:3000`
2. Enter a simple Python function like:
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```
3. Click "Optimize Code"
4. You should see the optimized code and performance metrics

## Troubleshooting

If you encounter issues:

1. Ensure both servers are running (backend on port 5500, frontend on port 3000)
2. Check the browser console for any error messages (F12 in most browsers)
3. Verify that there are no CORS or Content-Security-Policy issues
4. Try the standalone test files in `frontend/test_connection.html` or `frontend/check_api.js` 