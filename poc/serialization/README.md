# __Sérialisation et envoi de structures en C__


## Objectif :
* Découvrir comment on envoie des structures en C
* Découvrir ce qu’est la sérialisation des données 

<br>

## Recherches :

[Envoie de structure par socket, Openclassroom](https://openclassrooms.com/forum/sujet/envoi-de-structure-par-socket-83381)<br>
[Sérialiser une structure, StackOverflow (source principale)](https://stackoverflow.com/questions/15707933/how-to-serialize-a-struct-in-c)
*Il manque pas mal de mes sources j'ai pas tout noté déso je le ferai plus tard*

* __*Trucs intéressants*__:
   * Apparemment, si notre structure contient des champs simples (donc pas d’adresses ou de choses dans le genre, des tableaux de taille fixée) la sérialisation n’est pas vraiment utile ? → à vérifier, j’ai l’impression que c’est uniquement valable en C++
   * D’autres sites disent que la sérialisation est importante parce que quand on envoie une structure on envoie un pointeur qui ne pointe plus sur rien
   * Sur StackOverflow on peut voir la méthode suivante : tout sérialiser sous forme d’une string (unsigned) et tout envoyer et du côté serveur ça déchiffre le tout

<br>

## Explication du code :

* Le tout est basé sur un client UDP simple, et j’ai défini une structure appelée ```game_struct``` qui représente un paquet qu’on pourrait envoyer 
* J’ai créé deux fonctions, ```serialization()``` qui prend un une structure et la transforme en chaîne de caractères, et ```deserialization()``` qui fait l’inverse

* __*La fonction serialization*__ : 
   * Elle prend une structure en paramètres
   * Elle récupère la taille du champ string de la structure (qui est ```game_struct.user_input```) afin de créer une chaîne de caractères qui sera de la forme : `[player_id][action][taille de user_input][user_input]`
   * Avec la fonction ```memcpy()``` on copie tout dans un buffer qu’on retourne

* __*La fonction deserialization*__ : 
   * Elle prend un buffer de caractères en entrée et retourne une structure ```game_struct```.
   * Elle copie les deux premiers champs dans une structure
   * Ensuite elle récupère la taille pour pouvoir allouer une bonne taille au champ ```game_struct.user_input```, puis elle copie ce qui reste du buffer dans ```game_struct.user_input```
   * Elle retourne la structure

* __*Les problèmes*__ : 
   * Quelque chose dans le code fait que la taille ```ui_len``` ("user_input len") ne passe pas à travers le réseau, puisque quand on la fixe on reçoit relativement bien le paquet mais quand on ne la fixe pas on a des tailles de 22909 à la place de 6 par exemple et impossible de trouver d’où ça vient (j’ai déjà essayé par mal de choses, je compte continuer mais au bout de 2h de recherche de bugs je commence à fatiguer)

*  __*Ce que je vais tenter*__ :
   * Régler le soucis
   * En cas d'échec, essayer de faire une sérialization plus simple à partir de strcpy (mais c'est moins stylé qu'on se l'avoue)

Toute aide est la bienvenue :)