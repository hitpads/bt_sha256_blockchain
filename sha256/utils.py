def right_rotate(value, shift, size=32):
    # perform right rotate on value
    return ((value >> shift) | (value << (size - shift))) & (2**size - 1)
