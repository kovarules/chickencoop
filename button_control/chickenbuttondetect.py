#!/usr/bin/env python
# noinspection SpellCheckingInspection
"""
================================================
Uses ABElectronics IO Pi 32-Channel Port Expander

Requires python smbus to be installed
For Python 2 install with: sudo apt-get install python-smbus
For Python 3 install with: sudo apt-get install python3-smbus


================================================

This example will control the door using simple button press and will detect either of the
two end states using a switch

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
        raise ImportError(
            "Failed to import library from parent folder")


class Hardware:
    """
    Hardware abstraction Class
    """
    bus = None

    def __init__(self, simulated):
        """
        __init__ is called at startup
        """

        self.simulatedHw = simulated

        if self.simulatedHw:
            self.doorStateUp = False
        else:
            # create an instance of Bus 1 which is on I2C address 0x21 by default
            self.bus = IOPi(0x20)

            # set pins 1 to 8 to be outputs and turn them off
            self.bus.set_port_direction(0, 0x00)
            self.bus.write_port(0, 0x00)

            # set pins 9 to 16 to be inputs and turn pull-up on
            self.bus.set_port_direction(1, 1)
            self.bus.set_port_pullups(1, 1)
            self.timeToMove = 20
            if self.detect_door_down():
                self.doorStateUp = False
            elif self.detect_door_up():
                self.doorStateUp = True
            else:
                # reboot while undetermined state -> close door
                self.doorStateUp = True
                self.motor_down()

    def motor_stop(self):
        """
        controls the H-bridge to stop the motor.
        """
        if not self.simulatedHw:
            # set all H-bridge switches to off
            self.bus.write_pin(1, 0x00)
            self.bus.write_pin(2, 0x00)
            self.bus.write_pin(3, 0x00)
            self.bus.write_pin(4, 0x00)

    def motor_up(self):
        """
        controls the H-bridge to move the motor in a specific direction.
        """
        if not self.simulatedHw:
            # avoid conflicts
            self.motor_stop()

            # enable up
            self.bus.write_pin(1, 0x01)
            self.bus.write_pin(3, 0x01)

            time.sleep(self.timeToMove)
            self.motor_stop()
        self.doorStateUp = True

    def motor_down(self):
        """
        controls the H-bridge to move the motor in a specific direction.
        """
        if not self.simulatedHw:
            # avoid conflicts
            self.motor_stop()

            # enable downward side of H-bridge
            self.bus.write_pin(1, 0x01)
            self.bus.write_pin(2, 0x01)

            time.sleep(self.timeToMove)
            self.motor_stop()
        self.doorStateUp = False

    def button_pressed(self):
        """
        checks if the button is pressed with debouncing.
        """
        if self.simulatedHw:
            return False
        else:
            pin = 9
            if self.bus.read_pin(pin) == 0:
                time.sleep(0.05)
                if self.bus.read_pin(pin) == 0:  # debounce 50 ms
                    return True
            return False

    def detect_door_down(self):
        """
        checks if the door if completely at the down end stop
        """
        if self.simulatedHw:
            return True
        else:
            pin = 10
            if self.bus.read_pin(pin) == 0:
                time.sleep(0.05)
                if self.bus.read_pin(pin) == 0:  # debounce 50 ms
                    return True
            return False

    def detect_door_up(self):
        """
        checks if the door if completely at the down end stop
        """
        if self.simulatedHw:
            return True
        else:
            pin = 11
            if self.bus.read_pin(pin) == 0:
                time.sleep(0.05)
                if self.bus.read_pin(pin) == 0:  # debounce 50 ms
                    return True
            return False

    def is_door_up(self):
        """
        Returns the state of the door without checking the hardware to save detection time
        """
        return self.doorStateUp


def main():
    io = Hardware(False)

    while True:
        # move by button press
        if io.button_pressed():
            if io.is_door_up():
                io.motor_down()
            else:
                io.motor_up()
    # move by sunup/sundown ( + 30 min)


if __name__ == "__main__":
    main()
