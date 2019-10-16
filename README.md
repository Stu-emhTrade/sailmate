# Boat data logger pi project

## Initial Pi Setup
Using a rasberry pi 3, make a boot sd with Raspbian... follow instructions here: 
https://github.com/Stu-emhTrade/sailmate/wiki/Setup-OS-image

then follow the instructions on https://github.com/Stu-emhTrade/sailmate/wiki/Set-up-wireless-access-point to set up an access point.

when plugged into a power supply, the pi should now have an access point, currently called
`PiWiFi`

## For Development
To ssh into the pi, connect to this wifi network and use

```
ssh pi@192.168.4.1
```

If you set up Atom to access remote files on the pi go to packages > remote_atom > start server
then ssh using
```
ssh -R 52698:localhost:52698 pi@192.168.4.1
```
which will forward a port through. Then on the pi run `ratom <path to file>` and the file will appear in Atom where it can be edited and saved.

To copy files from the pi to local machine run
```
scp pi@192.168.4.1:path/to/file/on/pi /path/to/destination/file
```

## CANBUS

Follow instructions here to get the pi on the NMEA 2000 network:
https://github.com/Stu-emhTrade/sailmate/wiki/Setup-CAN-board
(Note this assumes one of these boards is connected to the pi https://copperhilltech.com/pican-2-can-bus-interface-for-raspberry-pi/)

after doing above, the canbus should be connected on boot on
`can0`

## node.js application

To log and dish up the data from the canbus, we'll use a node.js app called app.js. We want this to run on startup, so we've followed the instructions here:
https://github.com/Stu-emhTrade/sailmate/wiki/Setup-node.js-application-service to create a service called `canLogService`


