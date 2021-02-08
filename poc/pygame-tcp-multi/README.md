# Création d'un multijoueur très simple entre deux programmes python

## Objectif :

- Avoir un jeu python développé grâce au module **pygame** très basique
- Créer un lien entre un serveur tcp et un jeu python
- Intégrer le serveur tcp au jeu python

## Fonctionnement :

### Lancement des programmes :

- Pour pouvoir lancer le programme python il faut respecter la syntaxe suivante : `python3 game.py <server_port> <client_port>` sinon le programme lève une exception. <br>`<server_port> != <client_port>` <br>_exemple : python3 game.py 8000 8001 <br> dans un autre terminal : python3 game.py 8001 8000_
- Le jeu est pour l'instant seulement jouable à 2. C'est pour cela qu'il faut indiquer le port client.

### Programme Python :

- Le programme python est un jeu très simple développé grâce au module **pygame**.
  <br>On créé donc un objet `Game` qui va initialiser :
  - un écran d'une taille fixe de `1024 * 768`.
  - une horloge qui va définir la fréquence de rafraîchissement du logiciel.
  - `pygame.key.set_repeat(...)` qui permet de définir la fréquence à laquelle une touche va se répéter si elle reste enfoncée.
  - Les deux joueurs contenu dans le dictionnaire `self.players`
  - On définit un `booléen` qui nous permettra de savoir quand envoyer des données ou non.
  - On récupère le port server associé au programme et le port client vers le quel on va envoyer les données de position.
  - on lance un sous-processus via `Popen` qui correspondra au serveur.
  - on créé un objet `select.poll` qui va nous servir d'interface entre la sortie du server et le python. En effet, si on n'utilise pas ça on ne peut pas détecter si des information sont écrites sur stdout et donc le `readline()` peut complétement bloquer le programme.
- En fonction des inputs utilisateurs **ZQSD** la surface va se déplacer de haut en bas et de gauche à droite sans sortir de l'écran.
- On peut sortir du programme en cliquant sur la croix en haut à droite. Cette action entraine aussi la mort du sous-processus server **NE PAS QUITTER AVEC CTRL+C SINON LES PORTS RESTENT UTILISÉS**
- Une fonction `auto()` permet de se faire déplacer automatiquement les carrés pour vérifier si des problèmes surviennent.
- La fonction `client()` permet de créer un sous-processus via `Popen` qui exécute la commande `./tcpclient [x,y]` avec [x,y] la position de notre surface.
- La fonction `server()` permet de récupérer les informations transmises par le serveur sur sa sortie standart. Dans notre cas seule la position est envoyé, de ce fait on doit modifier la chaine de caractère pour récupérer les informations de position et les attribuer au second joueur.
- la classe `Player` permet d'initialiser des surfaces de 50\*50 en 0,0 pour représenter des joueurs.

### Client & Serveur TCP :

- Le serveur est lancé dans un autre terminal et peut gérer une file de 20000 connexions en cas de forte affluence (modifiable). Le serveur est dans une boucle infini et ne s'arrête jamais.
- Le client tcp se connecte au serveur, sur le port passé par `argv[1]`,si un serveur existe sinon il se termine. Une fois connecté il envoie le message passé par `argv[2]` plus un retour à la ligne pour signifier la fin du paquet et se déconnecte.
