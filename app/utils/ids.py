import random
import string

def generate_public_id(prefix: str, length: int = 6) -> str:
    """
    Generates a random public ID with the given prefix.
    Example: generate_public_id('USR-') -> 'USR-X8A2M1'
    """
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choices(chars, k=length))
    return f"{prefix}{random_str}"
