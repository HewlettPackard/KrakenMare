# coding=utf-8
import paho.mqtt.client
import time
import threading
import collections
import datetime
import pytz
import json
import pathlib
import pytoml


import influxdb
class InfluxPush :
    # -------------------------- Init --------------------------
    def __init__(self, params=None):
        self.myInfluxClient   = None
        self.myInfluxClientDF = None
        if params is None :
            params = dict()
        self.myIP           = params.get('ip')          or '127.0.0.1'
        self.myPort         = params.get('port')        or int(8086)
        self.myUsername     = params.get('username')    or 'username'
        self.myPassw        = params.get('password')    or 'password'
        self.myDefaultDB    = params.get('dbdefault')   or 'defaultdb'
        self.myTimeout      = params.get('timeout')     or int(10)
    # -------------------------- Quick insert  --------------------------
    def insertInIDB(self, dbnameoverride=None, liste_objets=None):
        """ Insert 1 or more records into Influx. In case of error, the push will be forgotten. If influx not connected, the connection will be done.
        :param dbnameoverride: if different than the one initialized.
        :param liste_objets: List of dict for influx : timestamp, measurements, tags, fields
        :return: True if sucess, False if problem
        """
        retour = False
        if liste_objets is not None :
            try :
                if self.myInfluxClient is None :
                    self.myInfluxClient = influxdb.InfluxDBClient(host=self.myIP, port=self.myPort, username=self.myUsername, password=self.myPassw, database=self.myDefaultDB, timeout=self.myTimeout)
                self.myInfluxClient.write_points(database=dbnameoverride or self.myDefaultDB, points=liste_objets)
                retour = True
            except Exception as e :
                    print("Echec insert InfluxDB : %s" % str(e))
        return retour



