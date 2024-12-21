from constants import K, H
from utils import right_rotate
import struct


def preprocess_message(message):
    #make input message length a multiple of 512 bits.
    message = bytearray(message, 'ascii')
    original_length = len(message) * 8  # length in bits
    message.append(0x80)  # add the "1" bit followed by 0s
    while (len(message) * 8 + 64) % 512 != 0:  # pad with 0s
        message.append(0)

    # add og input message length as a 64 bit big-endian integer.
    message += struct.pack('>Q', original_length)
    return message


def split_into_chunks(message, chunk_size=64):
    # split the message into chunks
    for chunk_start in range(0, len(message), chunk_size):
        yield message[chunk_start:chunk_start + chunk_size]


def extend_schedule(chunk):
    # create message schedule array W for a 512b chunk
    w = list(struct.unpack('>16L', chunk)) + [0] * 48
    for i in range(16, 64):
        s0 = right_rotate(w[i - 15], 7) ^ right_rotate(w[i - 15], 18) ^ (w[i - 15] >> 3)
        s1 = right_rotate(w[i - 2], 17) ^ right_rotate(w[i - 2], 19) ^ (w[i - 2] >> 10)
        w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF
    return w


def compress_chunk(chunk, H):
    # proccess single 512b chunk.
    w = extend_schedule(chunk)
    a, b, c, d, e, f, g, h = H

    for i in range(64):
        S1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
        ch = (e & f) ^ (~e & g)
        temp1 = (h + S1 + ch + K[i] + w[i]) & 0xFFFFFFFF
        S0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
        maj = (a & b) ^ (a & c) ^ (b & c)
        temp2 = (S0 + maj) & 0xFFFFFFFF

        h, g, f, e, d, c, b, a = g, f, e, (d + temp1) & 0xFFFFFFFF, c, b, a, (temp1 + temp2) & 0xFFFFFFFF

    # update hash values
    return [(v + n) & 0xFFFFFFFF for v, n in zip(H, [a, b, c, d, e, f, g, h])]


def sha256(message):
    # compute sha256

    message = preprocess_message(message)

    # process every 512b chunk
    global H
    for chunk in split_into_chunks(message):
        H = compress_chunk(chunk, H)

    # render hash as a string
    return ''.join(f'{x:08x}' for x in H)
