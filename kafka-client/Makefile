CC = gcc

LDFLAGS = -lrdkafka -ljansson
CFLAGS = -O2 -g -Wall -Werror -I/usr/local/include/librdkafka

all:simul

simul:
	$(CC) simul.c $(CFLAGS) $(LDFLAGS) -o simul
clean:
	rm -rf *.o *~ simul
