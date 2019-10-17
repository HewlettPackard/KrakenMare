#!/bin/bash


# Change directory
cd $(dirname $0) || exit 1
KM_HOME=$(pwd)


#TEMPLATE
TOOL_NAME=`basename $0`
#unset args
unset $ansible;
unset $build;
unset $push;
unset $deploy;
unset $proxy;
unset $setupRegistry;
unset $restartDocker;
unset $stop;

dockerpull="--pull";

#DEFAULT ARGS
DEFAULT_INVENTORY_FILE=hosts;
MIRROR_REGISTRY_PORT=5001;


PROXY=http://grewebcachevip.bastion.europe.hp.com:8080
project_name=krakenmare

#Usage function
usage () {
     echo ""
     echo "usage : ${TOOL_NAME} [-h] "
     echo ""
     echo "At least one arguments is required "
     echo ""
     echo "-a: to run Ansible playbooks"
     echo "-r: to create Registry"
     echo "-p: to Pull"
     echo "-b: to Build and Push"
     echo "-f: do not force pulling newer image from dockerhub"
     echo "-d: to Deploy"
     echo "-i: to specify the inventory file (DEFAULT is ${DEFAULT_INVENTORY_FILE})"
     echo "-R: to restart the docker daemon locally (requires root privileges, only needed when proxy/registry config changed or is initialized"
     echo "-s: to stop the stack"
     echo "-h: to display help"
     echo "return code is 0 if all tasks success"
     echo "            is 1 if a task failed "
     echo "            is 2 if there is no registry available"
     echo "            is 3 if inventory file does not exist"
     echo "            is 4 if wget is not installed"
     echo ""
}

registry_content () {
     echo $registry will be used as registry node
     
     echo -n "[info] $registry catalog content on mirror registry (can be void if not running):"
     curl --max-time 3 $registry:5001/v2/_catalog 2> /dev/null
     echo ""
     echo -n "[info] $registry catalog content on private registry (can be void if not running):"
     curl --max-time 3 $registry:5000/v2/_catalog 2> /dev/null
     echo ""
}

#Parse args
while getopts "hfapbdrfi:Rs" Option
do
     case $Option in
         h     ) usage $0 ; exit 0        ;;
         a     ) ansible=1      ;;
         p     ) pull=1         ;;
         b     ) build=1        ;;
         d     ) deploy=1       ;;
	 f     ) dockerpull=""  ;;
         R     ) restartDocker=1;;
         i     ) DEFAULT_INVENTORY_FILE=${OPTARG}       ;;
         r     ) setupRegistry=1; ansible=1     ;;# To setup registry you have to setup the node first
         s     ) stop=1        ;;
         *     ) echo "unrecognized option, try $0 -h" >&2 ; usage $0 ; exit 1  ;;
     esac
done

#sanity checks

if [ -z $1 ];then
     usage $0; exit 1;
fi

if [ ! -f $DEFAULT_INVENTORY_FILE ]; then
     echo "" >&2; echo "$DEFAULT_INVENTORY_FILE does not exists, help available at $0 -h" >&2; 
     echo "" >&2;
     exit 3;
fi

#Registry vars
unset $registry;
registry=$(cat $DEFAULT_INVENTORY_FILE | sed -n -e '/\[registry\]/,$p' | grep -v "[\[,#,^$]" |sed  '/^$/d'| awk '{$1=$1};1' | head -1 | awk '{ print $1}' )
export no_proxy=$registry
export REGISTRY_FULL_PATH="$registry:$MIRROR_REGISTRY_PORT/" 

if  [ -z $registry ]
then
     echo "" >&2; echo "can't extract registry name from hosts, help available at $0 -h" >&2; 
     echo "" >&2;
     exit 1;
fi

#Display information about registry
registry_content;


#BODY

#Check proxy
export COMPOSE_FILE=../all-compose.yml:../secrets.yml
echo "Checking whether we are on the HPE LAN and needing a proxy..."
{ type wget &> /dev/null ; } || { echo "Unable to find wget in your env, install it to have automatic HPE proxy detection" ; exit 4 ;}


wget --no-proxy -q --dns-timeout=2 --timeout=2 www.google.com ; r=$?
echo "$r"
if [ ! $r -eq 0 ]; then
    wget -q --dns-timeout=5 --timeout=5 autocache.hpecorp.net -O /dev/null
    if [ $? -eq 0 ]; then
	export COMPOSE_FILE=${COMPOSE_FILE}:../docker-proxy.yml
	echo "HPE proxy USED..."
    else
	echo "network connectivity issue..."
	exit 1
    fi
fi


compose_args=$( for file in $(echo $COMPOSE_FILE | tr ":" "\n"); do   echo -n " -c $file "; done;)
# Example ../all-compose.yml:../docker-proxy.yml  ====> -c ../all-compose.yml -c ../docker-proxy.yml


if [  "$ansible" == "1"  ]; then
    #Build ansible
    docker build $dockerpull --build-arg http_proxy=$PROXY --build-arg https_proxy=$PROXY --tag ansible . || exit 1
    
    mkdir -p $KM_HOME/download-cache || exit 1
    
    #The last task restarts docker and therefore exits brutally, FIXME
    
    docker run --rm --volume $KM_HOME:/playbooks/ --volume $KM_HOME/$DEFAULT_INVENTORY_FILE:/etc/ansible/hosts --network=host ansible ansible-playbook /playbooks/kmu-client-playbook.yml --forks 100
     if [ "$restartDocker" == 1 ] ; then
          #need to be root to restart the docker service when proxy and/or registries have been reconfigured
          sudo systemctl daemon-reload || exit 1
          sudo systemctl restart docker || exit 1
     else
          echo "***"
          echo "[warning] daemon-reload and restart-docker skipped"
          echo "[warning] this is harmless if proxy or registries for `hostname` were already configured" 
          echo "[warning] add -R flag to force this step if needed (requires privileges)"
          echo "***"
     fi
     docker run --rm --volume $KM_HOME:/playbooks/ --volume $KM_HOME/$DEFAULT_INVENTORY_FILE:/etc/ansible/hosts --network=host ansible ansible-playbook /playbooks/swarm_exit.yml --forks 100 
     docker run --rm --volume $KM_HOME:/playbooks/ --volume $KM_HOME/$DEFAULT_INVENTORY_FILE:/etc/ansible/hosts --network=host ansible ansible-playbook /playbooks/swarm_init.yml  --forks 100

     if [ "$setupRegistry" == "1"  ]; then
          docker run --rm --volume $KM_HOME:/playbooks/ --volume $KM_HOME/$DEFAULT_INVENTORY_FILE:/etc/ansible/hosts --volume $KM_HOME/../docker-registry:/docker-registry/  --network=host ansible ansible-playbook /playbooks/launch_registry.yml --forks 100 
     fi
     
fi

if [ "$pull" == "1" ]; then
     # to only pull registry's content
     docker-compose pull || exit 1
fi

if [ "$build" == "1" ]; then
    docker-compose build $dockerpull || exit 1
    docker-compose push || exit 1
fi

if [ "$stop" == "1" ] || [ "$deploy" == "1" ]; then
     docker stack rm  $project_name ## No exit to prevent an error like "nothing to remove"
fi

if [ "$deploy" == "1" ]; then
						  
    cd ../km-security || exit 1
    #if all necessary secrets already exist in swarm, use them,
    #if not and they exist as files, push them
    #if not generate them and push them
    #delete files after pushing to swarm in all cases
    ./km-secrets-tool.sh -wcgpd || exit 1

    cd ../playbooks || exit 1
    docker stack deploy $compose_args $project_name || exit 1 

fi

