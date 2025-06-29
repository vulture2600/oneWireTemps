# Issues

### Data types in InfluxDB affecting alerting

Because temp and humidity columns are string types and not floats in the SandstoneSensorData.temps table, alerts in Grafana fail to evaluate. This is because they cannot compare string values to float/int values set as the alerting threshold in Grafana. See the following examples.

```sql
SELECT last(temp) FROM temps WHERE location = 'stageWallOutsideTemp'
```

```
name: temps
time                last
----                ----
1751153102963487979 77.6
```

```sql
SHOW FIELD KEYS FROM "temps"
```

```
name: temps
fieldKey  fieldType
--------  ---------
humidity  string
temp      string
timeStamp string
```

Possible solution

* New temp and humidity columns (key fields) in the SandstoneSensorData.temps table may need to be created with float at the data types.

* The [getTemps.py](src/getTemps.py) script will need to be updated to use non-string value for temp. The other Python script should be inspected for the same issue.

```phython
return "Off"  # string in read_temp() function

temp = "Off"  # string in __main__
```
