"""HTTP client for inter-service communication."""

import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class ServiceClient:
    """HTTP client for calling other microservices."""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Initialize service client.
        
        Args:
            base_url: Base URL of the service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make GET request to service.
        
        Args:
            path: API endpoint path
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            HTTPException: If request fails
        """
        url = f"{self.base_url}{path}"
        try:
            logger.info(f"GET {url} with params {params}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {url}: {e}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Service error: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error calling {url}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(e)}"
            )
    
    async def post(self, path: str, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make POST request to service.
        
        Args:
            path: API endpoint path
            json_data: JSON request body
            
        Returns:
            Response JSON data
            
        Raises:
            HTTPException: If request fails
        """
        url = f"{self.base_url}{path}"
        try:
            logger.info(f"POST {url} with data {json_data}")
            response = await self.client.post(url, json=json_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {url}: {e}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Service error: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error calling {url}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(e)}"
            )
    
    async def put(self, path: str, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make PUT request to service.
        
        Args:
            path: API endpoint path
            json_data: JSON request body
            
        Returns:
            Response JSON data
            
        Raises:
            HTTPException: If request fails
        """
        url = f"{self.base_url}{path}"
        try:
            logger.info(f"PUT {url} with data {json_data}")
            response = await self.client.put(url, json=json_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {url}: {e}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Service error: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error calling {url}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(e)}"
            )
    
    async def delete(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Make DELETE request to service.
        
        Args:
            path: API endpoint path
            
        Returns:
            Response JSON data if any
            
        Raises:
            HTTPException: If request fails
        """
        url = f"{self.base_url}{path}"
        try:
            logger.info(f"DELETE {url}")
            response = await self.client.delete(url)
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {url}: {e}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Service error: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error calling {url}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: {str(e)}"
            )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
