import phoenixAES

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


r_con = (
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
    0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
    0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
    0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
)

s_box = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

def bytes2matrix(text):
    """ Converts a 16-byte array into a 4x4 matrix.  """
    return [list(text[i:i+4]) for i in range(0, len(text), 4)]

def matrix2bytes(matrix):
    """ Converts a 4x4 matrix into a 16-byte array.  """
    return bytes(sum(matrix, []))

def xor_bytes(a, b):
    """ Returns a new byte array with the elements xor'ed. """
    return bytes(i^j for i, j in zip(a, b))

def reverse_expand_key(ik10):
    key_columns = [
        [None]*4, [None]*4, [None]*4, [None]*4,
        [None]*4, [None]*4, [None]*4, [None]*4,
        [None]*4, [None]*4, [None]*4
    ]

    for idx in range(0,16,4):
        key_columns[-1][idx//4] = ik10[idx:idx+4]

    for idx in range(-1, -11, -1):
        for i in range(-1, -4, -1):
            word = key_columns[idx][i]
            pword = key_columns[idx][i-1]
            key_columns[idx-1][i] = xor_bytes(pword, word)

        word = key_columns[idx][-4]
        pword = key_columns[idx-1][-1]
        pword = list(pword)
        pword.append(pword.pop(0))
        pword = pword
        pword = [s_box[b] for b in pword]
        pword[0] ^= r_con[11 + idx]
        key_columns[idx-1][-4] = xor_bytes(pword, word)

    return [b''.join(key_column) for key_column in key_columns]

def expand_key(master_key):
    """
    Expands and returns a list of key matrices for the given master_key.
    """
    # Initialize round keys with raw key material.
    key_columns = bytes2matrix(master_key)
    iteration_size = len(master_key) // 4

    # Each iteration has exactly as many columns as the key material.
    columns_per_iteration = len(key_columns)
    i = 1
    while len(key_columns) < (10 + 1) * 4:
        # Copy previous word.
        word = list(key_columns[-1])

        # Perform schedule_core once every "row".
        if len(key_columns) % iteration_size == 0:
            # Circular shift.
            word.append(word.pop(0))
            # Map to S-BOX.
            word = [s_box[b] for b in word]
            # XOR with first byte of R-CON, since the others bytes of R-CON are 0.
            word[0] ^= r_con[i]
            i += 1
        elif len(master_key) == 32 and len(key_columns) % iteration_size == 4:
            # Run word through S-box in the fourth iteration when using a
            # 256-bit key.
            word = [s_box[b] for b in word]

        # XOR with equivalent word from previous iteration.
        word = xor_bytes(word, key_columns[-iteration_size])
        key_columns.append(word)

    # Group key words in 4x4 byte matrices.
    return [key_columns[4*i : 4*(i+1)] for i in range(len(key_columns) // 4)]

# refkey = 'df92119f723cb00a121f232e0cfa7d26'
# ik10 = phoenixAES.crack_file('sim.log.outbufs')
# print(f'ik{10}: {ik10}')
# print()
# for kidx, ik in enumerate(reverse_expand_key(bytes.fromhex(ik10))):
#     if kidx == 0 and ik.hex() == refkey:
#         print(f'ik{kidx:02d} matches refkey!')
#     print(f'ik{kidx:02d}: {ik.hex()}')

logfn = 'logs/log_1653657508.txt'
lines = []
with open(logfn, 'r') as logf:
    lines = logf.readlines()

# refkey line
refkey = eval(lines[1])

# ref in/out line
refinp, refout = lines[3][46:78], lines[3][90:122]
refinp = bytes.fromhex(refinp)
refout = bytes.fromhex(refout)

aes = Cipher(algorithms.AES(refkey), modes.ECB(), backend=default_backend())
assert(aes.encryptor().update(refinp) == refout)

outputs = []
good_faults = 0
phoenixAES.check(refout, encrypt=True, verbose=1, init=True)
for line in lines[6:]:
    if line[82:90] == 'output: ' and line[122:126] == '\\r\\n':
        output = bytes.fromhex(line[90:122])
        outputs.append(output)
        status = phoenixAES.check(output, encrypt=True, verbose=1, init=False)[0]
        if status == phoenixAES.FaultStatus.GoodEncFault:
            good_faults += 1
            print(output.hex(), status)

print(f'Good faults: {good_faults} / {len(outputs)} ({good_faults/len(outputs)*100:.2f})')

ik10 = phoenixAES.crack_bytes(outputs, refout, lastroundkeys=[], encrypt=True, outputbeforelastrounds=True, verbose=1)

print(f'ik{10}: {ik10}')

for kidx, ik in enumerate(expand_key(refkey)):
    if kidx != 0:
        print(f'{kidx:2d}: {b"".join(ik).hex()}')
        print(f'    {ik10}')

# if ik10 != None:
#     for kidx, ik in enumerate(reverse_expand_key(bytes.fromhex(ik10))):
#         if kidx == 0 and ik.hex() == refkey:
#             print(f'ik{kidx:02d} matches refkey!')
#         print(f'ik{kidx:02d}: {ik.hex()}')