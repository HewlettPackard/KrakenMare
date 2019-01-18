import subprocess
import json
import time
from random import *

# Read formatted JSON data that describes the switches in the IRU (c stands for CMC)
for cmc in ['r1i0c-ibswitch','r1i1c-ibswitch']:
   with open(cmc, 'r') as f:
      query_data = json.load (f)

# For each switch found in the JSON data generate perfquery with -a to summarize the ports
# This simulates a poor quality fabric in heavy use
# Using random numbers on 0,1 we update the error counters as
# [0,.75] no update
# [.75,.85] + 1
# [.85,.95] + 10 which is a warning condition
# [.95,1] + 1000 which is an error condition
# For data counters add randint[1000,4000]
# for packet counters add randint[100,400]
   now=time.time()
   nowint=long(now)

   for switch in query_data['Switch']:
      hca=str(switch['HCA'])
      port=str(switch['Port'])
      guid=str(switch['Node_GUID'])
      # Read in the old query outuput
      output="/tmp/" + guid +".perfquery.json"
      with open(output, 'r') as g:
         query_output = json.load (g)

      query_output['Timestamp'] = nowint
      x = random()
      if x > .95:
         query_output['SymbolErrorCounter'] += 1000
      elif x > .85:
         query_output['SymbolErrorCounter'] += 10
      elif x > .75:
         query_output['SymbolErrorCounter'] += 1

      x = random()
      if x > .95:
         query_output['LinkDownedCounter'] += 1000
      elif x > .85:
         query_output['LinkDownedCounter'] += 10
      elif x > .75:
         query_output['LinkDownedCounter'] += 1

      x = random()
      if x > .95:
         query_output['PortXmitDiscards'] += 100
      elif x > .85:
         query_output['PortXmitDiscards'] += 5
      elif x > .8:
         query_output['PortXmitDiscards'] += 2

      query_output['PortXmitData'] += randint(1000,4000)
      query_output['PortRcvData'] += randint(1000,4000)
      query_output['PortXmitPkts'] += randint(100,400)
      query_output['PortRcvPkts'] += randint(100,400)
      query_output['PortXmitWait'] += randint(100,200)

      with open(output, 'w') as g:
         json.dump(query_output,g)

      subprocess.call(["mosquitto_pub","-t","ibswitch","-f",output])
