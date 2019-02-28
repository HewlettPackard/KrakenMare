CC = gcc

LDFLAGS = -lmosquitto -ljansson
CFLAGS = -O2 -g -Wall -Werror

all:simul

test: simul
	valgrind --leak-check=full ./simul -r 10

hello_world:
	$(CC) hello_world.c $(CFLAGS) $(LDFLAGS) -o hello_world

simul:
	$(CC) simul.c $(CFLAGS) $(LDFLAGS) -o simul
clean:
	rm -rf *.o *~ hello_world simul


