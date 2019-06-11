#!/usr/bin/env python
"""
================================================
Uses ABElectronics IO Pi 32-Channel Port Expander

Requires python smbus to be installed
For Python 2 install with: sudo apt-get install python-smbus
For Python 3 install with: sudo apt-get install python3-smbus

================================================

This example will control the door using simple button, sunrise/sundown and external (app).

Initialises the IOPi device using the default address
for Bus 2, you will need to change the addresses if you have changed
the jumpers on the IO Pi
"""

import sys
from threading import Timer
import logging

sys.path.append('.')
import blynklib

from hardware import Hardware
from sunrise import TimeCheck

logging.basicConfig(level=logging.DEBUG)

BLYNK_AUTH = 'c9d9d21bbf1c44c2851b72dc06c84cd9'
app_button_pressed = False
run_sun_door_check = False

# initialize blynk
blynk = blynklib.Blynk(BLYNK_AUTH)

# READ_PRINT_MSG = "[READ_VIRTUAL_PIN_EVENT] Pin: V{}"
# register handler for virtual pin V11 reading
# @blynk.handle_event('read V11')
# def read_virtual_pin_handler(pin):
#    print(READ_PRINT_MSG.format(pin))
#    blynk.virtual_write(pin, 101)

WRITE_EVENT_PRINT_MSG = "[WRITE_VIRTUAL_PIN_EVENT] Pin: V{} Value: '{}'"
# register handler for virtual pin V1 write event
@blynk.handle_event('write V1')
def write_virtual_pin_handler(pin, value):
    global app_button_pressed
    print(WRITE_EVENT_PRINT_MSG.format(pin, value))
    app_button_pressed = True

def schedule_sun_up_down():
    global run_sun_door_check
    run_sun_door_check = True
    print('schedule_sun_up_down')

SUN_CHECK_INTERVAL = 30

def main():
    global app_button_pressed
    global run_sun_door_check
    t = Timer(SUN_CHECK_INTERVAL,schedule_sun_up_down)
    t.start()

    hw = Hardware(False, False)
    s = TimeCheck('Brussels')
    hw.motor_down()  # @Startup open door
    door_state_up = False
    button_override = False

    while True:
        # blynk iot stuff
        #blynk.run()

        # move by button press
        if hw.button_pressed() or app_button_pressed:
            print ('button_pressed')
            app_button_pressed = False
            if door_state_up:
                hw.motor_down()
                door_state_up = False
                button_override = not button_override
            else:
                hw.motor_up()
                door_state_up = True
                button_override = not button_override

        # sunup triggers...only check every 5 min
        if run_sun_door_check:
            logging.debug ('sun door check')
            door_state_sun_is_up = s.run()
            logging.debug ('override  = %r' % button_override)
            if button_override:
                # Max override is until override state matches state indicated by the sun
                button_override = not (door_state_sun_is_up == door_state_up)
            else:
                # move by sunup/sundown
                if door_state_sun_is_up and not door_state_up:
                    hw.motor_up()
                    door_state_up = True
                    logging.debug('door up')
                elif not door_state_sun_is_up and door_state_up:
                    hw.motor_down()
                    door_state_up = False
                    logging.debug('door down')
                else:
                    logging.debug('door unchanged')
            run_sun_door_check = False
            t = Timer(SUN_CHECK_INTERVAL, schedule_sun_up_down)
            t.start()


if __name__ == "__main__":
    main()
