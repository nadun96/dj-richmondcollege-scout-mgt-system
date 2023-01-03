# utility.py
def generate_code(item_id):
    # Convert the item ID to a string and pad it with zeros
    code = str(item_id).zfill(5)
    return code
