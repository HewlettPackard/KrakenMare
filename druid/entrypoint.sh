#!/bin/bash

echo "hello from druid... starting waiting for services..."

/tmp/wait-for --timeout=240 broker-1:9092 ||  { echo "timeout on b1" ; exit 1 ;  }
/tmp/wait-for --timeout=240 broker-2:9093 ||  { echo "timeout on b2" ; exit 1 ;  }
/tmp/wait-for --timeout=240 broker-3:9094 ||  { echo "timeout on b3" ; exit 1 ;  }
/tmp/wait-for --timeout=240 schemaregistry:8081 || { echo "timeout on schemaregistry" ; exit 1 ;  }

# Even though Java is in the path and is the right version druid still does not start. Hence we skip the java check.
export DRUID_SKIP_JAVA_CHECK=1

echo "Starting with KM_DRUID_SIZE_PROFILE $KM_DRUID_SIZE_PROFILE"

case $KM_DRUID_SIZE_PROFILE in
         nano     ) bin/start-nano-quickstart  ;;
         micro    ) bin/start-micro-quickstart  ;;
         small    ) bin/start-single-server-small ;;
         medium   ) bin/start-single-server-medium ;;
         large    ) bin/start-single-server-large ;;
         xlarge   ) bin/start-single-server-xlarge ;;
         *        ) echo "unrecognized KM_DRUID_SIZE_PROFILE option" ; exit 1  ;;
esac
