import re
def generate_email(creator_name: str) -> str:
    """Generate email from creatorName like JS code"""
    if not creator_name:
        return None
    name = creator_name.lower()
    # Keep only a-z and 0-9
    name = re.sub(r'[^a-z0-9]', '', name)
    return f"{name}@yopmail.com"