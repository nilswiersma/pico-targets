from shutil import ExecError
from qiling import Qiling
from qiling.const import QL_VERBOSE
from capstone import Cs

import subprocess
import os

BIN = r'/home/nils/projects/picoemp/pico-targets/aes-dfa/build/test_aes.elf'

nm_out = subprocess.check_output(["arm-none-eabi-nm", BIN]).decode()
nm_dict = {}
for nm_line in nm_out.split('\n'):
    if nm_line == '':
        continue
    try:
        addr_s, type_s, name_s = nm_line.split(' ')
        nm_dict[name_s] = {'type': type_s, 'addr': int(addr_s, 16)}
    except Exception as e:
        print(f'{repr(nm_line)}: {type(e)}, {e}')

def dumpregs(ql):
    for reg in ql.reg.register_mapping:
        if isinstance(reg, str):
            ql.log.debug(f'{reg}\t: {ql.reg.read(reg):#x}')

def simple_disassembler(ql: Qiling, address: int, size: int, user_data) -> None:
    # ql.log.debug("<")
    # ql.log.debug("simple_disassembler")
    # ql.log.debug(f'UC_MODE_THUMB: {ql.arch.check_thumb()==16}')
    # ql.log.debug(f'hook_code: {args}')
    # if 8 < user_data["ins_counter"] < 15:
    ql.log.debug(f'@{user_data["ins_counter"]}')
    ql.log.debug(f'ql.reg.pc={ql.reg.pc:08x} {ql.reg.pc&0x1}')
    ql.arch.utils.disassembler(ql, address, size)
    ql.log.debug(f'sp: {ql.reg.sp:08x}')
    ql.log.debug(f'r0: {ql.reg.r0:08x}')
    ql.log.debug(f'r6: {ql.reg.r6:08x}')
    ql.log.debug(f'r8: {ql.reg.r8:08x}')
    # dumpregs(ql)

    # ql.log.debug(f'ql.reg.r3: {ql.reg.r3:x}')
    # ql.log.debug(f'ql.reg.pc: {ql.reg.pc:x}')
    # ql.log.debug(">")
    # ql.log.debug(f'\t{address:08x}, {size:x}, {args}')
    
    # buf = ql.mem.read(address, size)
    # ql.log.debug(f'\t {repr(buf)}')
    # ql.log.debug(f'\t {buf[::-1].hex()} {buf.hex()}')
    # ql.log.debug(f'\t {len(buf)}')
    # print(f'{buf} {address} {0}')
    # dis = md.disasm(buf, address, 0)
    # print(list(dis))
    # # for insn in md.disasm(buf, address, 0):
    # #     ql.log.debug(f'\t\t {insn.address:#x} : {insn.mnemonic:24s} {insn.op_str}')

