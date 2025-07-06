# config.py

class Config:
    # General Flask configurations
    SECRET_KEY = 'your_secret_key_here'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:rootuser@localhost:5432/ecommercedb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Other settings (e.g., email configurations, Stripe API keys, etc.)
    STRIPE_API_KEY = 'your_stripe_api_key_here'
