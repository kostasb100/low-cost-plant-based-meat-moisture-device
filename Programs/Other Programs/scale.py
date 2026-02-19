"""
Standalone mass measurement module using the HX711 24-bit ADC and load cell.

This program:
- Uses a reference unit derived from calibration.py
- Provides real time measurements from the HX711 chip

Purpose:
- Measurement of plant-based sample mass before and after experimental cycles.
- Monitoring of scale drift, repeatability, and long-term measurement error.

Date: 2025-10
"""

import time
import RPi.GPIO as GPIO
from hx711 import HX711

# Setup HX711
hx = HX711(17, 27)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(2817)  # Use your calculated reference unit here
hx.reset()
hx.tare()

print("Scale ready! Place items to weigh...")
print("Press Ctrl+C to exit")

# Take three measurements, find their average and print it
try:
    while True:
        weight = hx.get_weight(3) # Can be adjusted
        print(f"Weight {weight:.2f}g")
        
        hx.power_down()
        hx.power_up()
        time.sleep(0.2)

# Shut down upon interrupt
except KeyboardInterrupt:
    print("\nExiting...")
    GPIO.cleanup()