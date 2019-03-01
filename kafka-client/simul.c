#include <stdio.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>
#include <rdkafka.h>
//json generation
#include <jansson.h>

static int run = 1;

/**
 * @brief Message delivery report callback.
 *
 * This callback is called exactly once per message, indicating if
 * the message was succesfully delivered
 * (rkmessage->err == RD_KAFKA_RESP_ERR_NO_ERROR) or permanently
 * failed delivery (rkmessage->err != RD_KAFKA_RESP_ERR_NO_ERROR).
 *
 * The callback is triggered from rd_kafka_poll() and executes on
 * the application's thread.
 */
static void dr_msg_cb (rd_kafka_t *rk,
                       const rd_kafka_message_t *rkmessage, void *opaque) {
  if (rkmessage->err)
    fprintf(stderr, "%% Message delivery failed: %s\n",
	    rd_kafka_err2str(rkmessage->err));
  else
    fprintf(stderr,
	    "%% Message delivered (%zd bytes, "
	    "partition %"PRId32")\n",
	    rkmessage->len, rkmessage->partition);

  /* The rkmessage is destroyed automatically by librdkafka */
}



char* text_to_json(const char* mymsg) {

  char* s = NULL;
  
  json_t *root = json_object();
    
  json_object_set_new( root, "message" , json_string(mymsg));
  //kafka-connect is sending all messages from the 'fabric' topic into the perfquery influxDB table
  //provided they have a GUID. see connect.influx.kcql into configure-influxdb.sh
  json_object_set_new( root, "GUID" , json_string("0xdeadbeef"));
  
  s = json_dumps(root, 0);

  return s;
}



int main (int argc, char **argv) {
  rd_kafka_t *rk;         /* Producer instance handle */
  rd_kafka_topic_t *rkt;  /* Topic object */
  rd_kafka_conf_t *conf;  /* Temporary configuration object */
  char errstr[512];       /* librdkafka API error reporting buffer */
  const char *brokers;    /* Argument: broker list */
  const char *topic;      /* Argument: topic to produce to */
  char *msg = NULL ;
	
  /*
   * Argument validation
   */
  if (argc != 4) {
    fprintf(stderr, "%% Usage: %s <broker> <topic> <msg>\n", argv[0]);
    return 1;
  }

  brokers = argv[1];
  topic   = argv[2];
  msg     = argv[3];

  /*
   * Create Kafka client configuration place-holder
   */
  conf = rd_kafka_conf_new();

  /* Set bootstrap broker(s) as a comma-separated list of
   * host or host:port (default port 9092).
   * librdkafka will use the bootstrap brokers to acquire the full
   * set of brokers from the cluster. */
  if (rd_kafka_conf_set(conf, "bootstrap.servers", brokers,
			errstr, sizeof(errstr)) != RD_KAFKA_CONF_OK) {
    fprintf(stderr, "%s\n", errstr);
    return 1;
  }

  /* Set the delivery report callback.
   * This callback will be called once per message to inform
   * the application if delivery succeeded or failed.
   * See dr_msg_cb() above. */
  rd_kafka_conf_set_dr_msg_cb(conf, dr_msg_cb);

  /*
   * Create producer instance.
   *
   * NOTE: rd_kafka_new() takes ownership of the conf object
   *       and the application must not reference it again after
   *       this call.
   */
  rk = rd_kafka_new(RD_KAFKA_PRODUCER, conf, errstr, sizeof(errstr));
  if (!rk) {
    fprintf(stderr,
	    "%% Failed to create new producer: %s\n", errstr);
    return 1;
  }

  /* Create topic object that will be reused for each message
   * produced.
   *
   * Both the producer instance (rd_kafka_t) and topic objects (topic_t)
   * are long-lived objects that should be reused as much as possible.
   */
  rkt = rd_kafka_topic_new(rk, topic, NULL);
  if (!rkt) {
    fprintf(stderr, "%% Failed to create topic object: %s\n",
	    rd_kafka_err2str(rd_kafka_last_error()));
    rd_kafka_destroy(rk);
    return 1;
  }

  
  char* json_msg = NULL;
	
  while ( run && msg ) {
	   
    json_msg = text_to_json(msg);
	  
    size_t len = strlen(json_msg);
	  
    if (json_msg[len-1] == '\n') /* Remove newline */
      json_msg[--len] = '\0';

    if (len == 0) {
      /* Empty line: only serve delivery reports */
      rd_kafka_poll(rk, 0/*non-blocking */);
      continue;
    }

    /*
     * Send/Produce message.
     * This is an asynchronous call, on success it will only
     * enqueue the message on the internal producer queue.
     * The actual delivery attempts to the broker are handled
     * by background threads.
     * The previously registered delivery report callback
     * (dr_msg_cb) is used to signal back to the application
     * when the message has been delivered (or failed).
     */
  retry:
    if (rd_kafka_produce(
			 /* Topic object */
			 rkt,
			 /* Use builtin partitioner to select partition*/
			 RD_KAFKA_PARTITION_UA,
			 /* Make a copy of the payload. */
			 RD_KAFKA_MSG_F_COPY,
			 /* Message payload (value) and length */
			 json_msg, len,
			 /* Optional key and its length */
			 NULL, 0,
			 /* Message opaque, provided in
			  * delivery report callback as
			  * msg_opaque. */
			 NULL) == -1) {
      /**
       * Failed to *enqueue* message for producing.
       */
      fprintf(stderr,
	      "%% Failed to produce to topic %s: %s\n",
	      rd_kafka_topic_name(rkt),
	      rd_kafka_err2str(rd_kafka_last_error()));

      /* Poll to handle delivery reports */
      if (rd_kafka_last_error() ==
	  RD_KAFKA_RESP_ERR__QUEUE_FULL) {
	/* If the internal queue is full, wait for
	 * messages to be delivered and then retry.
	 * The internal queue represents both
	 * messages to be sent and messages that have
	 * been sent or failed, awaiting their
	 * delivery report callback to be called.
	 *
	 * The internal queue is limited by the
	 * configuration property
	 * queue.buffering.max.messages */
	rd_kafka_poll(rk, 1000/*block for max 1000ms*/);
	goto retry;
      }
    } else {
      fprintf(stderr, "%% Enqueued message (%zd bytes) "
	      "for topic %s\n",
	      len, rd_kafka_topic_name(rkt));
    }


    /* A producer application should continually serve
     * the delivery report queue by calling rd_kafka_poll()
     * at frequent intervals.
     * Either put the poll call in your main loop, or in a
     * dedicated thread, or call it after every
     * rd_kafka_produce() call.
     * Just make sure that rd_kafka_poll() is still called
     * during periods where you are not producing any messages
     * to make sure previously produced messages have their
     * delivery report callback served (and any other callbacks
     * you register). */
    rd_kafka_poll(rk, 0/*non-blocking*/);
    sleep(1);
  }


  /* Wait for final messages to be delivered or fail.
   * rd_kafka_flush() is an abstraction over rd_kafka_poll() which
   * waits for all messages to be delivered. */
  fprintf(stderr, "%% Flushing final messages..\n");
  rd_kafka_flush(rk, 10*1000 /* wait for max 10 seconds */);

  /* Destroy topic object */
  rd_kafka_topic_destroy(rkt);

  /* Destroy the producer instance */
  rd_kafka_destroy(rk);

  return 0;
}
