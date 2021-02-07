# **Communication UDP & Lecture sur STDOUT**

## Objectif :

- Avoir un client qui envoie un message avec le protocole TCP sur un serveur TCP qui le reçoit puis l’écrit dans la sortie STDOUT.
- Cette sortie dans STDOUT est lue par un programme Python.

<br>

## Limites :

- Client TCP simple (juste un `connect()` puis un `send()`)
  Envoyer le message "PING"
  Ce petit POC a juste pour but de tester un peu la lecture sur STDOUT après l’arrivée d’un paquet, mais pas d’envoyer une structure car cela nécessite de la sérialisation (à voir dans un autre POC)

<br>

## Fonctionnement :

### Client & Serveur TCP :

- Ce sont des clients et serveur TCP classiques minimaux, le serveur attend qu'on lui envoie un message et l'écrit dans le flux `STDOUT_FILENO` avec la fonction `write()` , et le client se connecte et envoie juste un message "PING"

### Programme Python de lecture de STDOUT :

- Le programme python créé un sous-processus qui exécute _udpserver_ `subprocess.Popen(...)`. Le programme continue de s'exécuter tant que le sous-processus n'est pas terminé. Le programme python lit ligne par ligne la sortie stdout associée au sous-processus grâce à la fonction `stdout.readline()`et l'affiche à l'écran `stdout.write()`. Le flux récupéré grâce à `stdout.readline()` est un flux binaire qui est converti avant affichage avec la fonction `decode(...)`. Si le sous-processus se termine, le programme python sort de sa la boucle while et se termine aussi en affichant un message de succès.
