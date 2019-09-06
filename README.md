# Boat data logger pi project

Using a rasberry pi 3, make a boot sd with Raspbian... follow instructions here: 
https://youtu.be/ExPsG5yezbc

Once the pi has booted (can view this with a monitor), connect it to a machine or lan via ethernet cable and ssh into it using
```
ssh pi@raspberrypi.local
password: raspberry
```

Change password and locale etc using 
```
sudo raspi-config
```

then follow the instructions on https://github.com/Stu-emhTrade/sailmate/wiki/Set-up-wireless-access-point to set up an access point.

when plugged into a power supply, the pi should now have an access point, currently called
`PiWiFi`

# For Development
To ssh into the pi, connect to this wifi network and use

```
ssh pi@192.168.4.1
```


