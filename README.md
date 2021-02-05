# Dungeons and Dragons online

> Un projet de 3A pour les cours de réseau

## Build setup

Ce projet nécessite un os sous **linux** pour fonctionner.

### C

On trouvera un makefile permettant de compiler les fichiers C relatif au projet. Dans le dossier send, on trouve l'ensemble des fichiers permettant d'envoyer de la data et le dossier receive permettra d'accueillir l'ensemble des fichiers pour l'envoie de paquets.

L'ensemble des exécutables seront mis dans le dossier `build`.

### Python

La fichier `main.py` à la racine du projet sera le point d'entrée. Le reste des fichiers relatifs aux pythons seront disposé dans différents dossiers à la racine du projet.

## Docs

Read the docs [here](https://barbapapazes.github.io/dungeons-dragons-online/).

To start the docs locally, you need [nodejs](https://nodejs.org).

```sh
# install dependencies
npm i
# start the docs in dev mode
npm docs:dev
# build the docs in production mode
npm docs:build
```

### VS Code

[VS Code](https://code.visualstudio.com/) is recommended for this project.

To improve the way the code is written, there is some recommendations, about extensions, in the `.vscode` folder.

### Linter and formatter

Pour lint notre code, il est utilisé `flake8`. En ce qui concerne le formatage, il est utilisé `black`. Afin de n'avoir que du code de qualité et s'assurer que tout le monde respect les mêmes normes, il a été mis en place un outil git va s'assurer de la qualité du code python à chaque commit.

Le fonctionnement est le suivant :

- il est commit des fichiers python
- le pré-commit se déclenche et le code est vérifié
- si tout est bon le commit est réalisé, sinon les informations vous seront indiquées en console (s'il ne s'agit que de formatage, alors le pré-commit le fera mais il faudra retenter le commit pour s'en assurer)
