# __Communication UDP & Lecture sur STDOUT__ 


## Objectif :
* Avoir un client qui envoie un message avec le protocole UDP sur un serveur UDP qui le reçoit puis l’écrit dans la sortie STDOUT. 
* Cette sortie dans STDOUT est lue par un programme Python.

<br>

## Limites : 
* Client UDP simple (juste un “bind()” puis un “sendto()”)
Envoyer le message "PING" 
Ce petit POC a juste pour but de tester un peu la lecture sur STDOUT après l’arrivée d’un paquet, mais pas d’envoyer une structure car cela nécessite de la sérialisation (à voir dans un autre POC)

<br>

## Fonctionnement : 

### Client & Serveur UDP : 
    
* Ce sont des clients et serveur UDP classiques minimaux, le serveur attend qu'on lui envoie un message et l'écrit dans le flux ```STDOUT_FILENO``` avec la fonction ```write()``` , et le client se connecte et envoie juste un message "PING"

### Programme Python de lecture de STDOUT :

* *Partie de Benji*

