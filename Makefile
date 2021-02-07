.PHONY: all init receive send clean poc

all: init receive send

init:
	@mkdir build -p

receive: receive/main.c
	@gcc -o build/receive receive/main.c 

	
send: send/main.c
	@gcc -o build/send send/main.c 

clean:
	@rm -f build/* poc/subprocess-popen/sub poc/serialization/udpclient poc/serialization/udpserver poc/stdout-reading-udp/udpclient poc/stdout-reading-udp/udpserver

poc:
	@echo create subprocess-popen
	@gcc -o poc/subprocess-popen/sub poc/subprocess-popen/sub.c
	@echo create serialization
	@gcc -o poc/serialization/udpclient poc/serialization/udpclient.c
	@gcc -o poc/serialization/udpserver poc/serialization/udpserver.c
	@echo create stdout-reading-udp
	@gcc -o poc/stdout-reading-udp/udpclient poc/stdout-reading-udp/udpclient.c
	@gcc -o poc/stdout-reading-udp/udpserver poc/stdout-reading-udp/udpserver.c