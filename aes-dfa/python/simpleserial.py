import serial
import os

from serial.tools.list_ports import comports

if len(comports()) == 1:
    print(f'connecting to {comports()[0].device}')
    pico = serial.Serial(comports()[0].device, baudrate=115200, timeout=.1)
else:
    print([x.device for x in comports()])
    num = input('index?')
    pico = serial.Serial(comports()[int(num)].device, baudrate=115200, timeout=.1)

pico.dtr = not pico.dtr
print(pico.read_until(b'> '))

bs = os.urandom(16)
while True:
    pico.write(bs.hex().encode())
    print(pico.read_until(b'> '))
    #input()
