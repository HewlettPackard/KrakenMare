#!/bin/bash
  
cd $(dirname $0) || exit 1
BD_HOME=$(pwd)
PROXY=http://grewebcachevip.bastion.europe.hp.com:8080

#to be done see #146
export registry_name=$(hostname) || exit 1

if [ $UID -ne 0 ] ; then
    echo "root access needed for bootstraping" >&2 
    exit 1
fi


docker build --build-arg http_proxy=$PROXY --build-arg https_proxy=$PROXY --tag ansible . || exit 1
#The last task restarts docker and therefore exits brutally, FIXME
docker run --rm --volume $BD_HOME:/playbooks/ --network=host ansible ansible-playbook /playbooks/bdu-client-playbook.yml --inventory /playbooks/hosts --forks 10

docker run --rm --volume $BD_HOME:/playbooks/  --network=host ansible ansible-playbook /playbooks/ansible-clock.yml --inventory /playbooks/hosts --forks 10 || exit 1

docker run --rm --volume $BD_HOME:/playbooks/  --network=host ansible ansible-playbook /playbooks/swarm_exit.yml --inventory /playbooks/hosts --forks 10 || exit 1

docker run --rm --volume $BD_HOME:/playbooks/  --network=host ansible ansible-playbook /playbooks/swarm_init.yml --inventory /playbooks/hosts --forks 10 || exit 1

#Launch registry as late as possible ( docker swarm leave --force reset all exposed ports see #145)
docker-compose --file ../docker-registry/mirror-registry.yml --file ../docker-registry/docker-proxy.yml up -d --build || exit 1
docker stack rm project || exit 1
docker-compose -f ../all-compose.yml -f ../docker-proxy.yml build || exit 1
docker-compose -f ../all-compose.yml -f ../docker-proxy.yml push || exit 1
docker stack deploy -c ../all-compose.yml  -c ../docker-proxy.yml project || exit 1 
