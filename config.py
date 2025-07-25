import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConfig:
    """Database configuration loaded from environment variables"""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "6379"))
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = int(os.getenv("DB_DATABASE", "0"))
    
    def get_connection_kwargs(self) -> dict:
        """Get Redis connection parameters"""
        kwargs = {
            "host": self.host,
            "port": self.port,
            "db": self.database,
            "decode_responses": True,
        }
        
        if self.password:
            kwargs["password"] = self.password
            
        return kwargs

# Global configuration instance
config = DatabaseConfig()
