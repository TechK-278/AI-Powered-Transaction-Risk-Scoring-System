"""
Health check schema definitions.
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """
    Schema for the health check API response.
    """
    
    status: str
    service: str
    version: str
