#imports:
from machine import Pin

#variables:
"""
variables used for LED-controlls marked with number of the pin
"""
led_p_18 = Pin(18, Pin.OUT) #led[0], indicator 1 (now undefined), green LED
led_p_19 = Pin(19, Pin.OUT) #led[1], standby indicator, yellow LED
led_p_23 = Pin(23, Pin.OUT) #led[2], indicator 2 (now undefined), white LED
led_p_25 = Pin(25, Pin.OUT) #led[3], measurement indicator, blue LED
led_p_26 = Pin(26, Pin.OUT) #led[4], error indicator, red LED

#definitions:
"""
led driver, gets input via tuple
"""
def led_control(*led):
    if len(led) != 5:
        raise ValueError("Expected 5 arguments, got {}".format(len(led)))
    if led[0] == 1:
        led_p_18.value(1)
    else:
        led_p_18.value(0)
    if led[1] == 1:
        led_p_19.value(1)
    else:
        led_p_19.value(0)
    if led[2] == 1:
        led_p_23.value(1)
    else:
        led_p_23.value(0)
    if led[3] == 1:
        led_p_25.value(1)
    else:
        led_p_25.value(0)
    if led[4] == 1:
        led_p_26.value(1)
    else:
        led_p_26.value(0)