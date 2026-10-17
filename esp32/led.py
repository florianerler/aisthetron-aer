#imports:
from machine import Pin

#variables:
led_c = Pin(25, Pin.OUT)

#definitions:
def led_control(led):
    if led == 1:
        led_c.value(1)
    else:
        led_c.value(0)