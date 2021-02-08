.PHONY: all init receive send clean poc

all: init receive send

init:
	@mkdir build -p

receive: receive/main.c
	@gcc -o build/receive receive/main.c 

	
send: send/main.c
	@gcc -o build/send send/main.c 

clean:
	@rm -f build/* poc/subprocess-popen/sub poc/serialization/udpclient poc/serialization/udpserver poc/stdout-reading-udp/udpclient poc/stdout-reading-udp/udpserver poc/stdout-reading-tcp/tcpserver poc/stdout-reading-tcp/tcpclient poc/pygame-tcp/tcpserver poc/pygame-tcp/tcpclient poc/pygame-tcp-multi/tcpserver poc/pygame-tcp-multi/tcpclient

poc:
	@echo create subprocess-popen
	@gcc -o poc/subprocess-popen/sub poc/subprocess-popen/sub.c
	@echo create serialization
	@gcc -o poc/serialization/udpclient poc/serialization/udpclient.c
	@gcc -o poc/serialization/udpserver poc/serialization/udpserver.c
	@echo create stdout-reading-udp
	@gcc -o poc/stdout-reading-udp/udpclient poc/stdout-reading-udp/udpclient.c
	@gcc -o poc/stdout-reading-udp/udpserver poc/stdout-reading-udp/udpserver.c
	@gcc -o poc/stdout-reading-tcp/tcpserver poc/stdout-reading-tcp/tcpserver.c
	@gcc -o poc/stdout-reading-tcp/tcpclient poc/stdout-reading-tcp/tcpclient.c
	@gcc -o poc/pygame-tcp/tcpclient poc/pygame-tcp/tcpclient.c
	@gcc -o poc/pygame-tcp/tcpserver poc/pygame-tcp/tcpserver.c
	@gcc -o poc/pygame-tcp-multi/tcpclient poc/pygame-tcp-multi/tcpclient.c
	@gcc -o poc/pygame-tcp-multi/tcpserver poc/pygame-tcp-multi/tcpserver.c