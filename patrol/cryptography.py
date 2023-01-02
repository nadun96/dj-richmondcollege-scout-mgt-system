from cryptography.fernet import Fernet


def encrypt_value(value):
    # Generate a key and use it to create a Fernet object
    key = Fernet.generate_key()
    fernet = Fernet(key)

    # Encrypt the value
    encrypted_value = fernet.encrypt(value.encode())

    # Return the encrypted value as a hexadecimal string
    return encrypted_value.hex()


def decrypt_value(encrypted_value, key):
    # Convert the encrypted value back to a bytes object
    encrypted_value = bytes.fromhex(encrypted_value)

    # Create a Fernet object using the key
    fernet = Fernet(key)

    # Decrypt the value
    decrypted_value = fernet.decrypt(encrypted_value)

    # Return the decrypted value as a string
    return decrypted_value.decode()
