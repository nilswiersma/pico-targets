import threading
import serial
import time
import sys

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
        target = serial.Serial(self.target_serial_string, baudrate=115200, timeout=.1)

        # using dtr for reset, need to invert to start pico
        target.dtr = not target.dtr

        start_empty_timer = True
        empty_timer = None

        while self.alive and self.target_alive:
            # read amount in buffer or block for 1 byte for target.timeout time
            data = target.read(target.in_waiting or 1)
            if data != b'':
                self.target_ready = True
                start_empty_timer = True

                if b'FREE BEER' in data:
                    self.target_free_beers += 1

                try:
                    sys.stdout.write(data.decode())
                except UnicodeDecodeError:
                    sys.stdout.write(repr(data))
                sys.stdout.flush()
            
            else:
                self.target_ready = False
                if start_empty_timer:
                    empty_timer = time.time()
                    start_empty_timer = False
                else:
                    if empty_timer and time.time() - empty_timer > self.target_empty_timeout:
                        print(f'\nNo data from target for {self.target_empty_timeout}s, trying reset')
                        target.dtr = not target.dtr
                        target.dtr = not target.dtr
                        start_empty_timer = True

                        # break
        
        target.close()
        self.target_alive = False
    
    def glitching(self):
        # deal with talking to glitcher

        serial_timeout = 1
        picoemp = serial.Serial(self.glitcher_serial_string, baudrate=115200, timeout=serial_timeout)

        # reset into default state, resets the whole USB controller
        picoemp.write(b'r\r\n')
        try:
            print(picoemp.readall())
        except serial.SerialException:
            picoemp.close()
            while True:
                print('<picoemp serial dead!>')
                time.sleep(.1)
                try:
                    picoemp = serial.Serial(self.glitcher_serial_string, baudrate=115200, timeout=serial_timeout)
                    print(picoemp.readall())
                    break
                except serial.SerialException:
                    pass
                except OSError:
                    pass
        
        picoemp.write(b'a\r\n')
        picoemp.read_until(b'> \r\n').decode()
        print('Armed!')

        status = b''

        while self.alive and self.glitcher_alive:
            self.glitcher_attempts += 1

            charge_timer = time.time()
            while not b'Charged' in status:
                picoemp.write(b's\r\n')
                status = picoemp.read_until(b'> \r\n')
            # print(status.decode())
            print(f'Charged after {time.time() - charge_timer:.2f} seconds')
            status = b''

            target_timer = time.time()
            while not self.target_ready:
                if not self.alive or not self.glitcher_alive:
                    break
            
            print(f'Target ready after {time.time() - target_timer:.2f} seconds')
            
            
            # ctr += 1

            # input('Enter to pulse')
            picoemp.write(b'p\r\n')
            picoemp.read_until(b'> \r\n').decode()
            print('Pulsed')
            # picoemp.write(b'p\r\n')
            # picoemp.read_until(b'> \r\n').decode()
            # print('Pulsed')

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
