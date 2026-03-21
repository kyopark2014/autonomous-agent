from strands import tool
import random
import string

@tool
def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    """Generate a secure random password.
    
    Args:
        length: Password length (default: 12)
        include_symbols: Include special symbols (default: True)
        
    Returns:
        str: Generated password
    """
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*"
    
    password = ''.join(random.choice(chars) for _ in range(length))
    return f"Generated password: {password}"
