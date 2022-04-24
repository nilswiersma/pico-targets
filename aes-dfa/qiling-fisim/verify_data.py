from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key_s = None
encryptor = None
fail_count = 0
with open('sim.log', 'r') as inpf:
    for line in inpf.readlines():
        line = line.strip()
        if not key_s and 'keybuf' not in line:
            continue
        elif not key_s and 'keybuf' in line: 
            key_s = line.split(': ')[1][:32]
            print(key_s)
            print()
            aes = Cipher(algorithms.AES(bytes.fromhex(key_s)), modes.ECB(), backend=default_backend())
            encryptor = aes.encryptor()
        elif key_s and 'inpbuf' in line:
            inp_s = line.split(': ')[1][:32]
            inp_b = bytes.fromhex(inp_s)
        elif key_s and 'outbuf' in line:
            out_s = line.split(': ')[1][:32]
            out_b = bytes.fromhex(out_s)
            out_verify_b = encryptor.update(inp_b)
            if out_b != out_verify_b:
                fail_count += 1
                print('>', inp_b.hex())
                print('<', out_b.hex())
                print('?', encryptor.update(inp_b).hex(), out_b == out_verify_b)
                print()
            # break
if fail_count == 0:
    print('All tests passed!')