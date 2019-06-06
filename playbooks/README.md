# To deploy the ansible playbooks

## Prerequisites

Prerequisites server: RHEL 8, python3, docker and ssh access   git s
Prerequisites client: RHEL 8 ,**python3 preinstalled**

## Hosts

Example of **hosts**
```ini
[all:vars]
ansible_user=root
ansible_ssh_pass=password
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
[registry]
#Names of registry is mandatory on the third line ( head - 3 | tail -A)
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


## Default values

Default values in vars.yml:

* docker_mirror_registry_address : 172.16.7.253
* docker_mirror_registry_port : 5000
* docker_registry_port : 5001
* proxy : http://web-proxy.corp.hpecorp.net:8080

* ansible_python_interpreter : '/usr/bin/python3'
* RHEL_Version: rh8rc4_x86_64
* iso_server: 172.16.7.253
* iso_source_path: /opt/cmu/repositories
* iso_mount_point : /opt/cmu/repositories
* docker_compose_Version : 1.24.0
* time_server: ntp.hpecorp.net

NOTE: You can override default values in the command line with ` --extra-vars " <JSON syntax> " `, few examples below .

## Command line

Command line examples:  
```bash
ansible-playbook bdu-client-playbook.yml -i hosts --extra-vars "{ proxy : 'http://web-proxy.corp.hpecorp.net:8080 }"
```
You can also edit the vars.yml files.

NOTE: Docker_mirror_registry and docker_registry are on the same physical server
