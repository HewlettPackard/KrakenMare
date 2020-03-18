# To deploy the ansible playbooks

## Prerequisites

Prerequisites server: RHEL 8, python3, docker,wget (proxy detection)

Prerequisites client: RHEL 8 ,**python3 preinstalled**

## Hosts

Example of **hosts**
```ini
[all:vars]
ansible_user=root
ansible_ssh_pass=password
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
[registry]
n0498
[supervisory_cloud]
n0498
[injectors]
#All injectors run collectd
n0498
...
n0505
[swarm_manager]
n0498
[swarm_nodes]
n0502
....
n0505
```

### How to fill hosts
#### Registry
Only one registry node  
If you want to create a registry node : **registry node must be on the swarm_manager**  
Else you can specify an existing registry  
#### Swarm_manager
Only one swarm_manager  
if you want to deploy: the swarm_manager must be the one running `./setup.sh`  

## Default values

Default values in vars.yml:
* docker_mirror_registry_port : 5000
* docker_registry_port : 5001
* proxy : http://web-proxy.bbn.hpecorp.net:8080
* ansible_python_interpreter : '/usr/bin/python3'
* RHEL_Version: rh8rc4_x86_64
* iso_server: 16.16.184.151
* iso_source_path: /data/repositories
* iso_mount_point : /data/repositories
* docker_compose_version : 1.24.0
* time_server: ntp.hpecorp.net


The password for the kmu user is *kmu*

## Command line

### Some examples 

Use ` -i <INVENTORY_FILE>` to specify the inventory file. Default name is *hosts*  

To run **a**nsible playbooks, create **r**egistry, **b**uild & push  and **d**eploy :
```bash
./setup.sh -arbd 
```


To only **b**uild and push to the private registry you can use
```bash
./setup.sh -b 
```
Then you can run **a**nsible **p**ull and **d**eploy on an other node by executing
```bash
./setup.sh -apd 
```


To have more informations use :
```bash
./setup -h
```