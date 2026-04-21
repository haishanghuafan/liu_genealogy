"""
Analytics middleware for tracking page visits
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Middleware to track page visits for analytics"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Process the request first
        response = await call_next(request)
        
        # Note: Page visits are now tracked via frontend API calls
        # This middleware is kept for potential future server-side tracking
        
        return response
