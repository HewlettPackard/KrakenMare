#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
//MQTT library
#include <mosquitto.h>
#include <getopt.h>
#include <libgen.h>
//JSON C library
#include <jansson.h>


typedef struct s_options {
  char* client_id;
  char* host;
  int port;
  char* msg;
  char* topic;
  int keepalive;
  int repeat;
} s_options;
s_options options;

void options_default(void)
{
  options.client_id=NULL;
  options.host="localhost";
  options.port=1883;
  options.topic="default_mousttic_topic";
  options.msg="Default compiled-in 'Hello World' from mousttic...";
  options.keepalive=60;
  options.repeat=-1;
}

void print_usage(char ** argv)
{
  printf("\n");
  printf("%s -h | [-i mqtt_client_id] [-s host] [-p port] [-m msg] " \
	 "[-k keepalive] [-t topic] \n",basename(strdup(argv[0])));
  printf("\n");
  printf("-h: display this help\n");
  printf("-i: mqtt client id (default random)\n");
  printf("-s: target host (default localhost)\n");
  printf("-p: target port (default 1883)\n");
  printf("-m: message to keep repeating...\n");
  printf("-k: connection keepalive\n");
  printf("-t: topic to publish to\n");
  printf("-r: repeat message number(-1=indefinitely)\n");
  printf("\n");
  printf("\n");
}

int parse_options(int argc,char **argv) {
  int retval;
  int index;
  char * optstring = "hi:s:p:m:k:t:r:";
  struct option longopts [] = {
    /* name                   has_arg        flag    val*/
    { "help"	       	        ,	0,	NULL,   'h'},
    { "client_id"       	,	1,	NULL,	'i'},
    { "host"      		,	1,	NULL,	's'},
    { "port"     		,	1,	NULL,	'p'},
    { "message"		        ,	1,	NULL,	'm'},
    { "keepalive"	        ,	1,	NULL,	'k'},
    { "topic"	                ,	1,	NULL,	't'},
    { "repeat"	                ,	1,	NULL,	'r'},
    { NULL			,	0,	NULL,    0 }
  };
  
  options_default();
  
  while ((retval = getopt_long(argc,argv,optstring,longopts,&index)) != -1) {
    switch (retval) {
    case 'h':
      print_usage(argv); exit(0);
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
    default:
      print_usage(argv);
      exit(1);
    }
  }
  return optind;
}

char* text_to_json(const char* mymsg) {

  char* s = NULL;
  
  json_t *root = json_object();
    
  json_object_set_new( root, "message" , json_string(mymsg));
  
  s = json_dumps(root, 0);

  return s;
}

int main(int argc, char *argv[]) {
  bool clean_session = true;
  struct mosquitto *mosq = NULL;

  parse_options(argc,argv);

  printf("host target is %s\n",options.host);
  printf("mosquitto version = %d \n",mosquitto_lib_version(NULL,NULL,NULL));
	 
  mosquitto_lib_init();

  mosq = mosquitto_new(options.client_id, clean_session, NULL);
  if(!mosq){
    fprintf(stderr, "%s",strerror(errno));
    return 1;
  }

  while (mosquitto_connect(mosq, options.host, options.port, options.keepalive)) {
    fprintf(stderr, "unable to connect.\n");
    sleep(1);
  }

  int msg_id=0;

  char* json_msg = text_to_json(options.msg);

  while((options.repeat==-1)||(msg_id<options.repeat)) {
    msg_id++;
    if (mosquitto_publish(mosq,&msg_id,options.topic,strlen(json_msg),json_msg,0,false)) {
      fprintf(stderr, "mosquitto_publish error...\n");
      //break;
    }
    printf("sent %d\n",msg_id);
    sleep(1);
  }

  mosquitto_destroy(mosq);
  mosquitto_lib_cleanup();
  free(json_msg);
  return 0;
}
