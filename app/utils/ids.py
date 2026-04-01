import random
import string

def generate_public_id(prefix: str, length: int = 6) -> str:

    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choices(chars, k=length))
    return f"{prefix}{random_str}"
