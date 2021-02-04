all: init receive send

init:
	@mkdir build -p

receive: receive/main.c
	gcc -o build/receive receive/main.c 

	
send: send/main.c
	gcc -o build/send send/main.c 