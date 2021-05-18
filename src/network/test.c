#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <hashtable.h>

int main()
{
    return 0;
}

// struct nlist
// {                       /* table entry: */
//     struct nlist *next; /* next entry in chain */
//     char *name;         /* defined name */
//     int value;          /* replacement text */
// };

// #define HASHSIZE 100019
// static struct nlist *hashtab[HASHSIZE]; /* pointer table */

// /* hash: form hash value for string s */
// unsigned hash(char *s)
// {
//     unsigned hashval;
//     for (hashval = 0; *s != '\0'; s++)
//         hashval = *s + 101 * hashval;
//     printf("hash value : %d\n", hashval % HASHSIZE);
//     return hashval % HASHSIZE;
// }

// /* lookup: look for s in hashtab */
// struct nlist *lookup(char *s)
// {
//     struct nlist *np;
//     for (np = hashtab[hash(s)]; np != NULL; np = np->next)
//         if (strcmp(s, np->name) == 0)
//             return np; /* found */
//     return NULL;       /* not found */
// }

// char *hash_strdup(char *);
// /* install: put (name, defn) in hashtab */
// struct nlist *install(char *name, int value)
// {
//     struct nlist *np;
//     unsigned hashval;
//     if ((np = lookup(name)) == NULL)
//     { /* not found */
//         np = (struct nlist *)malloc(sizeof(*np));
//         if (np == NULL || (np->name = hash_strdup(name)) == NULL)
//             return NULL;
//         hashval = hash(name);
//         np->next = hashtab[hashval];
//         hashtab[hashval] = np;
//     }
//     np->value = value;
//     return np;
// }

// void print_hash_value()
// {
//     for (int i = 0; i < HASHSIZE; i++)
//         if (hashtab[i])
//             printf("%s : %d\n", hashtab[i]->name, hashtab[i]->value);
// }

// char *hash_strdup(char *s) /* make a duplicate of s */
// {
//     char *p;
//     p = (char *)malloc(strlen(s) + 1); /* +1 for ’\0’ */
//     if (p != NULL)
//         strcpy(p, s);
//     return p;
// }

// int main()
// {
//     struct nlist *tmp;

//     tmp = install("192.168.11.131:8000", 10);
//     tmp = install("192.168.11.131:8001", 10);
//     tmp = install("192.168.11.131:8002", 10);
//     tmp = install("192.168.111.131:8003", 10);
//     tmp = install("192.168.11.131:8004", 10);
//     tmp = install("192.168.11.131:8005", 10);
//     tmp = install("192.168.11.131:8006", 10);
//     tmp = install("192.158.11.151:8007", 10);
//     tmp = install("192.168.11.131:8008", 10);
//     tmp = install("192.168.11.131:8009", 10);
//     tmp = install("192.168.11.131:8010", 10);
//     tmp = install("192.168.11.131:8011", 10);
//     tmp = install("192.168.11.131:8012", 10);
//     tmp = install("192.168.11.191:8013", 10);
//     tmp = install("192.168.11.131:8014", 10);
//     tmp = install("192.164.11.131:8015", 10);
//     // tmp = install("191.114.127.32:8000", 14);
//     // printf("%s : %d\n", tmp->name, tmp->value);
//     // printf("---------\n");
//     print_hash_value();

//     return 0;
// }