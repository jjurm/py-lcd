#!/usr/bin/python

#
# Python library for controoling Character LCD display.
#
# by JJurM
#

from time import sleep


class CharLCD:

	MODE_COMMAND = 0
	MODE_DATA = 1

	LOW = 0
	HIGH = 1

	# commands
	CMD_CLEARDISPLAY     = 0x01
	CMD_RETURNHOME       = 0x02
	CMD_ENTRYMODESET     = 0x04
	CMD_DISPLAYCONTROL   = 0x08
	CMD_CURSORSHIFT      = 0x10
	CMD_FUNCTIONSET      = 0x20
	CMD_SETCGRAMADDR     = 0x40
	CMD_SETDDRAMADDR     = 0x80

	# Entry mode
	SHIFTED_TRUE = 1
	SHIFTED_FALSE = 0
	CURSORMOVEMENT_INCREASE = 1
	CURSORMOVEMENT_DECREASE = 0

	# Display control
	BLINKING_ON = 1
	BLINKING_OFF = 0
	CURSOR_ON = 1
	CURSOR_OFF = 0
	DISPLAY_ON = 1
	DISPLAY_OFF = 0

	# Cursor shift
	SHIFTDIRECTION_RIGHT = 1
	SHIFTDIRECTION_LEFT = 0
	SHIFT_DISPLAYSHIFT = 1
	SHIFT_CURSORMOVE = 0

	# Function set
	DOTSIZE_5x10DOTS = 1  # or 5x11
	DOTSIZE_5x7DOTS = 0   # or 5x8
	MULTILINE_2LINE = 1
	MULTILINE_1LINE = 0
	BITMODE_8BIT = 1
	BITMODE_4BIT = 0


	def __init__(self, pin_rs=25, pin_e=24, pins_db=[12, 16, 20, 21],
					   pin_backlight=None,
					   cols=16, rows=2, dotsize=None):

		# === Default configuration ===

		# Entry mode
		self.shifted = self.SHIFTED_FALSE
		self.cursorMovement = self.CURSORMOVEMENT_INCREASE

		# Display control
		self.blinking = self.BLINKING_OFF
		self.cursor = self.CURSOR_OFF
		self.display = self.DISPLAY_ON

		# Function set
		self.dotsize = self.DOTSIZE_5x7DOTS
		self.multiline = self.MULTILINE_1LINE
		self.bitmode = self.BITMODE_8BIT

		# === Arguments ===
		self.pin_rs = pin_rs
		self.pin_e = pin_e
		self.pins_db = pins_db

		if len(self.pins_db) < 8:
			self.bitmode = self.BITMODE_4BIT

		self.cols = cols
		self.rows = rows
		if dotsize == None:
			dotsize = self.DOTSIZE_5x7DOTS
		self.dotsize = dotsize
		self.multiline = (self.MULTILINE_2LINE if rows >= 2 else self.MULTILINE_1LINE)

		# === GPIO ===
		import RPi.GPIO as GPIO
		self.GPIO = GPIO

		self.GPIO.setmode(self.GPIO.BCM)
		self.GPIO.setwarnings(False)

		self.GPIO.setup(self.pin_e, self.GPIO.OUT)
		self.GPIO.setup(self.pin_rs, self.GPIO.OUT)
		pins = 4 if self.bitmode == self.BITMODE_4BIT else 8
		for i in range(pins):
			self.GPIO.setup(self.pins_db[-pins + i], self.GPIO.OUT)

		self.GPIO.output(self.pin_e, self.LOW)

		# Backlight pin
		self.pin_backlight = pin_backlight
		if self.pin_backlight is not None:
			self.GPIO.setup(self.pin_backlight, self.GPIO.OUT)
			self.GPIO.output(self.pin_backlight, self.LOW)

		# === Inicialization ===

		if self.bitmode == self.BITMODE_8BIT:
			# 8bit mode

			# initialisation sequence of 3 function set commands
			self.pushFunctionSet()
			self.msleep(4.5) # wait > 4.1ms

			# second attempt
			self.pushFunctionSet()
			self.usleep(150) # wait > 100us

			# third attempt
			self.pushFunctionSet()

		else:
			# 4bit mode

			# initialisation starts in 8bit mode
			self.write4bits(0x03)
			self.msleep(4.5) # wait > 4.1ms

			# second attempt
			self.write4bits(0x03)
			self.usleep(150) # wait > 100us

			# third attempt
			self.write4bits(0x03)

			# proceed to 4bit communication
			self.write4bits(0x02)

		# finally start configuration
		self.pushFunctionSet()
		self.pushDisplayControl()
		self.clear()
		self.pushEntryMode()


	def toRange(self, val, minimum, maximum):
		''' Ensures that the value will be in the specified range '''
		if val > maximum:
			val = maximum
		if val < minimum:
			val = minimum
		return val

	def msleep(self, milliseconds):
		''' Sleeps for specified number of milliseconds '''
		sleep(milliseconds / float(1000))

	def usleep(self, microseconds):
		''' Sleeps for specified number of microseconds '''
		sleep(microseconds / float(1000000))

	def pulseEnable(self):
		''' Makes standard short pulse on Enable pin '''
		self.GPIO.output(self.pin_e, False)
		self.usleep(10)       # enable pulse must be > 450ns
		self.GPIO.output(self.pin_e, True)
		self.usleep(10)       # enable pulse must be > 450ns
		self.GPIO.output(self.pin_e, False)
		self.usleep(100)      # commands need > 37us to settle

	def writeBits(self, bits, value):
		''' Writes specific number of bits of value and makes pulse '''
		for i in range(bits):
			self.GPIO.output(self.pins_db[-bits + i], (value >> i) & 0x01)
		self.pulseEnable()

	def write4bits(self, value):
		''' Writes last 4 bits of value and makes pulse '''
		self.writeBits(4, value)

	def write8bits(self, value):
		''' Writes last 8 bits of value and makes pulse '''
		self.writeBits(8, value)

	def send(self, value, mode):
		''' Writes value with given mode, auto 4/8-bit selection '''
		self.GPIO.output(self.pin_rs, mode)
		if self.bitmode == self.BITMODE_8BIT:
			self.write8bits(value & 0xFF)
		else:
			self.write4bits((value >> 4) & 0xF)
			self.write4bits(value & 0xF)

	def command(self, value):
		''' Sends value as command '''
		self.send(value, self.MODE_COMMAND)

	def data(self, value):
		''' Sends value as data '''
		self.send(value, self.MODE_DATA)

	def pushEntryMode(self):
		self.command(self.CMD_ENTRYMODESET
			| (0x01 * self.shifted)
			| (0x02 * self.cursorMovement)
		)

	def pushDisplayControl(self):
		self.command(self.CMD_DISPLAYCONTROL
			| (0x01 * self.blinking)
			| (0x02 * self.cursor)
			| (0x04 * self.display)
		)

	def pushFunctionSet(self):
		self.command(self.CMD_FUNCTIONSET
			| (0x04 * self.dotsize)
			| (0x08 * self.multiline)
			| (0x10 * self.bitmode)
		)


	def clear(self):
		''' Clears display (and returns cursor home) '''
		self.command(self.CMD_CLEARDISPLAY)

	def home(self):
		''' Returns cursor home '''
		self.command(self.CMD_RETURNHOME)

	def close(self, clear=False):
		if clear:
			self.clear()
		self.GPIO.cleanup()

	def moveCursor(self, col=0, row=0):
		''' Moves cursor to specified position '''
		col = self.toRange(col, 0, self.cols)
		row = self.toRange(row, 0, self.rows)
		offsets = [0x00, 0x40, 0x00 + self.cols, 0x40 + self.cols]
		self.command(self.CMD_SETDDRAMADDR | (offsets[row] + col))

	def shift(self, count=1, display=True):
		''' Shifts the cursor given # of times to the left (count can be negative); can also shift display (default) '''
		if count > 0:
			direction = self.SHIFTDIRECTION_LEFT
		elif count < 0:
			direction = self.SHIFTDIRECTION_RIGHT
		else:
			return
		count = abs(count)
		for i in range(count):
			self.command(self.CMD_CURSORSHIFT
				| (0x04 * direction)
				| (0x08 * (self.SHIFT_DISPLAYSHIFT if display else self.SHIFT_CURSORMOVE))
			)


	def setShifted(self, shifted):
		''' When enabled, display will shift after each data operation '''
		self.shifted = bool(shifted)
		self.pushEntryMode()

	def setCursorMovement(self, cursorMovement):
		''' Set direction to move cursor after each data operation '''
		if cursorMovement == -1:
			self.cursorMovement = cursorMovement
		else:
			self.cursorMovement = bool(cursorMovement)
		self.pushEntryMode()

	def setBlinking(self, blinking):
		''' Turns blinking cursor on/off '''
		self.blinking = bool(blinking)
		self.pushDisplayControl()

	def setCursor(self, cursor):
		''' Turns cursor pattern on/off '''
		self.cursor = bool(cursor)
		self.pushDisplayControl()

	def setDisplay(self, display):
		''' Turns display on/off '''
		self.display = bool(display)
		self.pushDisplayControl()


	def createChar(self, addr, bytemap):
		''' Creates character at given address (0-7) '''
		addr &= 0x7
		self.command(self.CMD_SETCGRAMADDR | (addr << 3))
		for i in range(8):
			if i < len(bytemap):
				self.data(bytemap[i])
			else:
				self.data(0x00)

	def setBackLight(self, on):
		if self.pin_backlight is not None:
			self.GPIO.output(self.pin_backlight, on)

	def write(self, string):
		''' Writes string char by char '''
		for char in string:
				self.data(ord(char))

	def wline(self, line, string=""):
		''' Writes string to specified line (clears whole line) '''
		string = string.ljust(self.cols)
		self.moveCursor(0, line)
		self.write(string)


