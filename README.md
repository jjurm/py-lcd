# py-lcd

Python library for controlling character LCD displays using GPIO pins on the Raspberry Pi.
This library is capable of 8bit communication with the display.

based on sources:
 * http://esd.cs.ucr.edu/labs/interface/interface.html
 * https://github.com/arduino/Arduino/tree/master/libraries/LiquidCrystal
 * https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_CharLCD/Adafruit_CharLCD.py

## Usage

```python
import RPi.GPIO as GPIO
from CharLCD import CharLCD

# 8bit mode
lcd = CharLCD(pin_rs=25, pin_e=24, pins_db=[6, 13, 19, 26, 12, 16, 20, 21], fourbitmode=False, GPIO=GPIO)
lcd.begin(16, 2)

# 4bit mode
lcd = CharLCD(pin_rs=25, pin_e=24, pins_db=[12, 16, 20, 21], fourbitmode=True, GPIO=GPIO)
lcd.begin(16, 2)
```
