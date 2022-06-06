import threading
import serial
import time
import sys
import os
import random

# Inspiration from https://github.com/pyserial/pyserial/blob/master/serial/tools/miniterm.py
class SetupController():
    
    def __init__(self):
        self.alive = None

        self.target_thread = None
        self.target_alive = None
        self.target_ready = False
        self.target_serial_string = '/dev/ttyUSB0'
        self.target_empty_timeout = 1
        self.target_free_beers = 0

        self.glitcher_thread = None
        self.glitcher_alive = None
        self.glitcher_ready = False
        self.glitcher_serial_string = '/dev/ttyACM0'
        self.glitcher_attempts = 0

    def start(self):
        self.start_target()
        self.start_glitcher()
        self.alive = True
    
    def start_target(self):
        # start target communication thread
        self.target_thread = threading.Thread(target=self.talking_to_target, name='target')
        self.target_thread.start()
        self.target_alive = True

    def start_glitcher(self):
        # start target communication thread
        self.glitcher_thread = threading.Thread(target=self.glitching, name='glitcher')
        self.glitcher_thread.start()
        self.glitcher_alive = True

    def talking_to_target(self):
        # deal with target communication
        target = serial.Serial(self.target_serial_string, baudrate=115200, timeout=1)

        # using dtr for reset, need to invert to start pico
        target.dtr = not target.dtr

        start_empty_timer = True
        empty_timer = None

        key = bytes.fromhex('00a86acb4663f03801b6590384706c96')
        inp = bytes.fromhex('f1eea797844e6c0c808badbe8c91469e')
        expected_bytes = b'f1eea797844e6c0c808badbe8c91469e\r\ninpbuf: f1eea797844e6c0c808badbe8c91469e\r\noutput: 4b26bf29bb2f566d7e79227ae2e955f0\r\ninpbuf (16 hex)?\r\n> '
        
        do_reset = True

        with open(f'logs/log_{int(time.time())}.txt', 'w') as log_f:
            log_f.write('Key line:\n')
            log_f.write(f'{repr(key.hex())}\n')
            log_f.write('Expected data:\n')
            log_f.write(f'{repr(expected_bytes)}\n')
            log_f.write('\nCollected data:\n')
            while self.alive and self.target_alive:
                
                if do_reset:
                    target.dtr = not target.dtr
                    target.dtr = not target.dtr

                    target.reset_input_buffer()
                    target.reset_output_buffer()

                    tmp = target.read_until(b'> ')
                    # print(f'[t] {repr(tmp)}')
                    
                    target.write(key.hex().encode()[1:]) # skip the first byte, first character sending is a bit unstable (thanks to dtr for reset?)
                    data = target.read(len(b'\xff0a86acb4663f03801b6590384706c96\r\nkeybuf: 00a86acb4663f03801b6590384706c96\r\n'))
                    print(f'[t] {repr(data)}')

                    tmp = target.read_until(b'> ')
                    # print(f'[t] {repr(tmp)}')

                    do_reset = False
                
                ## Synchronize threads in an ugly way
                self.target_ready = True
                # print('[t] Waiting for glitcher ready')
                while not self.glitcher_ready:
                    if not self.alive or not self.target_alive:
                        break
                    # wait for glitcher to be ready before sending input
                    pass
                # print('[t] Glitcher ready, sending input')
                self.target_ready = False
                self.glitcher_ready = False

                target.write(inp.hex().encode())

                data = target.read(len(expected_bytes))
                print(f'[t] {repr(data)}')
                
                # if data[-2:] != b'> ':
                if data != expected_bytes:
                # if True:
                    data += target.read(target.in_waiting or 1024)
                    log_f.write(f'{repr(data)}\n')
                    do_reset = True

                # # read amount in buffer or block for 1 byte for target.timeout time
                # data = target.read(target.in_waiting or 1)
                # if data != b'':
                #     self.target_ready = True
                #     start_empty_timer = True

                #     if b'FREE BEER' in data:
                #         self.target_free_beers += 1

                #     try:
                #         sys.stdout.write(data.decode())
                #     except UnicodeDecodeError:
                #         sys.stdout.write(repr(data))
                #     sys.stdout.flush()
                
                # else:
                #     self.target_ready = False
                #     if start_empty_timer:
                #         empty_timer = time.time()
                #         start_empty_timer = False
                #     else:
                #         if empty_timer and time.time() - empty_timer > self.target_empty_timeout:
                #             print(f'\nNo data from target for {self.target_empty_timeout}s, trying reset')
                #             target.dtr = not target.dtr
                #             target.dtr = not target.dtr
                #             start_empty_timer = True

                #             # break
        
        target.close()
        self.target_alive = False
    
    def glitching(self):
        # deal with talking to glitcher

        serial_timeout = 2 # sometimes takes long until b'> \r\n'
        picoemp = serial.Serial(self.glitcher_serial_string, baudrate=115200, timeout=serial_timeout)

        # reset into default state, resets the whole USB controller
        picoemp.write(b'r\r\n')
        try:
            print(picoemp.readall())
        except serial.SerialException:
            picoemp.close()
            while True:
                print('[g] <picoemp serial dead!>')
                time.sleep(.1)
                try:
                    picoemp = serial.Serial(self.glitcher_serial_string, baudrate=115200, timeout=serial_timeout)
                    print('[g] leftover bytes:', picoemp.readall())
                    break
                except serial.SerialException:
                    pass
                except OSError:
                    pass
        
        picoemp.write(b'di\r\n')
        tmp = picoemp.read_until(b'> \r\n')
        print('[g]', tmp)
        print('[g] Auto-off disabled!')

        picoemp.write(b'a\r\n')
        tmp = picoemp.read_until(b'> \r\n')
        print('[g]', tmp)
        print('[g] Armed!')

        status = b''

        while self.alive and self.glitcher_alive:
            self.glitcher_attempts += 1

            # set up pulse length and delay
            picoemp.write(b'fa\r\n')
            tmp = picoemp.read_until(b'> \r\n')
            # print('[g]', tmp)
            delay_ns = random.randint(20000, 35000)
            delay_cycles = delay_ns//8
            pulse_ns = random.randint(100, 10000)
            pulse_cycles = pulse_ns//8
            picoemp.write(b'%d\r\n' % delay_cycles)
            tmp = picoemp.read_until(b'> \r\n')
            # print('[g]', tmp)
            picoemp.write(b'%d\r\n' % pulse_cycles)
            tmp = picoemp.read_until(b'> \r\n')
            # print('[g]', tmp)
            print('[g] Configured', delay_ns, delay_cycles, pulse_ns, pulse_cycles)

            charge_timer = time.time()
            while not b'Charged' in status:
                picoemp.write(b's\r\n')
                status = picoemp.read_until(b'> \r\n')
                # print(status)
            # print(f'[g] Charged after {time.time() - charge_timer:.2f} seconds')
            status = b''

            target_timer = time.time()
            while not self.target_ready:
                if not self.alive or not self.glitcher_alive:
                    break
            # print(f'[g] Target ready after {time.time() - target_timer:.2f} seconds')

            # input('Enter to pulse')
            picoemp.write(b'fast_trigger\r\n')
            # print('[g]', picoemp.read(1024))
            self.glitcher_ready = True
            tmp = picoemp.read_until(b'> \r\n')
            self.glitcher_ready = False
            # print('[g]', tmp)

            # time.sleep(1)
            # print('Pulsed')
            # picoemp.write(b'p\r\n')
            # picoemp.read_until(b'> \r\n').decode()
            # print('Pulsed')

            # self.glitcher_ready = False

            # if self.glitcher_attempts > 100:
            #     self.stop()
            #     break

        self.glitcher_alive = False

    def stop(self):
        self.alive = False

    def join(self):
        self.glitcher_thread.join()
        print('glitcher finished')
        self.target_thread.join()
        print('target finished')

# start the controller, and wait for it to finish  
control = SetupController()
try:
    control.start()
    # wait for threads to stop by themselves
    control.join()
except KeyboardInterrupt:
    print('Ctrl-C, exit')
    control.stop()
    # wait for threads to finish closing
    control.join()

print(f'{control.target_free_beers} FREE BEERs out of {control.glitcher_attempts} attempts (that is {control.target_free_beers/control.glitcher_attempts*100:.2f}% chance of FREE BEER!)')
