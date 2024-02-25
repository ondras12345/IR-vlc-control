# IR-vlc-control
This script allows you to control the VLC media player using any IR remote control.

There are probably better choices, like [LIRC](http://www.lirc.org/) (linux) or [WinLIRC](http://winlirc.sourceforge.net/) (Windows), but I wanted to create my own, simple to edit solution.

## Archived
I no longer use this software. There will be no further development. Feel free to fork and continue on your own.

## Setup and installation
1. Download this repository - download the latest release from the [Releases](https://github.com/ondras12345/IR-vlc-control/releases) page **and copy** [PyVLChttp](https://github.com/cheydrick/PyVLChttp/) repo to the `IR-vlc-control/PyVLChttp` directory,    
**OR clone** this repository and run `script/setup`. This initialises submodules.
1. Install requirements: `pip install -r requirements.txt`
1. Download the [IRremote Arduino Library](https://github.com/z3t0/Arduino-IRremote). Follow the steps described in their README.
1. Upload the IRrecvDump (NOT IRrecvDumpV2) example to your Arduino board, connect the required IR sensor.
1. Open the Arduino Serial monitor. Press the keys you want to assign to a function on the remote control and write down the codes that appear in the Serial moitor window. (eg. `NEC: 5EA110EF`)
1. Open VLC media player and set the http interface according to this [manual](https://wiki.videolan.org/Documentation:Modules/http_intf/). You'll have to set a password under Main interfaces -> Lua -> Lua HTTP.
1. Open the IR-vlc-control/IR_vlc_control.py file with your favorite text editor and locate the line that contains `# Settings:`
    - (Optionally) change `COM_PORT_DEFAULT` to your Arduino's COM port. This is just the default value the script will use if you just press enter on the _Enter serial port_ prompt.
    - You shouldn't need to change any of these: `PORT`, `IP`.
    - Change `VLC_PASSWORD` to the password you've chosen.
    - In `KEY_DICT`, assign the key codes you've captured to some actions (for list of possible commands see [PyVLChttp](https://github.com/cheydrick/PyVLChttp)): The first argument of KeyAction() is the assigned function - without parentheses, the second is just a name that is used in the log).
    - You shouldn't need to change `KEY_REPEAT_TIMEOUT`.
1. Run the script. You need to have Python interpreter installed.

## How to exit the script
Just press ctrl+c

## Hardware
You need an Arduino board that is compatible with the [IRremote Arduino Library](https://github.com/z3t0/Arduino-IRremote) and an IR sensor.
