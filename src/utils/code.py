import hashlib
import uuid


def create_invite_code(admin_id: int) -> str:
    # Create a random UUID
    random_uuid = uuid.uuid4()
    # Convert the admin_id to bytes and concatenate it with the bytes representation of the UUID
    combined = str(admin_id).encode() + str(random_uuid).encode()
    # Hash the combined bytes
    hashed = hashlib.md5(combined)
    # Return the hexadecimal representation of the hash
    return hashed.hexdigest()
