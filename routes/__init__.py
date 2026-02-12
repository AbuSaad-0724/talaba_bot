# Routes package
from routes.admin_routes import router as admin_routes
from routes.library_routes import router as library_routes

__all__ = ["admin_routes", "library_routes"]
