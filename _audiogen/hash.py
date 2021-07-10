def joaat_hash(inp):
    encoded = str.encode(inp)
    hsh = 0
    for byte in encoded:
        hsh += byte
        hsh &= 0xFFFFFFFF
        hsh += hsh << 10
        hsh &= 0xFFFFFFFF
        hsh ^= hsh >> 6

    hsh += hsh << 3
    hsh &= 0xFFFFFFFF
    hsh ^= hsh >> 11
    hsh &= 0xFFFFFFFF
    hsh += hsh << 15
    hsh &= 0xFFFFFFFF
    return hsh

def joaat_hash3f(inp):
    encoded = str.encode(inp)
    hsh = 0
    for byte in encoded:
        hsh += byte
        hsh &= 0xFFFFFFFF
        hsh += hsh << 10
        hsh &= 0xFFFFFFFF
        hsh ^= hsh >> 6

    hsh += hsh << 3
    hsh &= 0xFFFFFFFF
    hsh ^= hsh >> 11
    hsh &= 0xFFFFFFFF
    hsh += hsh << 15
    hsh &= 0xFFFFFFFF
    hsh &= 0x3FFFFFFF
    return hsh

def joaat_hash_hex(inp):
    return str(hex(joaat_hash(inp)))

def joaat_hash3f_hex(inp):
    return str(hex(joaat_hash3f(inp)))

def joaat_hash_hex_fill(inp, places):
    return f"0x{joaat_hash_hex(inp).zfill(places)}"