#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <mosquitto.h>
#include <getopt.h>
#include <unistd.h>
//basename
#include <libgen.h>
//JSON C Library
#include <jansson.h>
#include <uuid/uuid.h>

//global variable to know if agent is registered
int registered = 0;
char my_name[128];
char my_uuid[128];
int my_id = -1;

typedef struct s_options {
  char* client_id;
  char* host;
  int port;
  char* msg;
  char* topic;
  int keepalive;
  int repeat;
  int debug;
} s_options;
s_options options;

void options_default(void)
{
  options.client_id = NULL;
  options.host = "mosquitto";
  options.port = 1883;
  options.topic = "default_mousttic_topic";
  options.msg = "Default compiled-in 'Hello World' from mousttic...";
  options.keepalive = 60;
  options.repeat = -1;
  options.debug = 0;
}

void print_usage(char ** argv)
{
  printf("\n");
  printf("%s -h | [-i mqtt_client_id] [-s host] [-p port] [-m msg] "
      "[-k keepalive] [-t topic] [ -d debug ] \n", basename(strdup(argv[0])));
  printf("\n");
  printf("-h: display this help\n");
  printf("-i: mqtt client id (default random)\n");
  printf("-s: target host (default localhost)\n");
  printf("-p: target port (default 1883)\n");
  printf("-m: message to keep repeating...\n");
  printf("-k: connection keepalive\n");
  printf("-t: topic to publish to\n");
  printf("-d: debug MQTT messages\n");
  printf("-r: repeat message number(-1=indefinitely)\n");
  printf("\n");
  printf("\n");
}

int parse_options(int argc, char **argv) {
  int retval;
  int index;
  char * optstring = "hi:s:p:m:k:t:r:d";
  struct option longopts[] = {
      /* name   has_arg  flag  val*/
      { "help",       0, NULL, 'h' },
      { "client_id",  1, NULL, 'i' },
      { "host",       1, NULL, 's' },
      { "port",       1, NULL, 'p' },
      { "message",    1, NULL, 'm' },
      { "keepalive",  1, NULL, 'k' },
      { "topic",      1, NULL, 't' },
      { "repeat",     1, NULL, 'r' },
      { "debug",      0, NULL, 'd' },
      { NULL,         0, NULL, 0 }
  };

  options_default();

  while ((retval = getopt_long(argc, argv, optstring, longopts, &index)) != -1) {
    switch (retval) {
    case 'h':
      print_usage(argv);
      exit(0);
      break;
    case 'i':
      options.client_id = strdup(optarg);
      break;
    case 's':
      options.host = strdup(optarg);
      break;
    case 'p':
      options.port = atoi(optarg);
      break;
    case 'm':
      options.msg = strdup(optarg);
      break;
    case 'k':
      options.keepalive = atoi(optarg);
      break;
    case 't':
      options.topic = strdup(optarg);
      break;
    case 'r':
      options.repeat = atoi(optarg);
      break;
    case 'd':
      options.debug = 1;
      break;
    default:
      print_usage(argv);
      exit(1);
    }
  }
  return optind;
}

json_t *load_json(const char *text) {
  json_t *root;
  json_error_t error;

  root = json_loads(text, 0, &error);

  if (root) {
    return root;
  } else {
    fprintf(stderr, "json error on line %d: %s\n", error.line, error.text);
    return (json_t *) 0;
  }
}

char* text_to_json(const char* uuid, const char* name, const char* mymsg) {

  char* s = NULL;

  json_t *root = json_object();

  json_object_set_new(root, "uuid", json_string(uuid));
  json_object_set_new(root, "name", json_string(name));
  json_object_set_new(root, "message", json_string(mymsg));

  s = json_dumps(root, 0);

  return s;
}

void parse_me(const char* msg)
{
  json_t* root = NULL;
  char* registration_name;
  char* registration_uuid;
  int registration_id = -1;

  if ((root = load_json(msg)) != 0) {
    const char *key = NULL;
    json_t *value = NULL;

    json_object_foreach(root, key, value) {
      if (strncmp(key, "name", strlen(key)) == 0) {
        if (json_typeof(value) == JSON_STRING) {
          fprintf(stdout, "registration name is <%s>\n", json_string_value(value));
          fflush(stdout);
          registration_name = strdup(json_string_value(value));
        } else {
          fprintf(stderr, "name is not a string, ignoring value\n");
          fflush(stderr);
        }
      } else if (strncmp(key, "uuid", strlen(key)) == 0) {
        if (json_typeof(value) == JSON_STRING) {
          fprintf(stdout, "registration uuid is <%s>\n", json_string_value(value));
          fflush(stdout);
          registration_uuid = strdup(json_string_value(value));
        } else {
          fprintf(stderr, "uuid is not a string, ignoring value\n");
          fflush(stderr);
        }
      } else if (strncmp(key, "id", strlen(key)) == 0) {
        if (json_typeof(value) == JSON_INTEGER) {
          fprintf(stdout, "registration id is <%d>\n", (int) json_integer_value(value));
          fflush(stdout);
          registration_id = json_integer_value(value);
        } else {
          fprintf(stderr, "ignoring key: <%s>\n", key);
          fflush(stderr);
        }
      }
    }

    if (strncmp(registration_uuid, my_uuid, strlen(my_uuid)) == 0) {
      sprintf(my_name, "%s", registration_name);
      sprintf(my_uuid, "%s", registration_uuid);
      my_id = registration_id;
      fprintf(stdout, "registered with name '%s', uuid '%s' and id '%d'\n", registration_name, registration_uuid, registration_id);
      fflush(stdout);
      registered = 1;
    } else {
      fprintf(stdout, "ignoring message not for us: %s != %s\n", my_uuid, registration_uuid);
      fflush(stdout);
    }
  }
}

