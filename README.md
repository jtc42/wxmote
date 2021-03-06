# wxmote
Host-side codebase for AmbiLight based on Pimoroni Mote, for Windows

A demo of the various modes can be seen [here](https://twitter.com/jtc9242/status/804073090993049602).

## Requirements
* Python 3 (should run on Python 2.7, but not tested)
* [WxPython >= 4](https://pypi.python.org/pypi/wxPython)
* [Mote](https://github.com/pimoroni/mote)
* [Numpy](http://www.numpy.org/)
* [Pillow](https://pypi.python.org/pypi/Pillow)
### Windows
* [PyWin32](https://pypi.python.org/pypi/pypiwin32)
* [WMI](https://pypi.python.org/pypi/WMI)
* [Open Hardware Monitor](http://openhardwaremonitor.org/) (Only required for CPU temperature monitoring)

## Getting started
Download/clone the repository, and install all dependencies in `requirements.txt` or `environment.yml` (conda).
From there, simply run 'main.pyw' using pythonw to suppress the command line. The tray icon should appear.
Double clicking the tray icon will open the main GUI, where all options can be changed.

*Note: You can have the application launch at startup (minimized to tray) by creating a shortcut to main.pyw in your user startup folder.*

## Arrangement of Mote sticks
To function properly without modifying the code, fix the Mote sticks to the back of your display as in the diagram

<img src="https://raw.githubusercontent.com/jtc42/wxmote/master/resources/layout.png" width="40%"/>

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
* **Contrast** - Boosts the contrast of the LED projection, to make darks darker and lights lighter.
* **Brightness** - Scales the overall brightness of the LEDs, to make the effect more subtle.

## Gradient images
Images to be used as gradients are stored in the /gradients folder. Some examples are included already.

Files must be 64 x N .bmp files, where N is the number of temperature-steps. This means that the CPU temperature range specified will be divided up into N values, and that row of pixels will be used as the gradient when the CPU is at the appropriate temperature. The top of the image corresponds to cool, the bottom corresponds to warm. 

The file name will be used in all menus.
