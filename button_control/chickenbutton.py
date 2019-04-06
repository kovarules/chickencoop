#!/usr/bin/env python
"""
================================================
Uses ABElectronics IO Pi 32-Channel Port Expander

Requires python smbus to be installed
For Python 2 install with: sudo apt-get install python-smbus
For Python 3 install with: sudo apt-get install python3-smbus


================================================

This example will control the door using simple button press.

Initialises the IOPi device using the default address
for Bus 2, you will need to change the addresses if you have changed
the jumpers on the IO Pi
"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import sys
import time

try:
    from IOPi import IOPi
except ImportError:
    print("Failed to import IOPi from python system path")
    print("Importing from parent folder instead")
    try:
        sys.path.append('..')
        from IOPi import IOPi
    except ImportError:
        raise ImportError("Failed to import library from parent folder")


class Hardware:
    """
    Hardware abstraction Class
    """
    bus = None

    def __init__(self):
        """
        __init__ is called at startup
        """

        # create an instance of Bus 1 which is on I2C address 0x21 by default
        self.bus = IOPi(0x20)

        # set pins 1 to 8 to be outputs and turn them off
        self.bus.set_port_direction(0, 0x00)
        self.bus.write_port(0, 0x00)

        # set pins 9 to 16 to be inputs and turn pullup on
        self.bus.set_port_direction(1, 1)
        self.bus.set_port_pullups(1, 1)

    def motor_stop(self):
        """
        controls the H-bridge to stop the motor.
        """
        # set all H-bridge switches to off
        self.bus.write_pin(1, 0x00)
        self.bus.write_pin(2, 0x00)
        self.bus.write_pin(3, 0x00)
        self.bus.write_pin(4, 0x00)

    def motor_up(self):
        """
        controls the H-bridge to move the motor in a specific direction.
        """
        # avoid conflicts
        self.motor_stop()

        # enable up
        self.bus.write_pin(1, 0x01)
        self.bus.write_pin(3, 0x01)

    def motor_down(self):
        """
        controls the H-bridge to move the motor in a specific direction.
        """
        # avoid conflicts
        self.motor_stop()

        # enable downward sidecof H-bridge
        self.bus.write_pin(1, 0x01)
        self.bus.write_pin(2, 0x01)

    def button_pressed(self):
        """
        controls the H-bridge to move the motor in a specific direction.
        """
        if self.read_pin(8) == 0:
            time.sleep(0.05)
            if self.read_pin(8) == 0:  # debounce 50 ms
                return True
        return False


def main():
    io = Hardware()
    doorStateUp = False  # standard at startup the door should be closed at powerup (unless detectable)
    timeToMove = 20

    while True:
        if io.button_pressed():
            if doorStateUp:
                io.motor_down()
            else:
                io.motor_up()
            time.sleep(timeToMove)
            io.motor_stop()


if __name__ == "__main__":
    main()
