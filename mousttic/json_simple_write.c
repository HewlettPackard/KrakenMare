#include <stdio.h>
#include <string.h>
#include <jansson.h>

int main(void) {
  
  char* s = NULL;
  
  json_t *root = json_object();
  json_t *json_arr = json_array();
  
  json_object_set_new( root, "destID", json_integer( 1 ) );
  json_object_set_new( root, "command", json_string("enable") );
  json_object_set_new( root, "respond", json_integer( 0 ));
  json_object_set_new( root, "data", json_arr );
  
  json_array_append_new ( json_arr, json_integer(11) );
  json_array_append_new ( json_arr, json_integer(12) );
  json_array_append_new ( json_arr, json_integer(14) );
  json_array_append_new ( json_arr, json_integer(9) );
  
  s = json_dumps(root, 0);
  
  puts(s);
  json_decref(root);
  free(s);
  
 return 0;
}
