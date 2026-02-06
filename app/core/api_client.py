"""
API Client Module for AI Assistant Application

This module handles all HTTP communication with the backend AI API.
It provides:
- Synchronous and asynchronous API calls
- Error handling and retry logic
- Request/response logging
- Authentication header injection
- Timeout management

IMPORTANT: This is where all REST API calls are made.
Connect your AI backend endpoints here.
"""

import logging
import json
from typing import Optional, Dict, Any, Tuple
from enum import Enum

import requests
from requests.exceptions import (
    RequestException, 
    Timeout, 
    ConnectionError, 
    HTTPError
)

from app.core.config import Config


# Configure logging for this module
# All API calls and errors will be logged here
logger = logging.getLogger(__name__)


class APIStatus(Enum):
    """
    Enumeration of possible API response statuses.
    
    Used to communicate API state to the UI layer without
    exposing raw HTTP status codes.
    """
    SUCCESS = "success"  # Request succeeded
    ERROR = "error"  # Request failed
    TIMEOUT = "timeout"  # Request timed out
    CONNECTION_ERROR = "connection_error"  # Cannot connect to server
    INVALID_RESPONSE = "invalid_response"  # Server returned invalid data
    AUTHENTICATION_ERROR = "authentication_error"  # Auth failed (401/403)


