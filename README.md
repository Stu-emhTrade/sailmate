# Boat data logger pi project

## Initial Pi Setup
Using a rasberry pi 3, make a boot sd with Raspbian... follow instructions here: 
https://github.com/Stu-emhTrade/sailmate/wiki/Setup-OS-image

then follow the instructions on https://github.com/Stu-emhTrade/sailmate/wiki/Set-up-wireless-access-point to set up an access point.

when plugged into a power supply, the pi should now have an access point, currently called
`PiWiFi`

## CANBUS

Follow instructions here to get the pi on the NMEA 2000 network:
https://github.com/Stu-emhTrade/sailmate/wiki/Setup-CAN-board
(Note this assumes one of these boards is connected to the pi https://copperhilltech.com/pican-2-can-bus-interface-for-raspberry-pi/)

after doing above, the canbus should be connected on boot on
`can0`

## Install Logger Application
To ssh into the pi, connect to this wifi network and use

```
ssh pi@192.168.4.1
```
clone the repo then run the following inside the repo folder
```
python3 -m venv .venv

source .venv/bin/activate

python3 -m pip install -r requirements.txt
```

We also use a small nodejs program to convert from actisense to signal k. npm should be on the pi already as part of the linux distro, but we need to install the package and set up the script executable.

download dependancies
```
cd stream_converter
npm install
```

install package globally, still in the stream_converter dir
```
sudo npm install -g
```

## For development

In pycharm, you can set up a remote interpreter so using the pi to develop on (but with the local file structure). To do this using a venv, follow these instructions. https://intellij-support.jetbrains.com/hc/en-us/community/posts/115000120270-Using-a-virtual-environment-on-a-remote-machine

The script is currently:
```
scripts/remote_dev_interpreter.sh
```
you may need to run
```
chmod +x scripts/remote_dev_interpreter.sh
```



## Currently we're using the canboat and signal K projects to parse data as it comes in

You'll need this repo https://github.com/SignalK/n2k-signalk.

```
sudo npm install -g https://github.com/SignalK/n2k-signalk.git
```