void my_message_callback(struct mosquitto *mosq, void *userdata, const struct mosquitto_message *message)
{
  if (message->payloadlen) {
    printf("topic:<%s> payload:<%s>\n", message->topic, (char*) message->payload);
    parse_me((char*) message->payload);
    //when registered... now start publishing...
    if (registered) {
      //
    }
  } else {
    printf("topic:<%s> payload:NULL\n", message->topic);
  }
  fflush(stdout);
}

void my_connect_callback(struct mosquitto *mosq, void *userdata, int result)
{
  if (!result) {
    /* Subscribe to broker information topics on successful connect. */
    mosquitto_subscribe(mosq, NULL, "registration-result", 2);
  } else {
    fprintf(stderr, "Connect failed\n");
  }
}

void my_subscribe_callback(struct mosquitto *mosq, void *userdata, int mid, int qos_count, const int *granted_qos)
{
  int i;
  printf("Subscribed (mid: %d): qos: %d", mid, granted_qos[0]);
  for (i = 1; i < qos_count; i++) {
    printf(", %d", granted_qos[i]);
  }
  printf("\n");
}

void my_log_callback(struct mosquitto *mosq, void *userdata, int level, const char *str)
{
  /* Pring all log messages regardless of level. */
  if (options.debug)
    printf("-- log --:%s\n", str);
}

int main(int argc, char *argv[])
{
  bool clean_session = true;
  struct mosquitto *mosq = NULL;

  parse_options(argc, argv);

  printf("mqtt broker target is %s\n", options.host);
  printf("mosquitto version = %d \n", mosquitto_lib_version(NULL, NULL, NULL));
  fflush(stdout);

  mosquitto_lib_init();
  mosq = mosquitto_new(NULL, clean_session, NULL);

  if (!mosq) {
    fprintf(stderr, "%s", strerror(errno));
    return 1;
  }

  while (mosquitto_connect(mosq, options.host, options.port, options.keepalive)) {
    fprintf(stderr, "unable to connect. retrying in one second \n");
    sleep(1);
  }

  if (mosquitto_subscribe(mosq, NULL, "registration-result", 2) != MOSQ_ERR_SUCCESS) {
    fprintf(stderr, "failed subscribing... retrying in one second \n");
    exit(1);
  }

  //send a UUID name and remember it.
  uuid_t uuid;
  char uuid_str[37]; //36 + 1
  uuid_generate_random(uuid);
  uuid_unparse_lower(uuid, uuid_str);

  sprintf(my_uuid, "%s", uuid_str);
  sprintf(my_name, "mousttic-simulator");

  char msg[512];
  sprintf(msg, "{\"name\": \"%s\", \"uuid\": \"%s\"}", my_name, my_uuid);
  fprintf(stdout, "msg=%s\n", msg);
  fflush(stdout);

  //Registration request consist in sending our name
  //QOs is 2 to guarantee exactly one registration request is sent.
  int msg_id = 1;
  if (mosquitto_publish(mosq, &msg_id, "registration-request/mousttic", strlen(msg), msg, 2, true) != MOSQ_ERR_SUCCESS) {
    fprintf(stderr, "failed publishing registration-request, retrying in one second \n");
    exit(1);
  }

  mosquitto_log_callback_set(mosq, my_log_callback);
  mosquitto_message_callback_set(mosq, my_message_callback);

  while (!registered) {
    mosquitto_loop(mosq, -1, 1);
    sleep(1);
  }

  char* json_msg = text_to_json(my_uuid, my_name, options.msg);

  msg_id = 0;
  while ((options.repeat == -1) || (msg_id < options.repeat)) {
    msg_id++;
    int err = 0;
    if ((err = mosquitto_publish(mosq, &msg_id, options.topic, strlen(json_msg), json_msg, 0, false)) != MOSQ_ERR_SUCCESS) {
      fprintf(stderr, "mosquitto_publish error: %s \n", mosquitto_strerror(err));
    }
    fprintf(stdout, "sent to <%s> msg:%d <%s>\n", options.topic, msg_id, json_msg);
    fflush(stdout);
    sleep(1);
  }

  mosquitto_destroy(mosq);
  mosquitto_lib_cleanup();
  return 0;
}
