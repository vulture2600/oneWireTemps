# oneWireTemps

Code adapted from weatherStation along with OneWire sensors are being used to monitor ice farming for the [Sandstone Ice Park](https://www.mountainproject.com/area/106915985/sandstone-ice-park).

### InfluxDB

[influxdb](influxdb.md)

### Slack alerts

https://api.slack.com/apps > Grafana Alerts > Incoming Webhooks

Sample curl request to post to the #alerts channel. Get the full URL from the link above.

```shell
curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' https://hooks.slack.com/services/<REMOVED>
```

In Grafana:
1) Go to Alerting → Contact points
2) Add a new contact point of type Slack
3) Paste the webhook URL: 
```https://hooks.slack.com/services/<REMOVED>```
4) Save it

After this create alerts from the panels in the Grafana dashboard.

### Issues

[Issues](issues.md)

### Change log

[change_log](change_log.md)
