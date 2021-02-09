# Création d'un multijoueur très simple entre deux programmes python

## Objectif :

- Avoir un jeu python développé grâce au module **pygame** très basique
- Créer un lien entre un serveur tcp et un jeu python
- Intégrer le serveur tcp au jeu python
- Gérer un nombre illimité de clients

## Fonctionnement :

### Lancement des programmes :

- On peut lancer le programme python de deux façons :
  - Soit on veut créer une nouvelle partie auquel cas la syntaxe de lancement du programme est : `python3 game.py <server_port>`
  - Soit on veut rejoindre une partie existante auquel cas la syntaxe de lancement du programme est : `python3 game.py <server_port> <ip>:<port>`
    <br>_exemple : python3 game.py 8000 <br> dans un autre terminal : python3 game.py 8001 127.0.0.1:8000_

### Programme Python :

- Le programme python est un jeu très simple développé grâce au module **pygame**.
  <br>On créé donc un objet `Game` qui va initialiser :
  - un écran d'une taille fixe de `1024 * 768`.
  - une horloge qui va définir la fréquence de rafraîchissement du logiciel.
  - `pygame.key.set_repeat(...)` qui permet de définir la fréquence à laquelle une touche va se répéter si elle reste enfoncée.
  - Le dictionnaire `self.players` contenant tous les joueurs actuellement connecté à la partie : la clé de chaque joueur est son adresse ip est son port `<ip>:<port>`
  - On définit un `booléen` qui nous permettra de savoir quand envoyer des données ou non.
  - On récupère le port server associé au programme et l'adresse ip du programme pour l'utiliser à l'avenir
  - On définit une liste `client_port` qui contiendra la liste de toutes les adresses ip + port `<ip>:<port>` pour envoyer des messages en P2P
  - Si on se connecte à une partie on ajoute l'adresse ip correspondante dans `client_port` et on lui envoie un message pour l'informer que c'est notre première connexion pour qu'elle renvoie sa propre liste `client_port`. De ce fait tous les joueurs ont une liste de client cohérente.
  - on lance un sous-processus via `Popen` qui correspondra au serveur.
  - on créé un objet `select.poll` qui va nous servir d'interface entre la sortie du server et le python. En effet, si on n'utilise pas ça on ne peut pas détecter si des information sont écrites sur stdout et donc le `readline()` peut complétement bloquer le programme.
- En fonction des inputs utilisateurs **ZQSD** la surface va se déplacer de haut en bas et de gauche à droite sans sortir de l'écran.
- On peut sortir du programme en cliquant sur la croix en haut à droite. Cette action entraine aussi la mort du sous-processus server **NE PAS QUITTER AVEC CTRL+C SINON LES PORTS RESTENT UTILISÉS**
- Une fonction `auto()` permet de se faire déplacer automatiquement les carrés pour vérifier si des problèmes surviennent.
- La fonction `client()` permet de créer un sous-processus via `Popen` qui exécute la commande `./tcpclient`. cette fonction prend un argument paramétré. Si il n'est pas réécrit c'est que la fonction est utilisée pour envoyer la position du jouer. Sinon le msg est envoyé à la place. Le message est envoyé à **tous les clients contenus dans client_port**
- La fonction `ip_send()` permet d'envoyer les ips contenues dans `client_port` au client qui vient de se connecter. La fonction envoie également l'adresse ip du nouveau client à tous les anciens clients pour conserver une cohérence. La position de tous les joueurs est aussi envoyé.
- La fonction `server()` permet de récupérer les informations transmises par le serveur sur sa sortie standard et de les traiter. Dans notre cas nous traitons la première connexion avec `first`, l'ajout d'un nouveau client avec `ip` et les déplacements avec `move`.
- la classe `Player` permet d'initialiser des surfaces de 50\*50 en 0,0 pour représenter des joueurs.
- Après chaque envoie via `Popen`, il est nécessaire d'attendre la fin du processus. Sinon des bugs peuvent apparaître. Si des clients se connectent pendant que des paquets sont envoyés il est possible qu'ils ne reçoivent pas l'information de la position de tous les joueur.
- Lorsqu'un joueur quitte le programme il disparait de l'écran des autres joueurs ainsi que de `client_port`

### Client & Serveur TCP :

- Le serveur est lancé dans un autre terminal et peut gérer une file de 20000 connexions en cas de forte affluence (modifiable). Le serveur est dans une boucle infini et ne s'arrête jamais.
- Le client tcp se connecte au serveur, sur le port passé par `argv[1]`,si un serveur existe sinon il se termine. Une fois connecté il envoie le message passé par `argv[2]` plus un retour à la ligne pour signifier la fin du paquet et se déconnecte.
