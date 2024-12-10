# taskmaster

### Useful commands

#### setup venv
```bash
source setup-venv.sh
```

#### run taskmaster

```bash
python3 taskmaster.py <config.yml> -l LEVEL 
```
> LEVEL = DEBUG, INFO, WARNING, ERROR, CRITICAL

#### socket
```bash
sudo lsof -i :<port>
```
```bash
sudo ss -tulnp | grep <port>
```
```bash
sudo netstat -an | grep <port>
```

#### processes
```bash
ps aux | grep <process>
```
```bash
ps aux | grep <process> | awk '{print $2}' | xargs kill -9
```
```bash
kill -9 <pid>
```