import utime as time
import machine
import esp
import io
import json
import os
import random
from machine import I2C, Pin, RTC
from ht16k33segment14 import HT16K33Segment14
from ds3231 import DS3231
from inputs import Switch


i2c = I2C(0)

ds = DS3231(i2c)
display = HT16K33Segment14(i2c, is_ht16k33=True)
display.set_brightness(2)
display.clear()

# display.set_character(chr(a), 0, point_state)
# display.set_number(a, 0, point_state)
# display.draw()


mode_pin = Pin(27, Pin.IN, Pin.PULL_UP)
mode_sw = Switch(mode_pin)
mode_sw_value = False
mode_has_new_val = False

minus_pin = Pin(25, Pin.IN, Pin.PULL_UP)
minus_sw = Switch(minus_pin)
minus_has_new_val = False

plus_pin = Pin(26, Pin.IN, Pin.PULL_UP)
plus_sw = Switch(plus_pin)
plus_has_new_val = False

def wait_pin_change(pin):
    # wait for pin to change value
    # it needs to be stable for a continuous 20ms
    cur_value = pin.value()
    active = 0
    while active < 20:
        if pin.value() != cur_value:
            active += 1
        else:
            active = 0
        time.sleep_ms(1)

def read_conf():
    with open('.userconf', 'r') as f:
        return json.load(f)

def write_conf(conf):
    with open('.userconf', 'w') as f:
        json.dump(conf, f)


def set_hour(initial):
    display.clear()
    display.set_character('H', 0, False)
    display.set_character('r', 1, False)

    hour = initial

    while True:
        if plus_pin.value() == 0:
            # increment up to 23
            hour += 1
            if hour >= 24:
                hour = 0
            time.sleep_ms(200)
        if minus_pin.value() == 0:
            hour -= 1
            if hour <= 0:
                hour = 23
            time.sleep_ms(200)
        if mode_pin.value() == 0:
            time.sleep_ms(400)
            return hour

        hr_str = f'{hour:02}'
        display.set_character(hr_str[0], 2, False)
        display.set_character(hr_str[1], 3, False)
        display.draw()
        time.sleep(.01)

def set_minute(initial):
    display.clear()
    display.set_character('M', 0, False)
    display.set_character('n', 1, False)

    minute = initial

    while True:
        if plus_pin.value() == 0:
            # increment up to 23
            minute += 1
            if minute >= 60:
                minute = 0
            time.sleep_ms(200)
        if minus_pin.value() == 0:
            minute -= 1
            if minute <= 0:
                minute = 59
            time.sleep_ms(200)
        if mode_pin.value() == 0:
            time.sleep_ms(400)
            return minute

        hr_str = f'{minute:02}'
        display.set_character(hr_str[0], 2, False)
        display.set_character(hr_str[1], 3, False)
        display.draw()
        time.sleep(.01)


def show_str(s):
    display.clear()
    for i, c in enumerate(s):
        display.set_character(c, i, False)
    display.draw()

def set_dst(dst_flag):
    labels = ['ETE', 'HIV']
    show_str(labels[dst_flag])
    curr_pos = dst_flag
    while True:
        if plus_pin.value() == 0 or minus_pin.value() == 0:
            curr_pos = (curr_pos + 1) % 2
            show_str(labels[curr_pos])
            time.sleep_ms(200)
        if mode_pin.value() == 0:
            time.sleep_ms(400)
            return curr_pos
        time.sleep_ms(10)


def set_time():
    display.clear()
    display.set_brightness(14)
    display.set_character("S", 0, False)
    display.set_character("E", 1, False)
    display.set_character("T", 2, False)
    display.draw()
    time.sleep_ms(500)

    t = list(ds.datetime())
    config = read_conf()

    # dst = set_dst(config['dst'])
    dst = 0
    hour = set_hour(t[4])
    minute = set_minute(t[5])
    t2 = list(ds.datetime())
    second = t2[6] if all([hour == t[4], minute == t[5]]) else 0

    t[4] = hour
    t[5] = minute
    print(f'will set the time to {dst} {hour}:{minute}:{second}')
    ds.datetime((t[0], t[1], t[2], hour, minute, second))
    config['dst'] = dst
    write_conf(config)
    do_explode()

try:
    config = read_conf()
except OSError:
    print("No config file found, creating one.")
    config = {'dst': 0}
    write_conf(config)

def do_explode():
    show_str(' 3  ')
    time.sleep_ms(500)
    show_str('  2 ')
    time.sleep_ms(500)
    show_str('   1')
    time.sleep_ms(500)
    show_str('boum')
    time.sleep_ms(1000)

do_explode()

while True:
    current_time = list(ds.datetime())
    print("Current Time is", current_time)

    display.clear()

    if mode_pin.value() == 0:
        # enter setup mode.
        set_time()
        config = read_conf()

    if random.random() <= 0.001:
        do_explode()

    # Get 0 padded digits.
    if config['dst'] == 1:
        current_time[4] += 1
        current_time[4] %= 24

    hours = f"{current_time[4]:02}"
    minute = f"{current_time[5]:02}"
    seconds = current_time[6]
    second_pulse = seconds % 2

    display.set_character(hours[0], 0, False)
    display.set_character(hours[1], 1, second_pulse)
    display.set_character(minute[0], 2, False)
    display.set_character(minute[1], 3, False)

    if second_pulse:
        display.set_brightness(14)
    else:
        display.set_brightness(8)

    display.draw()
    time.sleep(0.2)
