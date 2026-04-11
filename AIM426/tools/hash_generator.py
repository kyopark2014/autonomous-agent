from strands import tool
import hashlib

@tool
def generate_hash(text: str, hash_type: str = "md5") -> str:
    """Generate hash of input text using various algorithms.
    
    Args:
        text: Text to hash
        hash_type: Hash algorithm ('md5', 'sha1', 'sha256', 'sha512')
        
    Returns:
        str: Generated hash result
    """
    text_bytes = text.encode('utf-8')
    
    hash_functions = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    if hash_type.lower() not in hash_functions:
        available = list(hash_functions.keys())
        return f"Error: Hash type must be one of {available}"
    
    hash_func = hash_functions[hash_type.lower()]
    hash_result = hash_func(text_bytes).hexdigest()
    
    return f"Text: {text}\nHash Type: {hash_type.upper()}\nHash: {hash_result}\nLength: {len(hash_result)} characters"
