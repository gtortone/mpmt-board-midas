## Supervisor startup scripts

### MIDAS server

- copy `midas-mhttpd.conf` and `midas-mserver.conf` in `/etc/supervisor/conf.d/`
- configure supervisord for remote access in `/etc/supervisor/supervisord.conf`:
```
[inet_http_server]
port = *:9001
username = midas
password = changeme
```
- configure MIDAS Programs (Start command)
```
(rcfe) supervisorctl -s http://mpmthostname:9001 -u midas -p password start mpmt-rc
(hvfe) supervisorctl -s http://mpmthostname:9001 -u midas -p password start mpmt-hv
(snfe) supervisorctl -s http://mpmthostname:9001 -u midas -p password start mpmt-sn
```

### MPMT node

- copy `mpmt-rc.conf` and `mpmt-hv.conf` in `/etc/supervisor/conf.d/`
- modify `-i` argument in startup scripts accordingly to MPMT board index
- configure supervisord for remote access in `/etc/supervisor/supervisord.conf`:
```
[inet_http_server]
port = *:9001
username = midas
password = changeme
```
