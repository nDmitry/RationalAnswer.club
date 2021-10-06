import os

PUBLIC_CONTENT = os.getenv("PUBLIC_CONTENT") == 'true' or False
EMAIL_SIGN_UP = os.getenv("EMAIL_SIGN_UP") == 'true' or False
FREE_MEMBERSHIP = os.getenv("FREE_MEMBERSHIP") == 'true' or False
