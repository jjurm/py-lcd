# py-lcd

Python library for controlling character LCD displays using GPIO pins on the Raspberry Pi.
This library is capable of both 4bit and 8bit communication with the display. Allows creating of custom characters.

Based on sources:
 * http://esd.cs.ucr.edu/labs/interface/interface.html
 * https://github.com/arduino/Arduino/tree/master/libraries/LiquidCrystal
 * https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_CharLCD/Adafruit_CharLCD.py
 * https://github.com/dbrgn/RPLCD/blob/master/RPLCD/lcd.py

## Usage

```python
from CharLCD import CharLCD

# 8bit mode
lcd = CharLCD(pin_rs=25, pin_e=24, pins_db=[6, 13, 19, 26, 12, 16, 20, 21], cols=16, rows=2)
# OR 4bit mode
lcd = CharLCD(pin_rs=25, pin_e=24, pins_db=[12, 16, 20, 21], cols=16, rows=2)

# write text
lcd.write("Hello World!")

# move cursor
lcd.moveCursor(col=0, row=1)

# clear display and go home
lcd.clear()

# go home  (equals to moveCursor(0, 0))
lcd.home()

# cursor modes
lcd.setBlinking(True)
lcd.setCursor(True)

# create custom character
smiley = [
	0b00000,
	0b01010,
	0b00000,
	0b00100,
	0b10001,
	0b01110,
	0b00000,
	0b00000
]
lcd.createChar(addr=0, bytemap=smiley)
lcd.write("\x00")

# rewrite entire line
lcd.wline(line=0, string="Hello \x00")

# turn backlight on and off (if set up)
lcd.setBackLight(True)
```

