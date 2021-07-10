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

# print(joaat_hash3f_hex("radio"))

# def powerSet(items):
#     N = len(items)
#     # enumerate the 2**N possible combinations
#     for i in range(2**N):
#         combo = []
#         for j in range(N):
#             # test bit jth of integer i
#             if (i >> j) % 2 == 1:
#                 combo.append(items[j])
#         yield combo

# def get_powerset (string):
#     perm = []
#     if len(string) == 0:
#         perm.append("")
#         return perm
#     first = string[0]
#     rem = string[1:len(string)]
#     words = get_powerset(rem)
#     perm.extend(words)
#     for word in words:
#         perm.append(first+word)

#     return perm

# from itertools import permutations

# tape = "rmacusiwneAMW_-"
# input = [char for char in tape]

# target = 0x618D1833
# counter = 0;
# counterT = 0;

# for i in permutations(tape):
#     counter = counter + 1

#     if counter > 1000000:
#         counterT = counterT + 1
#         print("Crunched", str(counterT * 1000000), "combinations")
#         counter = 0
#     foundStr = ''.join(i)
#     foundHsh = joaat_hash(foundStr)

#     if target == foundHsh:
#         print(foundHsh, " hash(", foundHsh, ") matched target.")
