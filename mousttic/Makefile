CC = gcc

LDFLAGS = -lmosquitto -ljansson
CFLAGS = -g3 -Wall -Werror

all:simul registration

test: simul
	valgrind --leak-check=full ./simul -r 10

hello_world:
	$(CC) hello_world.c $(CFLAGS) $(LDFLAGS) -o hello_world

simul:
	$(CC) simul.c $(CFLAGS) $(LDFLAGS) -o simul

registration:
	$(CC) registration.c $(CFLAGS) $(LDFLAGS) -o registration -Wl,-rpath,/usr/local/lib -luuid
clean:
	rm -rf *.o *~ hello_world simul registration


