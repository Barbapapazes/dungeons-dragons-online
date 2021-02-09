all : tcpclient tcpserver 

tcpclient : tcpclient.o serialization.o
	gcc tcpclient.o serialization.o -o tcpclient 

tcpclient.o : tcpclient.c serialization.c 
	gcc -c tcpclient.c serialization.c 

tcpserver : tcpserver.o serialization.o
	gcc tcpserver.o serialization.o -o tcpserver 

tcpserver.o : tcpserver.c serialization.c 
	gcc -c tcpserver.c serialization.c 

clean :
	rm -rf *.o tcpserver tcpclient

