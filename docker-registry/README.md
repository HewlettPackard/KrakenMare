# Docker registry

Command line to deploy registry on HPE network
```bash
docker-compose -f mirror-registry.yml -f config-mirror-registry.yml up -d 
```
else
```bash
docker-compose -f mirror-registry.yml -f docker-proxy.yml up -d 
```