CC = gcc
CFLAGS= -Wall

POC_DIR = poc/
POC_NAMES = subprocess-popen/sub \
						stdout-reading-udp/udpclient stdout-reading-udp/udpserver \
						stdout-reading-tcp/tcpserver stdout-reading-tcp/tcpclient \
						pygame-tcp/tcpclient pygame-tcp/tcpserver \
						pygame-tcp-multi/tcpclient pygame-tcp-multi/tcpserver \
						pygame-udp-multi/udpclient pygame-udp-multi/udpserver \
						pygame-tcp-thread/tcpclient pygame-tcp-thread/tcpserver \
						network-full-c/fork-read/main tcp-latency/tcpclient tcp-latency/tcpserver
POC_SRCS = $(addprefix $(POC_DIR),$(POC_NAMES))

SRC_DIR = src/
SRC_NAMES = tcpclient tcpserver
SRC_SRCS = $(addprefix $(SRC_DIR),$(SRC_NAMES))

.PHONY: all init receive send clean poc

all: init receive send

init:
	@mkdir build -p

receive: receive/main.c
	@$(CC) -o build/receive receive/main.c 
	
send: send/main.c
	@$(CC) -o build/send send/main.c 

clean:
	@rm -f build/* $(POC_SRCS)
	@rm -f build/* $(SRC_SRCS)

poc: $(POC_SRCS)
	@echo Create $(POC_SRCS)
src: $(SRC_SRCS)
	@echo Create $(SRC_SRCS)

$(SRC_SRCS): %: %.c
	@$(CC) $(CFLAGS) src/serialization.c -o $@ $<

$(POC_SRCS): %: %.c
	@$(CC) $(CFLAGS) -o $@ $<
