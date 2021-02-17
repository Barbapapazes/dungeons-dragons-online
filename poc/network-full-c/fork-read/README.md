# Communication entre un père et plusieurs fils

## Fonctionnement :

### Lancement des programmes :

- on lance le programme et on tape le texte qu'on souhaite envoyer aux enfants. `./main`

### main.c :

- Le programme créé plusieurs descripteurs de fichiers, chaque fils possède deux voie de communication avec le père : une entrante et sortante. Chaque fils attend de recevoir une ligne sur son descripteur entrant.
- Une fois tous les enfants créés le programme envoie la même chaîne à tous les enfants
