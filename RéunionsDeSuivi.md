# Réunions de suivi

# Réunion du 12/02/2021

- Petits programmes de test, qui permettent de connecter 2 joueurs ou plus en local, de façon assez minimaliste et en utilisant diverses méthodes ou protocoles 
  - On peut voir les personnages se déplacer sur chaque fenêtre
  - Les jeux se renvoient les tables d'adresses quand un nouveau jeu se connecte au groupe

- Programmes pour tester la faisabilité et la rapidité de différents protocoles (tcp, udp, ...)

- **Important** : Vous pouvez retrouver ces programmes de test dans le dossier `poc/` qui contient toutes les programmes non-reliés au jeu final que nous avons fait, dans le but d'expérimenter diverses méthodes et fonctionnalités pour faire notre jeu. Ils sont normalement assez documentés (avec des fichiers "README") mais si vous avez des problèmes avec ces derniers ou ne comprenez pas, n'hésitez pas à nous envoyer un mail.

# Réunion du 03/03/2021

- Petit programme pour instance de combat (création d'une salle parallèle quand un combat se lance, pour pouvoir mettre le jeu en tour par tour sans que cela soit trop long si trop de joueurs sont connectés en même temps), le programme n'est pas relié au premier petit programme de connexion
    - Vous pouvez trouver ce programme au chemin suivant : `poc/pygame-fight`

- Programmation d'une première vraie version du jeu, et structuration du code : chaque dossier contient des fonctionnalités du jeu, et des parties de code réseau et python ont bien été avancé : on peut se connecter, se déconnecter entre joueurs, etc. Côté Python, il y a une base du jeu avec des menus pour se connecter à d'autres joueurs notamment.


# Réunion du 18/03/2021

- Intégration de la sérialisation dans le jeu : on peut maintenant envoyer des structures, et nous avons défini une ""norme"" pour ces dernières pour créer des paquets standardisés
- Mise en place d'une carte (monde) de jeu en réseau
- Connexion depuis le jeu et non plus depuis le terminal


# Réunion du 25/03/2021
