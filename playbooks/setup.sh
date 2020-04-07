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
unset $no_cache
unset $stop;
unset $importImages;
unset $exportImages;
dockerpull="--pull";
#DEFAULT ARGS
DEFAULT_INVENTORY_FILE=hosts;
MIRROR_REGISTRY_PORT=5001;


PROXY=http://web-proxy.bbn.hpecorp.net:8080
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
     echo "-F: perform a full docker build with --no-cache (do not combine with -f)"
     echo "-h: to display help"
     echo "-e: export registry content to an archive for later import"
     echo "-I: import registry content from an archive (created with -e)"
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
     curl --max-time 3 $registry:5000/v2/_catalog 2> /dev/null
     echo ""
     echo -n "[info] $registry catalog content on private registry (can be void if not running):"
     curl --max-time 3 $registry:5001/v2/_catalog 2> /dev/null
     echo ""
}

#Parse args
while getopts "hfapbdrfi:FRseI" Option
do
     case $Option in
         h     ) usage $0 ; exit 0        ;;
         a     ) ansible=1      ;;
         p     ) pull=1         ;;
         b     ) build=1        ;;
         d     ) deploy=1; stop=1 ;;
         f     ) dockerpull=""  ;;
         R     ) restartDocker=1;;
         F     ) no_cache='--no-cache';;
         i     ) DEFAULT_INVENTORY_FILE=${OPTARG}       ;;
         r     ) setupRegistry=1; ansible=1;;# To setup registry you have to setup the node first
         s     ) stop=1                    ;;
         e     ) exportImages=1; setupRegistry=1; ansible=1; build=1; stop=1 ;;# Need to build, push and stop the stack before exporting registry content
         I     ) importImages=1; setupRegistry=1; ansible=1; pull=1;;
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


wget --no-proxy -q --dns-timeout=2 --timeout=2 www.google.com -O /dev/null ; r=$?
echo "$r"
if [ ! $r -eq 0 ]; then
    wget -q --dns-timeout=5 --timeout=5 autocache.hpecorp.net -O /dev/null
    if [ $? -eq 0 ]; then
        export COMPOSE_FILE=${COMPOSE_FILE}:../docker-proxy.yml
        echo "HPE proxy USED..."
    else
        echo "network connectivity issue..."
    fi
fi


compose_args=$( for file in $(echo $COMPOSE_FILE | tr ":" "\n"); do   echo -n " -c $file "; done;)
# Example ../all-compose.yml:../docker-proxy.yml  ====> -c ../all-compose.yml -c ../docker-proxy.yml

if [  "$ansible" == "1"  ]; then

     if [ "$importImages" == "1" ]; then
         cd $KM_HOME/docker-registry
         echo "Extracting registries content tarball..."
         tar -xf registries-content.tar
         echo "Loading ansible docker image..."
         docker load -i ansible-docker-image.tar
         echo "Loading registry docker image..."
         docker load -i registry-docker-image.tar
         cd $KM_HOME
     else
         #Build ansible
         docker build $no_cache $dockerpull --build-arg http_proxy=$PROXY --build-arg https_proxy=$PROXY --tag ansible . || exit 1
     fi

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

         #TO BE REMOVED
         #stopping the mirror registries is necessary to stabilize our build systems
         #see #384 for details.
         #assuming we have the two registries like:
         #[root@o184i108 ~]# docker ps 
         #CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
         #f527a4303e4f        registry            "/entrypoint.sh /etc…"   5 weeks ago         Up 5 weeks          0.0.0.0:5000->5000/tcp   docker-registry_registry-mirror_1
         #d925eb8ce317        registry            "/entrypoint.sh /etc…"   5 weeks ago         Up 5 weeks          0.0.0.0:5001->5000/tcp   docker-registry_registry-private_1

         docker ps | grep docker-registry_registry- | awk '{ print $1}' | xargs docker stop

         if [ "$importImages" == "1" ]; then
              # don't do registry mirroring when importing, since the registry will die if it cannot acces the Internet
              docker-compose -f ../docker-registry/mirror-registry.yml -f ../docker-registry/docker-proxy.yml up -d
         else
              docker-compose -f ../docker-registry/mirror-registry.yml -f ../docker-registry/docker-proxy.yml -f ../docker-registry/registry-proxy.yml up -d
         fi
     fi
     
fi

if [ "$pull" == "1" ]; then
     # pull registry's content to warm-up cache before build
     # displays an error message for image not already existing in the registry, which is not a problem
     docker-compose pull
fi

if [ "$build" == "1" ]; then
    docker-compose build --parallel $no_cache $dockerpull || exit 1
    docker-compose push || exit 1
fi

if [ "$stop" == "1" ]; then
    echo "Check if prior krakenmare stack is completely gone"
    docker stack rm  $project_name ## No exit to prevent an error like "nothing to remove"
    #wait until that the stack is stopped
    until (( $(docker network ls | grep -c krakenmare) == 0 ))
    do
      sleep 3
      echo -n "."
    done
fi

if [ "$deploy" == "1" ]; then
    cd ../km-security || exit 1
    #if all necessary secrets already exist in swarm, use them,
    #if not and they exist as files, push them
    #if not generate them and push them
    #delete files after pushing to swarm in all cases
    ./km-secrets-tool.sh -wcgpd || exit 1

    cd ../playbooks || exit 1
    cmd="docker stack deploy $compose_args $project_name"
    echo "running..."
    echo "REGISTRY_FULL_PATH=$REGISTRY_FULL_PATH"
    echo $cmd
    eval $cmd || exit 1
fi

if [ "$exportImages" == "1" ]; then
    #make sure upstream image we don't build are available in the mirror registry
    echo "Pull required images..."
    docker-compose pull

    cd $KM_HOME/docker-registry
    echo "Saving ansible docker image..."
    docker save ansible:latest -o ansible-docker-image.tar
    echo "Saving registry docker image..."
    docker save registry -o registry-docker-image.tar
    echo "Exporting registries content..."
    tar -cf registries-content.tar  ansible-docker-image.tar registry-docker-image.tar registry-mirror/ registry-private/
    cd $KM_HOME
fi

