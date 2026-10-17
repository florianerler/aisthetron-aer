#imports:
from machine import Pin

#variables:
"""
variables used for LED-controlls marked with number of the pin
"""
led_p_18 = Pin(18, Pin.OUT)
led_p_19 = Pin(19, Pin.OUT)
led_p_23 = Pin(23, Pin.OUT)
led_p_25 = Pin(25, Pin.OUT)
led_p_26 = Pin(26, Pin.OUT)

#definitions:
def led_mi_control(led):
    """
    mi stands for measurement indication
    """
    if led == 1:
        led_p_25.value(1)
    else:
        led_p_25.value(0)

def led_si_control(led):
    """
    si stands for stand-by indication
    """
    if led == 1:
        led_p_19.value(1)
    else:
        led_p_19.value(0)

def led_ei_control(led):
    """
    ei stands for error indication
    """
    if led == 1:
        led_p_26.value(1)
    else:
        led_p_26.value(0)

def led_i1_control(led):
    """
    i1 stands for indication 1, now not further defined
    """
    if led == 1:
        led_p_18.value(1)
    else:
        led_p_18.value(0)

def led_i2_control(led):
    """
    i2 stands for indication 2, now not further defined
    """
    if led == 1:
        led_p_23.value(1)
    else:
        led_p_23.value(0)