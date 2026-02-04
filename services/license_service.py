import hashlib
import json
import os
import uuid
from pathlib import Path
import dotenv
from services.state import resource_path


dotenv.load_dotenv(resource_path(".env"))



LICENSE_SECRET = os.getenv("LICENSE_SECRET")


def get_machine_id():
    """Returns a MAC Address based machine identifier."""
    return str(uuid.getnode())

def get_license_file_path():
    """Returns the path to the hidden license file."""
    # Save in the user's home directory to persist across updates
    base = Path.home() / "Documents" / "AttainmentSoftware"
    base.mkdir(parents=True, exist_ok=True)
    return base / ".license"

def generate_key_hash(key_suffix):
    """Generates a hash for the key validation."""
    raw = f"{LICENSE_SECRET}-{key_suffix}"
    return hashlib.sha256(raw.encode()).hexdigest()[:8].upper()

def validate_key_format(key):

    parts = key.strip().upper().split('-')
    if len(parts) != 4:
        return False
    
    checksum, part2, part3, part4 = parts
    suffix = f"{part2}-{part3}-{part4}"
    
    expected_checksum = generate_key_hash(suffix)
    return checksum == expected_checksum

class LicenseService:
    @staticmethod
    def is_activated():
        """Checks if the software is activated on this machine."""
        path = get_license_file_path()
        if not path.exists():
            return False
            
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                
            # Check if key is valid and matches this machine
            key = data.get('key')
            machine_id = data.get('machine_id')
            
            if not key or not validate_key_format(key):
                return False
                
            # Optional: Bind to machine to prevent copying the file
            if machine_id != get_machine_id():
                return False
                
            return True
        except Exception:
            return False

    @staticmethod
    def activate(key):
        """Attempts to activate the software with the given key."""
        if validate_key_format(key):
            path = get_license_file_path()
            data = {
                "key": key.strip().upper(),
                "machine_id": get_machine_id(),
                "activated_at": str(os.times())
            }
            with open(path, 'w') as f:
                json.dump(data, f)
            return True
        return False
