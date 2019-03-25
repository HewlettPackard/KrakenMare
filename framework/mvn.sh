#!/bin/bash

# Launch mvn with appropriate proxy setup
# if variable $https_proxy is set as https://name:port
opt=""
if [ _"$https_proxy" != _"" ]; then
	prox=`echo $https_proxy | cut -d: -f2 | cut -d/ -f3`
	port=`echo $https_proxy | cut -d: -f3`
	opt="-Dhttps.proxyHost=$prox -Dhttps.proxyPort=$port"
fi
echo "Running mvn $* $opt"
mvn $* $opt
