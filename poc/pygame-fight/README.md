# Implémentation des combats en jeu et gestion du système de phase

## Objectif :

- Avoir un jeu python développé grâce au module **pygame** très basique
- Commencé a voir le fonctionnement de base des phases

## Fonctionnement :

### Programme Python

- **Game** initialise la map les joueurs les ennemis et les combats, c'est là que tout est affiché et géré.
- **Map** création des maps utilisée dans le jeu et les combats (note : une "map" est une carte de jeu sur laquelle se déplacent les personnage)
- **Player** et **Foe** sont très similaires, ils ont un attribut map pour savoir ou ils sont et si ils sont déja phasé en fight.
- **Fight** créé différentes instances qui regroupent les combattants, une instance est toujours accessible même quand le combat a commencé.

## Lancer le jeu 

* Modules requis : Pygame 
* Commande : python3 Game.py (lancer le fichier "Game.py")

* Comment "utiliser" le programme : 
    * On peut faire bouger les carrés rouges qui sont des joueurs et quand un joueur rencontre un carré vert qui est un ennemi, on est transporté dans une instance du combat. En appuyant ensuite sur la touche "Tabulation" on peut revenir au monde de départ où on voit un point orange qui indique qu'un joueur est en combat. On peut le rejoindre en se déplaçant sur ce point orange, et on se retrouver également transporté à nouveau dans l'instance. 

