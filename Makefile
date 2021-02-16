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
						network-full-c/fork-read/main
POC_SRCS = $(addprefix $(POC_DIR),$(POC_NAMES))

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

poc: $(POC_SRCS)
	@echo Create $(POC_SRCS)

$(POC_SRCS): %: %.c
	@$(CC) $(CFLAGS) -o $@ $<
