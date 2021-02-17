# Dungeons and Dragons online

> Un projet de 3A pour les cours de réseau

## Build setup

Ce projet nécessite un os sous **linux** pour fonctionner.

### C

On trouvera un makefile permettant de compiler les fichiers C relatif au projet. Dans le dossier send, on trouve l'ensemble des fichiers permettant d'envoyer de la data et le dossier receive permettra d'accueillir l'ensemble des fichiers pour l'envoie de paquets.

L'ensemble des exécutables seront mis dans le dossier `build`.

#### POC

Afin de compiler aisément l'ensemble des exécutables, il est possible d'utiliser `make poc` ou `make src`. Attention, il est important de `make clean` avant de add pour s'assurer que les exécutables ne soient pas pris en compte.


Aussi, lors de la création d'un nouveau poc, il suffit s'implement d'ajouter le chemin de l'exécutable à faire dans la variable `POC_NAMES`.

### Python

La fichier `main.py` à la racine du projet sera le point d'entrée. Le reste des fichiers relatifs aux pythons seront disposé dans différents dossiers à la racine du projet.

You need **python 3.9** and **pip** installed on your machine.

```sh
# install pipenv
$ pip install pipenv
# install all packages
$ pipenv install
# start in dev mode
$ pipenv run dev
```

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

Pour lint notre code, il est utilisé `flake8`. En ce qui concerne le formatage, il est utilisé `black`.

Afin de s'assurer que chacun est du code de qualité, il ests vivement conseillé d'installer les extensions recommendées pour ce projet. Les paramètres présents dans `.vscode/settings.json` permettrons de voir vos erreurs directement dans vscode.
