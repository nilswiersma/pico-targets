with open('sim.log', 'r') as inpf:
    for line in inpf.readlines():
        line = line.strip()
        if 'outbuf' in line:
            print(line.split(': ')[1][:32])