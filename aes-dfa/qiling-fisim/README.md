Use [qiling](https://github.com/qilingframework/qiling) unicorn/qemu wrapper to simulate faults on `test_aes` by iterating through the execution and skipping instructions with `hook_code` (`ql.reg.pc += size + 1`).

- `python3.9 -m venv venv`
- `. venv/bin/activate`
- `pip install -r requirements.txt`
- `python sim.py | tee sim.log` (takes a few minutes, assumes `test_aes.elf` exists)
- `python extract_outbufs.py > sim.log.outbufs` 
- `python phoenixaes_recover.py` (assumes the first line of the file contains the correct output) 