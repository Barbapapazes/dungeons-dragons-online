# Evolution du jeu au fur et à mesure du temps

_Note : "Petit programme" est un programme qui a pour but de tester des fonctionnalité et leur fonctionnement avant de les intégrer au jeu (dossier *poc*), "jeu" désigne en revanche le programme principal auquel on ajoute les fonctionnalités au fur et à mesure_

# Réunion 12/02/2021

- Petits programmes de test, qui permettent de connecter 2 jeux ou plus en local (première version très minimaliste)
  - On peut voir les personnages se déplacer sur chaque fenetres
  - Les jeux se renvoient les tables d'adresse quand un nouveau jeu se connecte au groupe

- Programmes pour tester la faisabilité de différents protocoles (tcp, udp, ...)

# Réunion 03/03/2021

- Petit programme pour instance de combat (création d'une salle parallèle quand un combat se lance, pour pouvoir mettre le jeu en tour par tour sans que cela soit trop long si trop de joueurs sont connectés en même temps), le programme n'est pas relié au premier petit programme de connexion
- Beaucoup de modification sur la structure du code, et avancé sur un code plus global qui n'était pas encore fonctionnel
  
# Réunion 18/03/2021

- Intégration de la sérialisation dans le jeu
- Mise en place d'une carte (monde) de jeu en réseau
- Connexion depuis le jeu et non plus depuis le terminal