class APIResponse:
    """
    Wrapper class for API responses.
    
    Provides a consistent interface for handling API responses
    regardless of success or failure.
    
    Attributes:
        status: APIStatus enum indicating result
        data: Response data (dict) if successful
        error: Error message if failed
        status_code: HTTP status code
    """
    
    def __init__(
        self,
        status: APIStatus,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        """
        Initialize API response object.
        
        Args:
            status: APIStatus enum value
            data: Response data dictionary (for successful requests)
            error: Error message string (for failed requests)
            status_code: HTTP status code from response
        """
        self.status = status
        self.data = data or {}
        self.error = error
        self.status_code = status_code
    
    def is_success(self) -> bool:
        """
        Check if the API call was successful.
        
        Returns:
            bool: True if status is SUCCESS, False otherwise
        """
        return self.status == APIStatus.SUCCESS
    
    def get_message(self) -> str:
        """
        Extract message from response data or error.
        
        Returns:
            str: Message from response or error description
        """
        if self.is_success():
            return self.data.get("message", "")
        return self.error or "Unknown error occurred"
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"APIResponse(status={self.status}, status_code={self.status_code})"


class APIClient:
    """
    HTTP client for communicating with AI backend APIs.
    
    This class handles all REST API communication including:
    - Making HTTP requests (GET, POST, etc.)
    - Adding authentication headers
    - Error handling and retries
    - Response parsing
    - Logging
    
    Usage:
        client = APIClient()
        response = client.send_chat_message("Hello AI!")
        if response.is_success():
            print(response.data)
    """
    
    def __init__(self):
        """
        Initialize the API client.
        
        Sets up the requests session with default headers
        and authentication.
        """
        # Create a requests session for connection pooling and persistent headers
        # This improves performance for multiple requests
        self.session = requests.Session()
        
        # Set default headers for all requests
        self.session.headers.update({
            "Content-Type": "application/json",  # We send JSON data
            "Accept": "application/json",  # We expect JSON responses
            "User-Agent": f"{Config.APP_NAME}/{Config.APP_VERSION}",
        })
        
        # Add authentication headers if API key is configured
        auth_headers = Config.get_auth_header()
        if auth_headers:
            self.session.headers.update(auth_headers)
        
        logger.info(f"APIClient initialized with base URL: {Config.API_BASE_URL}")
    
    def _make_request(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> APIResponse:
        """
        Internal method to make HTTP requests with error handling.
        
        This method handles all the low-level HTTP communication and
        converts exceptions into APIResponse objects.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Full URL to request
            data: JSON data to send in request body
            params: Query parameters to append to URL
            timeout: Request timeout in seconds
            
        Returns:
            APIResponse: Wrapped response with status and data
        """
        # Use configured timeout if not specified
        if timeout is None:
            timeout = Config.API_TIMEOUT
        
        # Log the request for debugging
        logger.debug(f"Making {method} request to {url}")
        if data:
            logger.debug(f"Request data: {json.dumps(data, indent=2)}")
        
        try:
            # Make the actual HTTP request
            # The session automatically adds our configured headers
            response = self.session.request(
                method=method,
                url=url,
                json=data,  # Automatically serializes dict to JSON
                params=params,
                timeout=timeout
            )
            
            # Log response status
            logger.debug(f"Response status code: {response.status_code}")
            
            # Check if request was successful (status code 2xx)
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
                
                return APIResponse(
                    status=APIStatus.SUCCESS,
                    data=response_data,
                    status_code=response.status_code
                )
            
            except json.JSONDecodeError as e:
                # Server returned non-JSON response
                logger.error(f"Invalid JSON response: {e}")
                return APIResponse(
                    status=APIStatus.INVALID_RESPONSE,
                    error="Server returned invalid JSON response",
                    status_code=response.status_code
                )
        
        except Timeout:
            # Request timed out
            logger.error(f"Request to {url} timed out after {timeout}s")
            return APIResponse(
                status=APIStatus.TIMEOUT,
                error=f"Request timed out after {timeout} seconds"
            )
        
        except ConnectionError as e:
            # Cannot connect to server (server down, network issue, etc.)
            logger.error(f"Connection error: {e}")
            return APIResponse(
                status=APIStatus.CONNECTION_ERROR,
                error="Cannot connect to server. Please check your connection."
            )
        
        except HTTPError as e:
            # HTTP error (4xx or 5xx status code)
            status_code = e.response.status_code
            logger.error(f"HTTP error {status_code}: {e}")
            
            # Handle authentication errors specifically
            if status_code in [401, 403]:
                return APIResponse(
                    status=APIStatus.AUTHENTICATION_ERROR,
                    error="Authentication failed. Please check your API key.",
                    status_code=status_code
                )
            
            # Try to extract error message from response
            try:
                error_data = e.response.json()
                error_message = error_data.get("error", str(e))
            except:
                error_message = str(e)
            
            return APIResponse(
                status=APIStatus.ERROR,
                error=error_message,
                status_code=status_code
            )
        
        except RequestException as e:
            # Generic request error
            logger.error(f"Request error: {e}")
            return APIResponse(
                status=APIStatus.ERROR,
                error=f"Request failed: {str(e)}"
            )
        
        except Exception as e:
            # Unexpected error
            logger.exception(f"Unexpected error: {e}")
            return APIResponse(
                status=APIStatus.ERROR,
                error=f"Unexpected error: {str(e)}"
            )
    
    def send_chat_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> APIResponse:
        """
        Send a chat message to the AI backend.
        
        ADD YOUR AI API INTEGRATION HERE
        
        This is the main method for sending user messages to your AI backend.
        Modify the request structure to match your API's expected format.
        
        Args:
            message: User's message text
            context: Optional context data (conversation history, user info, etc.)
            
        Returns:
            APIResponse: Response containing AI's reply or error
            
        Expected API request format (modify as needed):
        {
            "message": "user message here",
            "context": {...}
        }
        
        Expected API response format (modify as needed):
        {
            "reply": "AI response here",
            "conversation_id": "unique_id",
            "timestamp": "2026-02-03T10:30:00Z"
        }
        """
        # Get the full chat endpoint URL
        url = Config.get_full_chat_url()
        
        # Construct request payload
        # MODIFY THIS to match your backend API's expected format
        payload = {
            "message": message,
        }
        
        # Add context if provided
        if context:
            payload["context"] = context
        
        # For development/testing: Return dummy response if backend not available
        # REMOVE THIS when connecting to real backend
        if Config.DEBUG_MODE and "localhost" in Config.API_BASE_URL:
            logger.info("DEBUG MODE: Returning dummy response")
            return APIResponse(
                status=APIStatus.SUCCESS,
                data={
                    "reply": f"Echo: {message}\n\n[This is a dummy response. Connect your AI backend in api_client.py]",
                    "conversation_id": "dummy-123",
                    "timestamp": "2026-02-03T10:30:00Z"
                },
                status_code=200
            )
        
        # Make the actual API call
        return self._make_request(
            method="POST",
            url=url,
            data=payload
        )
    
    def check_health(self) -> APIResponse:
        """
        Check if the backend API is healthy and responsive.
        
        This is used to show connection status in the UI.
        
        Returns:
            APIResponse: Health status response
        """
        url = Config.get_full_health_url()
        
        # For development/testing: Return dummy response if backend not available
        if Config.DEBUG_MODE and "localhost" in Config.API_BASE_URL:
            logger.info("DEBUG MODE: Returning dummy health response")
            return APIResponse(
                status=APIStatus.SUCCESS,
                data={"status": "healthy", "message": "API is running (dummy)"},
                status_code=200
            )
        
        return self._make_request(
            method="GET",
            url=url,
            timeout=5  # Shorter timeout for health checks
        )
    
    def close(self):
        """
        Close the API client and clean up resources.
        
        Call this when the application is shutting down
        to properly close network connections.
        """
        self.session.close()
        logger.info("APIClient closed")


# ========== USAGE EXAMPLES ==========
"""
How to use the APIClient:

1. Basic usage:
   from app.core.api_client import APIClient
   
   client = APIClient()
   response = client.send_chat_message("Hello!")
   
   if response.is_success():
       ai_reply = response.data.get("reply")
       print(ai_reply)
   else:
       print(f"Error: {response.error}")

2. Check API health:
   response = client.check_health()
   if response.is_success():
       print("API is healthy")

3. Send message with context:
   context = {
       "user_id": "user123",
       "session_id": "session456"
   }
   response = client.send_chat_message("What's the weather?", context)

4. Handle different error types:
   response = client.send_chat_message("Hello")
   
   if response.status == APIStatus.TIMEOUT:
       print("Request timed out")
   elif response.status == APIStatus.CONNECTION_ERROR:
       print("Cannot connect to server")
   elif response.status == APIStatus.AUTHENTICATION_ERROR:
       print("Authentication failed")

5. Remember to close when done:
   client.close()
"""
