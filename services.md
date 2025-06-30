### Systemd services

Copy the service files in [src](src) to **/etc/systemd/system/** and follow this example to enable and start the services.

```shell
sudo systemctl daemon-reload

sudo systemctl enabled getSHT30.service
sudo systemctl start getSHT30.service

sudo systemctl status getSHT30.service
```
