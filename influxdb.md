# InfluxDB

#### Systemctl for InfluxDB

```shell
sudo systemctl enable influxdb
sudo systemctl disable influxdb

sudo systemctl start influxdb
sudo systemctl stop influxdb
sudo systemctl status influxdb
```

#### Connect to InfluxDB

```shell
# Connect to InfluxDB running on the localhost without the password set:
influx

# Connect to InfluxDb running on another host:
influx -host 192.168.1.10 -username fakeuser -password fakepassword

# Same as above and specify the port and database:
influx -host 192.168.1.10 -port 8086 -username fakeuser -password fakepassword -database SandstoneSensorData
```

#### Databases, Measurements

```sql
-- In the influx shell, the semicolon at the end of the line isn't
-- necessary but will be included for the sake of convention.
-- Keywords are also capitalized but not necessary.
 
-- Show databases (power_monitor_sandstone, SandstoneSensorData):
SHOW databases;

-- Use the SandstoneSensorData database:
USE SandstoneSensorData;

-- Show measurements (pressures, temps, weather):
SHOW MEASUREMENTS;
```

#### Queries

```sql
-- List the latest 30 temps taken:
SELECT * FROM temps ORDER BY time DESC LIMIT 30;

-- List the latest 30 readings from the Derrick Wall:
SELECT * AS readable_time FROM temps WHERE location = 'derrickWallEnclTemp' ORDER BY time DESC LIMIT 30;

-- List the first temp from each day for the last 30 days:
SELECT FIRST("temp") AS first_temp_of_day FROM "temps" WHERE time >= now() - 30d GROUP BY time(1d);

-- Show counts from countable columns:
SELECT count(*) FROM temps;

-- List series limit to 5 rows:
SHOW SERIES LIMIT 5;
```
