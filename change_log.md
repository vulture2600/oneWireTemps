# Update Log

[assignSensors.py](assignSensors.py)

```
7/6/24 - Steve McCluskey
Spent the last few weeks revamping this to a pretty funciontal proof of concept.
Still planning to implement non number input error handling when selecting from list.
Otherwise, it appears things seem to be working as they should.

7/18/24 - Steve McCluskey
Decided to show current temp when showing current config, which takes longer to collect each sensor,
but if its offline it wont show up in either list.
That led me to find that get_temp() wasnt able to handle a sensor thats offline like in my other script. 

8/14/24 - Steve McCluskey
Added logging to any changes in config file.
```


[getTemps.py](getTemps.py)

```
7/6/24 - Steve McCluskey
Updated to work with new config file format and other formatting tweaks in console output.

7/14/24 - Steve McCluskey
Added time stamps to each db write.
```


[getWeather.py](getWeather.py)

```
7/14/24 - Steve McCluskey
Added time stamps to each db write.
```


[viewSensors.py](viewSensors.py)

```
7/25/24 - Steve McCluskey
Added threading to grab sensors values concurrently and changed the file used to grab temps to "/temperature" instead of "w1_slave". I dont know if I'm going to keep it that way yet, since there is no CRC in that file.
```
