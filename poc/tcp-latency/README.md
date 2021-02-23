# TCP-LATENCY

## Lancement :

- serveur : `./tcpserver <port_serveur> <ip_serveur>`
- client : `./tcpclient <ip_cible> <port_cible>`

### Serveur TCP :

- Le serveur se lance et créé un socket comportant l'adresse et le port donné en argument. Il attend ensuite une première connection avec `accept()`. Lorsqu'une connexion est établie, le programme se duplique : le père reste écouter le socket créé initialement pour accepter les potentielles nouvelles connexions tandis que le fils va écouter sur le nouveau socket associé à la connexion. Dès qu'il reçoit un message il l'écrit sur `STDOUT_FILENO` et analyse le paquet : si le nombre d'octet reçu est inférieur à 1500 (limite définie) celà indique qu'on arrive à la fin du paquet et qu'on peut donc prévenir le client de la bonne réception en lui envoyant le message `acknowledge`. Si le serveur reçoit un signal `SIGUSR1`, il envoie le signal `SIGINT` à tous ses fils et termine le programme avec `_exit(EXIT_SUCCESS)`.

### Client TCP :

- Le client essaie de se connecter au couple ip + port donné en argument. Si la tentative de connexion excède la valeur du timeout (0.1s), la tentative échoue et une erreur est soulevée par le programme. Avant de commencer à envoyer des données, le programme vérifie que la connexion s'est bien établie et qu'il n'y a pas eu de problèmes au niveau du socket. Lorsqu'un packet est envoyé, le temps en microsecondes est récupéré et le programme se met à écouter sur le socket pour recevoir quelquechose. Lorsque le programme reçoit le message `acknowledge` du serveur, il récupère de nouveau le temps en microsecondes et fais la différence entre les deux pour obtenir la latence. Le calcul du ping se fait en local sans requête NTP pour pouvoir jouer au jeu dans un réseau LAN sans accès à internet.
