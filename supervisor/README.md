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

### MPMT node
