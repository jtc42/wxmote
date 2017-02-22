# wxmote
Host-side codebase for AmbiLight based on Pimoroni Mote, for Windows

A demo of the various modes can be seen [here](https://twitter.com/jtc9242/status/804073090993049602).

## Requirements
* [PyWin32](https://pypi.python.org/pypi/pypiwin32)
* [WxPython](https://wxpython.org/download.php)
* [Mote](https://github.com/pimoroni/mote)
* [Open Hardware Monitor](http://openhardwaremonitor.org/) (Only required for CPU temperature monitoring)

## Getting started
Download/clone the repository, and install all dependencies listed above.
From there, simply run 'main.pyw' using pythonw to suppress the command line. The tray icon should appear.
Double clicking the tray icon will open the main GUI, where all options can be changed.

## Arrangement of Mote sticks
Details to follow...

## Options
### System
* **Colour** - Default colour to use for all channels
* **Set colour based on CPU temperature** - Grabs data from Open Hardware Monitor (if running) and selects a colour based on the CPU temperature and the gradient selected from the drop-down menu.
* **Pulse based on CPU load** - Pulses the LED brightness based on CPU load. High load leads to faster pulsing.
* **Minimum/maximum T** - Min and max expected temperatures for CPU. This is used to calculate the colour as a function of temperature, from the selected gradient.

### Rainbow
No options yet. Just makes rainbows

### Cinema
This is an AmbiLight clone, in which the colour of the screen edges is projected by the Mote sticks.

*Note: This mode does not work with all games. I'm unsure why, as some work but others don't. [Thumper](http://store.steampowered.com/app/356400/) is a great example of a game that both works, and looks fantastic.*
* **Contrast** - Boosts the contract of the LED projection, to make darks darker and lights lighter.
* **Brightness** - Scales the overall brightness of the LEDs, to make the effect more subtle.