if __name__ == '__main__':

    conf = dict()
    try :
        with open('mqttlistener.toml', mode='r', encoding='utf-8', errors='backslashreplace') as the_file:
            conf = pytoml.load(the_file)
    except Exception as EMQ :
        print("ERROR : Config file cannot be read, {:s}".format(str(EMQ)))
        conf = dict()

    print("-- MQTT_Listener is starting --")  # https://pypi.org/project/paho-mqtt/
    print("Config : {:s}".format(str(conf)))


    # --------------- Var glob for process ---------------
    countersLock        = threading.Lock()
    nbMsg_last1m        = collections.Counter()
    nbMsg_last1m_t0     = 0.0
    nbMsg_last3m        = collections.Counter()
    nbMsg_last3m_t0     = 0.0
    nbMsg_last15m       = collections.Counter()
    nbMsg_last15m_t0    = 0.0
    nbMsg_last1h        = collections.Counter()
    nbMsg_last1h_t0     = 0.0
    nbMsg_last24h       = collections.Counter()
    nbMsg_last24h_t0    = 0.0
    nbMsg_last72h       = collections.Counter()
    nbMsg_last72h_t0    = 0.0

    sys_topics = dict()
    ts_systopics = 0.0
    lock_systopics = threading.Lock()

    ts_lastMsg          = dict()
    ts_lastMsg_t0       = 0.0
    lock_ts_lastMsg     = threading.Lock()

    influxLock = threading.Lock()
    influxPtr  = None

    refresh_period      = conf.get('refresh_period_sec') or 29
    refresh_period      = refresh_period if refresh_period > 15 else 15
    conf_json_directory = conf.get('topics_full_hierarchy_by_filters').get('directory_for_json') or "./www"
    conf_hourstoforget  = conf.get('topics_full_hierarchy_by_filters').get('hourstoforget') or 48.0
    conf_deepness_max_level = conf.get('topics_full_hierarchy_by_filters').get('deepness_max_level') or 9

    enable_system_topics_to_influx      = conf.get('system_topics_to_influx').get('enable') or True
    enable_message_rates_to_influx      = conf.get('topics_full_hierarchy_by_filters').get('enable_message_rates_to_influx') or False
    enable_message_rates_to_webserv     = conf.get('topics_full_hierarchy_by_filters').get('enable_message_rates_to_webserv') or False
    enable_last_seen_message_to_influx  = conf.get('topics_full_hierarchy_by_filters').get('enable_last_seen_message_to_influx') or False

    broker_server_host = conf.get('mqtt_server').get('host') or "mosquitto"

    # --------------- The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        global conf, nbMsg_last1m_t0, nbMsg_last3m_t0, nbMsg_last15m_t0, nbMsg_last1h_t0, nbMsg_last24h_t0, nbMsg_last72h_t0
        global enable_system_topics_to_influx, ts_lastMsg_t0
        try :
            ts_lastMsg_t0 = nbMsg_last1m_t0 = nbMsg_last3m_t0 = nbMsg_last15m_t0 = nbMsg_last1h_t0  = nbMsg_last24h_t0 = nbMsg_last72h_t0 = time.time()
            print("MQTT Broker : Connected, Subscribing to topics...")
            topic_ecoute = list()
            lestopics = conf.get('topics_full_hierarchy_by_filters').get('filters_for_topics') or list()
            if enable_system_topics_to_influx :
                lestopics.append("$SYS/#")
            for t2e in lestopics :
                topic_ecoute.append((str(t2e) , 0))
            client.subscribe(topic=topic_ecoute) # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
            print("MQTT Broker : Subscribed to {:d} topics".format(len(topic_ecoute)))
        except Exception as EOC :
            print("Excep MqttConnect : {:s}".format(str(EOC)))

    # --------------- The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        global conf, nbMsg_last1m, nbMsg_last3m, nbMsg_last15m, nbMsg_last1h, nbMsg_last24h, nbMsg_last72h, countersLock
        global sys_topics, enable_system_topics_to_influx, lock_systopics, ts_systopics, enable_message_rates_to_influx, enable_message_rates_to_webserv
        global enable_last_seen_message_to_influx, lock_ts_lastMsg, ts_lastMsg
        try :
            latopic = str(msg.topic)
            if len(latopic) > 0 :

                # ---- System topics ----
                if enable_system_topics_to_influx :
                    if latopic.startswith('$SYS') :
                        try :
                            lock_systopics.acquire(blocking=True, timeout=5)
                            sys_topics[latopic] = float(msg.payload)
                            ts_systopics = time.time()
                            lock_systopics.release()
                        except :
                            try :
                                lock_systopics.acquire(blocking=True, timeout=5)
                                sys_topics[latopic] = str(msg.payload)
                                ts_systopics = time.time()
                                lock_systopics.release()
                            except :
                                pass

                # ---- hierarchy topics / rates ----
                if enable_message_rates_to_influx or enable_message_rates_to_webserv :
                    countersLock.acquire(blocking=True, timeout=5)
                    nbMsg_last1m[latopic]   += 1
                    nbMsg_last3m[latopic]   += 1
                    nbMsg_last15m[latopic]  += 1
                    nbMsg_last1h[latopic]   += 1
                    nbMsg_last24h[latopic]  += 1
                    nbMsg_last72h[latopic]  += 1
                    countersLock.release()

                # ---- last seen message ----
                if enable_last_seen_message_to_influx :
                    lock_ts_lastMsg.acquire(blocking=True, timeout=5)
                    ts_lastMsg[latopic]     = time.time()
                    lock_ts_lastMsg.release()

        except :
            print("ERREUR : Acquire impossible of counters, message missed into %s" %(str(msg.topic)))

    # ---------------
    def add_NbMsgPerTopic_to_influx_list(list_for_influx=None, dicocounters=None, duration_of_count=60.0, datetime_of_count=None) :
        global conf
        RangNiveauMax = 10
        for itopic in dicocounters.keys() :
            obj4idb = dict()
            obj4idb['time'] = pytz.timezone('utc').localize(datetime_of_count).isoformat()
            obj4idb['measurement'] = 'mqttExplo'  # for influx, it means like a table
            obj4idb['tags'] = dict() # tags are indexed
            obj4idb['fields'] = dict() # fields are not indexed : idea is not to do select on them, but to aggregate, fields are the measures.

            obj4idb['tags']['TopicName']     = str(itopic).replace('/', '.')

            topicTree = str(itopic).split('/')
            obj4idb['tags']['TopicLevelLast'] = str(topicTree[-1])

            tniveau = 1
            for niveauN in topicTree :
                tagnom = "TopicLevel{:d}".format(tniveau)
                obj4idb['tags'][tagnom] = str(niveauN)
                tniveau += 1
                if tniveau > RangNiveauMax :
                    break
            obj4idb['tags']['NbLevels'] = tniveau - 1

            obj4idb['fields']['DurationSec'] = float(duration_of_count)
            obj4idb['fields']['NbMessages']  = float(dicocounters.get(itopic) or 0.0)

            obj4idb['fields']['NbMsgPerMin'] = float(60*obj4idb['fields']['NbMessages']/obj4idb['fields']['DurationSec'])
            list_for_influx.append(obj4idb)
    # ---------------
    def add_TimestampLastMsg_to_influx_list(list_for_influx=None, datetime_of_count=None) :
        global conf, ts_lastMsg, conf_hourstoforget, conf_deepness_max_level
        # -- Boucle sur le dict() topic -> timestamp of last message
        secondsMax = 3600 * conf_hourstoforget

        timeNow = time.time()
        cles = ts_lastMsg.keys() # var multihreads
        for itopic2 in cles :
            obj4idb = dict()
            obj4idb['time'] = pytz.timezone('utc').localize(datetime_of_count).isoformat()
            obj4idb['measurement'] = 'mqttLastSeen'
            obj4idb['tags'] = dict()
            obj4idb['fields'] = dict()
            tmpTimeS     = ts_lastMsg.get(itopic2) or 0.0
            tmpTimeDuree = float(timeNow - tmpTimeS)
            tmpTimeDuree = 1.0 if tmpTimeDuree < 1 else tmpTimeDuree

            obj4idb['tags']['TopicName']        = str(itopic2).replace('/', '.')
            topicTree = str(itopic2).split('/')
            obj4idb['tags']['TopicLevelLast'] = str(topicTree[-1])
            tniveau = 1
            for niveauN in topicTree :
                tagnom = "TopicLevel{:d}".format(tniveau)
                obj4idb['tags'][tagnom] = str(niveauN)
                tniveau += 1
                if tniveau > conf_deepness_max_level :
                    break

            obj4idb['fields']['LastSeenAt']   = str(pytz.timezone('Europe/Paris').localize(datetime.datetime.fromtimestamp(tmpTimeS)).isoformat())
            obj4idb['fields']['LastSeenFor']  = tmpTimeDuree
            list_for_influx.append(obj4idb)
    # ---------------
    def add_SystemTopics_to_influx_list(list_for_influx=None, datetime_of_count=None) :
        global conf, sys_topics, broker_server_host, conf_deepness_max_level
        if len(sys_topics) > 0 :
            obj4idb                 = dict()
            obj4idb['time']         = pytz.timezone('utc').localize(datetime_of_count).isoformat()
            obj4idb['measurement']  = 'mqttSystemTopics'
            obj4idb['tags']         = dict()
            obj4idb['tags']['MqttServer'] = broker_server_host
            obj4idb['fields']       = dict()
            cles = sys_topics.keys() # var multihreads
            for itopic2 in cles :
                obj4idb['fields'][str(itopic2).replace('/', '.')] = sys_topics.get(itopic2)
            list_for_influx.append(obj4idb)
    # ---------------
    def json_view_of_topics(topics=None, typevaleur=0) :
        retour = dict()
        for topi in sorted(topics.keys()) :
            if len(topi) > 1 :
                topiL = str(topi).split('/')
                actuel = retour
                for topiUN in topiL[:-1] :
                    if len(topiUN)>0 :
                        level_name = "/{:s}".format(topiUN)
                        if actuel.get(level_name) or None :
                            actuel = actuel.get(level_name)
                        else :
                            actuel[level_name] = dict()
                            actuel = actuel[level_name]

                if typevaleur == 0 :
                    actuel[topiL[-1]] = topics.get(topi)
                elif typevaleur == 1 :
                    actuel[topiL[-1]] = int(topics.get(topi))
                elif typevaleur == 2 :
                    actuel[topiL[-1]] = float(topics.get(topi))

                else :
                    actuel[topiL[-1]] = str(topics.get(topi))
        return retour
    # ---------------
    def json_sunburst_view_of_topics(topics=None, name="Sunburst") :
        retour = dict()
        retour['name']     = name
        retour['children'] = list()
        for topi in sorted(topics.keys()) :
            if len(topi) > 1 :
                topiL = str(topi).split('/')
                actuel = retour
                for topiUN in topiL[:-1] :
                    if len(topiUN)>0 :
                        level_name = "{:s}".format(topiUN)
                        index=0
                        trouver = False
                        for enfant in actuel.get('children') :
                            if enfant.get('name') == level_name :
                                actuel = enfant
                                trouver = True
                                break
                            index+=0
                        if not trouver :
                            newchild = { 'name' : level_name , 'children' : list() }
                            actuel.get('children').append(newchild)
                            actuel = newchild

                newchild2 = { 'name' : topiL[-1] , 'size' : int(topics.get(topi)) }
                actuel.get('children').append(newchild2)
        return retour
    # --------------- remove topics with no message for too long from the list and return { topic : duration_since_last_msg }
    def json_and_clean_last_messages() :
        global conf, ts_lastMsg
        retour = dict()
        keys_to_remove = list()
        heure = time.time()
        secondsMax = conf_hourstoforget * 3600
        tmpDuree = 0.0
        for key, value in ts_lastMsg.items():
            tmpDuree = heure-value
            if tmpDuree >= secondsMax :
                keys_to_remove.append(key)
            else :
                retour[key] = round(tmpDuree, 1)
        if len(keys_to_remove) > 0 :
            try :
                countersLock.acquire(blocking=True, timeout=5)
                for ktrem in keys_to_remove :
                    ts_lastMsg.pop(ktrem)
                countersLock.release()
            except Exception as ESD:
                print("ERROR : Cant remove obsolete topic %s" %(str(ESD)))
        return retour

    # --------------- MONITORING Nb Msg / Min of topics : here counters are flushed . launched in a thread ---------------
    def releve_compteurs() :
        global conf, nbMsg_last1m, nbMsg_last3m, nbMsg_last15m, nbMsg_last1h, nbMsg_last24h, nbMsg_last72h, ts_lastMsg, nbMsg_last1m_t0, nbMsg_last3m_t0, nbMsg_last15m_t0, nbMsg_last1h_t0, nbMsg_last24h_t0, nbMsg_last72h_t0, countersLock
        global influxPtr, influxLock, ts_lastMsg_t0
        global sys_topics, enable_system_topics_to_influx, lock_systopics, ts_systopics, enable_message_rates_to_influx, enable_message_rates_to_webserv
        global enable_last_seen_message_to_influx, lock_ts_lastMsg, ts_lastMsg, conf_json_directory, conf_hourstoforget

        messages4idb = list()
        Counter2Process = None
        CounterDuration = 0.0
        CounterDatetime = None

        # -------------------- System topics --------------------
        if enable_system_topics_to_influx:
            CounterDatetime1 = datetime.datetime.fromtimestamp(ts_systopics)
            add_SystemTopics_to_influx_list(list_for_influx=messages4idb, datetime_of_count=CounterDatetime1)
            lock_systopics.acquire(blocking=True, timeout=5)
            sys_topics = dict()
            lock_systopics.release()

        # -------------------- hierarchy topics / rates -> Influx --------------------
        if enable_message_rates_to_influx :
            try :
                countersLock.acquire(blocking=True, timeout=5)
                newTime         = time.time()
                CounterDuration = abs(newTime - nbMsg_last1m_t0)
                Counter2Process = nbMsg_last1m
                nbMsg_last1m    = collections.Counter()
                nbMsg_last1m_t0 = newTime
                countersLock.release()
                CounterDatetime = datetime.datetime.fromtimestamp(newTime)
            except :
                print("ERROR : Acquire 1 impossible of timestep")
            add_NbMsgPerTopic_to_influx_list(list_for_influx=messages4idb, dicocounters=Counter2Process, duration_of_count=CounterDuration, datetime_of_count=CounterDatetime)

        # -------------------- hierarchy topics / rates -> Sunburst --------------------
        if enable_message_rates_to_webserv :
            # ---- 3 min
            if time.time() - nbMsg_last3m_t0 >= (60 * 3) - 3:
                try:
                    countersLock.acquire(blocking=True, timeout=5)
                    newTime         = time.time()
                    CounterDuration = abs(newTime - nbMsg_last3m_t0)
                    Counter2Process = nbMsg_last3m
                    nbMsg_last3m    = collections.Counter()
                    nbMsg_last3m_t0 = newTime
                    countersLock.release()
                    CounterDatetime = datetime.datetime.fromtimestamp(newTime)

                    jsonobj = {'description': 'MQTT Nb Messages in {:3.1f} seconds'.format(CounterDuration), 'timestamp': pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds'), 'data': json_view_of_topics(topics=Counter2Process, typevaleur=1) }
                    # -- save json file for humans
                    fichier  = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-last3min-nbmsg.json")
                    json.dump(obj=jsonobj, fp=fichier.open(mode="w"))
                    # -- create and save json for sunburst
                    jsonobj3 = json_sunburst_view_of_topics(topics=Counter2Process, name="mqtt-3min {:s}".format(pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds')))
                    fichier  = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-last3min-sunburst.json")
                    json.dump(obj=jsonobj3, fp=fichier.open(mode="w"))
                except:
                    print("ERROR : Acquire 3 impossible of timestep")

            # --- 15 min
            if time.time() - nbMsg_last15m_t0 >= (60 * 15) - 1:
                try:
                    countersLock.acquire(blocking=True, timeout=5)
                    newTime             = time.time()
                    CounterDuration     = abs(newTime - nbMsg_last15m_t0)
                    Counter2Process     = nbMsg_last15m
                    nbMsg_last15m       = collections.Counter()
                    nbMsg_last15m_t0    = newTime
                    countersLock.release()
                    CounterDatetime     = datetime.datetime.fromtimestamp(newTime)

                    jsonobj = {'description': 'MQTT Nb Messages in {:3.1f} seconds'.format(CounterDuration), 'timestamp': pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds'), 'data': json_view_of_topics(topics=Counter2Process, typevaleur=1)}
                    # -- save json file for humans
                    fichier  = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-last15min-nbmsg.json")
                    json.dump(obj=jsonobj, fp=fichier.open(mode="w"))
                    # -- create and save json for sunburst
                    jsonobj3 = json_sunburst_view_of_topics(topics=Counter2Process, name="mqtt-15min {:s}".format(pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds')))
                    fichier  = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-last15min-sunburst.json")
                    json.dump(obj=jsonobj3, fp=fichier.open(mode="w"))
                except:
                    print("ERROR : Acquire 15 impossible of timestep")

            # --- 60 min
            if time.time() - nbMsg_last1h_t0 >= (60 * 60) - 2:
                try:
                    countersLock.acquire(blocking=True, timeout=5)
                    newTime         = time.time()
                    CounterDuration = abs(newTime - nbMsg_last1h_t0)
                    Counter2Process = nbMsg_last1h
                    nbMsg_last1h    = collections.Counter()
                    nbMsg_last1h_t0 = newTime
                    countersLock.release()
                    CounterDatetime = datetime.datetime.fromtimestamp(newTime)

                    jsonobj = {'description': 'MQTT Nb Messages in {:3.1f} seconds'.format(CounterDuration), 'timestamp': pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds'), 'data': json_view_of_topics(topics=Counter2Process, typevaleur=1)}
                    # -- save json file for humans
                    fichier  = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-last1h-nbmsg.json")
                    json.dump(obj=jsonobj, fp=fichier.open(mode="w"))
                    # -- create and save json for sunburst
                    jsonobj3 = json_sunburst_view_of_topics(topics=Counter2Process, name="mqtt-1h {:s}".format(pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds')))
                    fichier  = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-last1h-sunburst.json")
                    json.dump(obj=jsonobj3, fp=fichier.open(mode="w"))
                except:
                    print("ERROR : Acquire 1h impossible of timestep")
                    
            # --- 24h
            if time.time() - nbMsg_last24h_t0 >= 24 * 3600 - 1:
                try:
                    countersLock.acquire(blocking=True, timeout=5)
                    newTime          = time.time()
                    CounterDuration  = abs(newTime - nbMsg_last24h_t0)
                    Counter2Process  = nbMsg_last24h
                    nbMsg_last24h    = collections.Counter()
                    nbMsg_last24h_t0 = newTime
                    countersLock.release()
                    CounterDatetime  = datetime.datetime.fromtimestamp(newTime)

                    jsonobj = {'description': 'MQTT Nb Messages in {:3.1f} hours'.format(CounterDuration / 3600), 'timestamp': pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds'), 'data': json_view_of_topics(topics=Counter2Process, typevaleur=1)}
                    # -- save json file for humans
                    fichier  = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-last24h-nbmsg.json")
                    json.dump(obj=jsonobj, fp=fichier.open(mode="w"))
                    # -- create and save json for sunburst
                    jsonobj3 = json_sunburst_view_of_topics(topics=Counter2Process, name="mqtt-24h {:s}".format(pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds')))
                    fichier  = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-last24h-sunburst.json")
                    json.dump(obj=jsonobj3, fp=fichier.open(mode="w"))
                except:
                    print("ERROR : Acquire 24h impossible of timestep")

            # --- 72h
            if time.time() - nbMsg_last72h_t0 >= 72 * 3600 - 1:
                try:
                    countersLock.acquire(blocking=True, timeout=5)
                    newTime          = time.time()
                    CounterDuration  = abs(newTime - nbMsg_last72h_t0)
                    Counter2Process  = nbMsg_last72h
                    nbMsg_last72h    = collections.Counter()
                    nbMsg_last72h_t0 = newTime
                    countersLock.release()
                    CounterDatetime  = datetime.datetime.fromtimestamp(newTime)

                    jsonobj = {'description': 'MQTT Nb Messages in {:3.1f} hours'.format(CounterDuration / 3600), 'timestamp': pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds'), 'data': json_view_of_topics(topics=Counter2Process, typevaleur=1)}
                    # -- save json file for humans
                    fichier = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-last72h-nbmsg.json")
                    json.dump(obj=jsonobj, fp=fichier.open(mode="w"))
                    # -- create and save json for sunburst
                    jsonobj3 = json_sunburst_view_of_topics(topics=Counter2Process, name="mqtt-72h {:s}".format(pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds')))
                    fichier = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-last72h-sunburst.json")
                    json.dump(obj=jsonobj3, fp=fichier.open(mode="w"))
                except:
                    print("ERROR : Acquire 72h impossible of timestep")

        # -------------------- last seen message --------------------
        if enable_last_seen_message_to_influx :
            if time.time() - ts_lastMsg_t0 >= (15 * 60) :
                # remove topics with no message for too long from the list and return { topic : duration_since_last_msg }
                duree_lastMsg = json_and_clean_last_messages()
                ts_lastMsg_t0 = time.time()

                # ---- Build and send to InfluxDB
                CounterDatetime = datetime.datetime.fromtimestamp(ts_lastMsg_t0)
                add_TimestampLastMsg_to_influx_list(list_for_influx=messages4idb, datetime_of_count=CounterDatetime)

                if enable_message_rates_to_webserv :
                    jsonobj2 = {'description': 'MQTT seconds since last message'.format(CounterDuration), 'timestamp': pytz.timezone('Europe/Paris').localize(CounterDatetime).isoformat(sep=' ', timespec='seconds'), 'data': json_view_of_topics(topics=duree_lastMsg, typevaleur=2)}
                    fichier  = pathlib.Path(conf_json_directory) / pathlib.Path("mqtt-time-since-last-msg.json")
                    json.dump(obj=jsonobj2, fp=fichier.open(mode="w"))


        # -------------------- Flush to InfluxDB --------------------
        if len(messages4idb)> 0 :
            # --- Create if needed
            if not influxPtr :
                influxPtr = InfluxPush(params=conf.get('influxdb'))
            # ---- Send to Influx
            try :
                influxLock.acquire(blocking=True, timeout=6)
                try :
                    if not influxPtr.insertInIDB(liste_objets=messages4idb) :
                        print("One MQTT monitoring measure not sent into influx")
                except :
                    pass
                influxLock.release()
            except :
                print("One MQTT monitoring measure not sent into influx Exception liee au lock")

    # --------------- MAIN ---------------
    encore = True
    while encore :
        try :
            Leclient            = paho.mqtt.client.Client()
            Leclient.on_connect = on_connect
            Leclient.on_message = on_message
            print("MQTT Broker : Connecting...")
            Leclient.connect(host=broker_server_host,
                             port=conf.get('mqtt_server').get('port') or 8883,
                             keepalive=conf.get('mqtt_server').get('keepalive') or 30,
                             bind_address="")
        except Exception as MQC :
            print("Cannot connect to MQTT, sleeping 60s before retry : {:s}".format(str(MQC)))
            time.sleep(60)
        else :
            try :
                Leclient.loop_start() # Leclient.loop_forever()
                encore2 = True
                while encore2 :
                    time.sleep(refresh_period)
                    releve_compteurs()
                print("MQTT Broker : Disconnecting...")
                Leclient.loop_stop()
            except Exception as MQL :
                print("Excep during mqtt listening : {:s}, sleeping 60s before reconnection retry".format(str(MQL)))
                time.sleep(60)
    print("-- MQTT_Listener is finished -")


