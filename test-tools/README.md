# Test Tools for wp1.3

To test that the demo is working correctly, following the following steps:

STEP1

To test the installation, launch a browser and reach http://localhost:3000 (admin/admin by default) and check you have data in Dashboard/Home Monitoring

STEP2

Launch the test tools side car container with:

`docker run -ti --network demo_default --rm demo_test-tools /bin/bash`

or run-test-containers.sh from the directory above

#../run-tests-containers.sh

Once in the container test mosquitto with:

`mosquitto_sub -h mosquitto -t hello_topic`

and kafla with 

`kafkacat -b broker-1 -t fabric`