def main(user_data, verbose=QL_VERBOSE.DEFAULT):
    # set up command line argv and emulated os root path
    ROOTFS = r'/home/nils/projects/picoemp/pico-targets/aes-dfa/qiling-fisim/tmp'

    # instantiate a Qiling object using above arguments and set emulation verbosity level to DEBUG.
    # additional settings are read from profile file
    ql = Qiling([BIN], ROOTFS,
        log_file='sim.out', 
        verbose=verbose)#QL_VERBOSE.OFF)#DEBUG)#DEFAULT)#DEBUG)#, profile=False)

    ql.mem.map(0x20001000, size=0x20002000-0x20001000, info='mapfix1')
    ql.mem.map(0xd0000000, size=4096, info='some_mmap_io')
    
    THUMB = 1

    MAIN = nm_dict['main']['addr']
    MEM_KEYBUF = nm_dict['keybuf']['addr']
    MEM_INPBUF = nm_dict['inpbuf']['addr']
    MEM_OUTBUF = nm_dict['outbuf']['addr']
    MEM_SCRATCHPAD = nm_dict['scratchpad']['addr']

    ql.log.info(f'MAIN = {MAIN:08x}')
    ql.log.info(f'MEM_KEYBUF = {MEM_KEYBUF:08x}')
    ql.log.info(f'MEM_INPBUF = {MEM_INPBUF:08x}')
    ql.log.info(f'MEM_OUTBUF = {MEM_OUTBUF:08x}')
    ql.log.info(f'MEM_SCRATCHPAD = {MEM_SCRATCHPAD:08x}')

    # patch out 
    #  - some (hardware) calls with bx lr instruction
    #  - user IO (put data into memory directly)
    #  - __wrap___aeabi_memcpy (no sure how wrap_aeabi works, just hook and replace it ez)
    BXLR = b'\x70\x47'
    patch_this = {
        'stdio_init_all' : nm_dict['stdio_init_all']['addr'],
        'gpio_init' : nm_dict['gpio_init']['addr'],

        'sleep_ms' : nm_dict['sleep_ms']['addr'],
        
        '__wrap_printf' : nm_dict['__wrap_printf']['addr'],
        '__wrap_putchar' : nm_dict['__wrap_putchar']['addr'],
        '__wrap_getchar' : nm_dict['__wrap_getchar']['addr'],
        'strtol' : nm_dict['strtol']['addr'],
        # 'phex' : nm_dict['phex']['addr'], # gets inlined if not debug build
        # 'hexin' : nm_dict['hexin']['addr'], # gets inlined if not debug build

        '__wrap___aeabi_memcpy' : nm_dict['__wrap___aeabi_memcpy']['addr'],
    }

    for fname, addr in patch_this.items():
        ql.log.info(f'patching {fname} ({addr:08x})')
        ql.patch(addr, BXLR)

    # put a hook on AES_init_ctx to setup keybuf right before
    def hook_AES_init_ctx(ql):
        ql.log.debug(f'hook_AES_init_ctx')
        keybytes = bytes.fromhex('df92119f723cb00a121f232e0cfa7d26')
        ql.mem.write(MEM_KEYBUF, keybytes)
        ql.log.debug(f'MEM_KEYBUF: {ql.mem.read(MEM_KEYBUF, 16)}')
        print(f'keybuf: {keybytes.hex()}')

    ql.hook_address(hook_AES_init_ctx, nm_dict['AES_init_ctx']['addr'])

    # simple memcpy, also use as point to deal with input and output buffers
    def hook_memcpy(ql, user_data):
        dst = ql.reg.r0
        src = ql.reg.r1
        size = ql.reg.r2
        ql.log.debug(f'hook_memcpy {src:x} {dst:x} {size}')
        
        if src == MEM_INPBUF:
            ql.log.debug('INPUT')
            inpbytes = bytes.fromhex('a0d5d5810e4157aa2af5af5d92ca3e0f')
            ql.mem.write(MEM_INPBUF, inpbytes)
            print(f'inpbuf: {inpbytes.hex()}')

        ql.log.debug(f'{ql.mem.read(src, size)}')
        ql.mem.write(dst, bytes(ql.mem.read(src, size)))
        
        if dst == MEM_OUTBUF:
            ql.log.debug('OUTPUT')
            outbytes = ql.mem.read(MEM_OUTBUF, 0x10)
            print(f'outbuf: {outbytes.hex()} ({user_data["ecb_blocks_counter"]})')
            user_data['ecb_blocks_counter'] += 1
            if user_data['ecb_blocks_counter'] >= user_data['ecb_blocks_lim']:
                ql.emu_stop()
    ql.hook_address(hook_memcpy, nm_dict['__wrap___aeabi_memcpy']['addr'], user_data=user_data)

    def ins_counter(ql, addr, size, user_data):
        # fi_target_ins = 2000
        if user_data['ins_counter'] == user_data['fi_target_ins']:
            # just skip over it with pc increment?
            ql.log.info(f'@{user_data["ins_counter"]} skipping {addr:08x} {ql.mem.read(addr, size).hex()} with pc increment')
            ql.arch.utils.disassembler(ql, addr, size)

            ql.reg.pc += size + 1
            # https://github.com/unicorn-engine/unicorn/issues/1561#issuecomment-1100866404
            
            # maybe remove the hook after this to speed up things
            ql.hook_del(user_data['ins_counter_hook'])
        else:
            pass
        
        user_data['ins_counter'] += 1
    # keep the ret so we can easily drop it once not needed anymore
    user_data['ins_counter_hook'] = ql.hook_code(ins_counter, user_data=user_data)

    # ql.hook_code(simple_disassembler, user_data=user_data)
    
    # def dump(ql, user_data):
    #     ql.log.info(f'@{user_data["ins_counter"]} {0x10000486:08x}')
    #     ql.log.info(f'MEM_INPBUF: {ql.mem.read(MEM_INPBUF, 16).hex()}')
    #     ql.log.info(f'MEM_OUTBUF: {ql.mem.read(MEM_OUTBUF, 16).hex()}')
    #     ql.log.info(f'MEM_KEYBUF: {ql.mem.read(MEM_KEYBUF, 16).hex()}')
    #     ql.log.info(f'MEM_SCRATCHPAD: {ql.mem.read(MEM_SCRATCHPAD, 16).hex()}')
    # ql.hook_address(dump, 0x10000486, user_data=user_data)
    # ql.hook_address(dump, 0x10000486+0x12, user_data=user_data)

    ql.reg.r8 = 0xdeadbeef
    ql.run(begin=MAIN+THUMB, timeout=100000)
    
    del ql

if __name__ == "__main__":
    user_data = {
        'fi_target_ins': None,
        'ins_counter': 0,
        'ins_counter_hook': None,
        'ecb_blocks_counter': 0,
        'ecb_blocks_lim': 2,
    }
    main(user_data, QL_VERBOSE.DEFAULT)#DEBUG)
    # 1 block takes 6699-1976=4723 instructions

    # This causes memory leak somewhere :)
    for fi_target_ins in range(1976, 6699):
    # for fi_target_ins in range(4564, 6699):
        user_data = {
            'fi_target_ins': fi_target_ins,
            'ins_counter': 0,
            'ins_counter_hook': None,
            'ecb_blocks_counter': 0,
            'ecb_blocks_lim': 1,
        }
        print(f'fi_target_ins: {fi_target_ins}')
        try:
            main(user_data, QL_VERBOSE.DISABLED)
        except Exception as e:
            print(f'Exception: {type(e)} {e}')
