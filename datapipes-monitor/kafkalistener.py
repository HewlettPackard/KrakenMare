# coding=utf-8
import datetime
import pytz
import kafka
import pytoml
import time

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
        with open('kafkalistener.toml', mode='r', encoding='utf-8', errors='backslashreplace') as the_file:
            conf = pytoml.load(the_file)
    except :
        conf = dict()

    print("-- KAFKA_Listener is starting --")
    print("Config : {:s}".format(str(conf)))

    topics_offsets_at_t0 = dict()
    topics_offsets_at_t0_timestamp = pytz.timezone('utc').localize(datetime.datetime.now())
    topics_offsets_at_t1 = dict()
    topics_offsets_at_t1_timestamp = pytz.timezone('utc').localize(datetime.datetime.now())
    topics_categories = {}
    ts_filewritten = 0.0
    influx_conf = conf.get('influxdb')
    influx_client = None
    dont_send_first_measures = 2

    def get_offsets_from_kafka() :
        offsets_per_partition = dict()
        offsets_max_per_topic = dict()

        all_partitions_with_end_offsets = None
        try:
            consumer = kafka.KafkaConsumer(api_version=(0, 10, 1),
                                           bootstrap_servers=conf.get('kafka_server').get('hosts') or ["127.0.0.1:9092"],
                                           client_id=conf.get('kafka_server').get('agent_id') or 'datapipesmonitor',
                                           group_id=conf.get('kafka_server').get('agent_grpid') or 'datapipesmonitor',
                                           auto_offset_reset='latest')

            list_topics = consumer.topics()
            all_partitions = list()
            for itopic in list_topics:
                set_partitions = consumer.partitions_for_topic(itopic)
                if set_partitions is not None:
                    for ipart in set_partitions:
                        all_partitions.append(kafka.TopicPartition(itopic, ipart))
            all_partitions_with_end_offsets = consumer.end_offsets(all_partitions)

            consumer.close()
            del consumer
        except Exception as MQC:
            print("Cannot connect to Kafka : {:s}".format(str(MQC)))
            all_partitions_with_end_offsets = None

        if all_partitions_with_end_offsets :
            for pkey in all_partitions_with_end_offsets.keys():
                topicname = pkey.topic
                partitionIndex = pkey.partition
                endoffset = all_partitions_with_end_offsets.get(pkey)
                if not offsets_per_partition.get(topicname):
                    offsets_per_partition[topicname] = dict()
                    offsets_max_per_topic[topicname] = int(0)
                offsets_per_partition[topicname][partitionIndex] = endoffset
                offsets_max_per_topic[topicname] = endoffset if endoffset > offsets_max_per_topic[topicname] else offsets_max_per_topic[topicname]
        return offsets_per_partition, offsets_max_per_topic


    refresh_period = conf.get('refresh_period_sec') or 45

    # ----- Get Kafka offsets at t0
    encore = True
    while encore :
        offsets_partitions_t0, offsets_topics_t0 = get_offsets_from_kafka()
        if len(offsets_partitions_t0) > 0 or len(offsets_topics_t0) > 0 :
            encore = False
        else :
            print("Initial Kafka connection problem : sleep and loop")
            time.sleep(refresh_period)

    ts_t0 = pytz.timezone('utc').localize(datetime.datetime.now())
    encore = True
    while encore :
        time.sleep(refresh_period)

        # ----- Get Kafka offsets at t1
        offsets_partitions_t1, offsets_topics_t1 = get_offsets_from_kafka()
        ts_t1 = pytz.timezone('utc').localize(datetime.datetime.now())

        # ----- Calculate Delta of offsets between t1 & t0
        delta_offsets_partitions = dict()
        delta_offsets_max_per_topic = dict()
        for letopic in offsets_partitions_t1.keys() :
            if not delta_offsets_max_per_topic.get(letopic) :
                delta_offsets_max_per_topic[letopic] = int(0)

            value_max_for_t0 = offsets_topics_t0.get(letopic) or int(0)
            delta_offsets_max_per_topic[letopic] = offsets_topics_t1.get(letopic) - value_max_for_t0
            for lapartition in offsets_partitions_t1.get(letopic).keys() :
                value_for_t0 = (offsets_partitions_t0.get(letopic) or dict()).get(lapartition) or int(0)
                if not delta_offsets_partitions.get(letopic) :
                    delta_offsets_partitions[letopic] = dict()
                delta_offsets_partitions[letopic][lapartition] = offsets_partitions_t1.get(letopic).get(lapartition) - value_for_t0

        # ----- Preparing json object
        delta_sec = float((ts_t1-ts_t0).seconds)+ (ts_t1-ts_t0).microseconds/1000000
        metrics_to_insert = list()
        ts_iso = ts_t1.isoformat()
        if delta_sec > 1 :
            for ftopic2 in delta_offsets_max_per_topic.keys() :
                item = dict()
                item['time']                  = ts_iso
                item['measurement']           = 'kafkaTopics'
                item['tags']                  = dict()
                item['tags']['topic']         = ftopic2
                item['fields']                 = dict()
                item['fields']['end_offset']   = offsets_topics_t1.get(ftopic2) or int(0)
                deltaoff = delta_offsets_max_per_topic.get(ftopic2) or int(0)
                item['fields']['delta_offset'] = deltaoff
                item['fields']['msg_per_min']  = float(60*deltaoff/delta_sec)
                metrics_to_insert.append(item)

            for ftopic2 in delta_offsets_partitions.keys() :
                item = dict()
                item['time']          = ts_iso
                item['measurement']   = 'kafkaPartitions'
                item['tags']          = dict()
                item['tags']['topic'] = ftopic2
                item['fields']        = dict()

                for fparti in delta_offsets_partitions.get(ftopic2).keys() :
                    item2 = dict(item)
                    item2['tags']['partition'] = str(fparti)
                    item2['fields']['end_offset']   = offsets_partitions_t1.get(ftopic2).get(fparti) or int(0)
                    deltaoff = delta_offsets_partitions.get(ftopic2).get(fparti) or int(0)
                    item2['fields']['delta_offset'] = deltaoff
                    item2['fields']['msg_per_min']  = float(60*deltaoff/delta_sec)
                    metrics_to_insert.append(item2)

        # ----- Sending to influx
        if dont_send_first_measures > 0 :
            dont_send_first_measures -= 1
        elif len(metrics_to_insert) > 0 :
            influx_client = InfluxPush(params=influx_conf)
            if not influx_client.insertInIDB(liste_objets=metrics_to_insert) :
                print("One KAFKA monitoring measure not sent into influx")
            # else :
            #     print('Pushed %d measures in InfluxDB' % len(metrics_to_insert))
        else :
            print("Nothing from KAFKA monitoring to send to influx")

        # ----- t1 is now t0 for next round
        ts_t0 = ts_t1
        offsets_partitions_t0 = offsets_partitions_t1
        offsets_topics_t0     = offsets_topics_t1

    print("-- KAFKA_Listener is finished -")

