# Configuration settings for the Flask app
class Config:
    JWT_SECRET_KEY = "secretkey"  # Replace with your actual JWT secret key
    CLIENTS = {"abcdefg": "1234567"}  # Replace with your actual client credentials
    SESSION_TYPE = "filesystem"  # Use file-based session management
    PERMANENT_SESSION_LIFETIME = 1800  # Session lifetime in seconds (30 minutes)

