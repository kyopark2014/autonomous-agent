from strands import tool
import hashlib

@tool
def shorten_url(url: str, custom_alias: str = None) -> str:
    """Create a shortened version of a URL.
    
    Args:
        url: The URL to shorten
        custom_alias: Optional custom alias for the short URL
        
    Returns:
        str: Shortened URL result
    """
    if custom_alias:
        short_code = custom_alias
    else:
        # Generate a short code from URL hash
        hash_object = hashlib.md5(url.encode())
        short_code = hash_object.hexdigest()[:6]
    
    short_url = f"https://short.ly/{short_code}"
    return f"Original: {url}\nShortened: {short_url}\nAlias: {short_code}"
