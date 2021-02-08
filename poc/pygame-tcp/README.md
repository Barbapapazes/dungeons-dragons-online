# Liaison entre un jeu basique Pygame et un serveur/client TCP

## Objectif :

- Avoir un jeu python développé grâce au module **pygame** très basique
- Créer un lien entre un serveur tcp et un jeu python

## Fonctionnement :

### Programme Python

- Le programme python est un jeu très simple développé grâce au module **pygame**.
  <br>On créé donc un objet `Game` qui va initialiser :
  - un écran d'une taille fixe de `1024 * 768`.
  - une horloge qui va définir la fréquence de rafraîchissement du logiciel.
  - `pygame.key.set_repeat(...)` qui permet de définir la fréquence à laquelle une touche va se répéter si elle reste enfoncée.
  - La position initiale du carré.
  - Une surface : `pygame.Surface(...)` qui est l'objet que nous allons faire bouger.
  - On définit la couleur de notre Surface : Blanc.
  - On définit un `booléen` qui nous permettra de savoir quand envoyer des données ou non.
- En fonction des inputs utilisateurs **ZQSD** la surface va se déplacer de haut en bas et de gauche à droite sans sortir de l'écran.
- On peut sortir du programme en cliquant sur la croix en haut à droite.
- Une fonction `auto()` permet de se faire déplacer automatiquement les carrés pour vérifier si des problèmes surviennent.
- La fonction `serv()` permet de créer un sous-processus via `Popen` qui exécute la commande `./tcpclient [x,y]` avec [x,y] la position de notre surface.

### Client & Serveur TCP :

- Le serveur est lancé dans un autre terminal et peut gérer une file de 20000 connexions en cas de forte affluence (modifiable)
- Le client tcp se connecte au serveur si un serveur existe sinon il se termine. Une fois connecté il envoie le message passé par `argv[1]` plus un retour à la ligne pour signifier la fin du paquet (surtout pour l'affichage) et se déconnecte.
