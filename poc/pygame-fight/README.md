# Implémentation des combats en jeu et gestion du système de phase

## Objectif :

- Avoir un jeu python développé grâce au module **pygame** très basique
- Commencé a voir le fonctionnement de base des phases

## Fonctionnement :

### Programme Python

- **Game** initialise la map les joueurs les ennemies et les combats, c'est la que tout est affiché et géré.
- **Map** creation des maps utilisé dans le jeu et les combats.
- **Player** et **Foe** sont très similaires, ils ont un attribut map pour savoir ou ils sont et si ils sont déja phasé en fight.
- **Fight** créé différentes instance qui regroupe les combatants, une instance est toujours accecible meme quand le combat à commencé.

