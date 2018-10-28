# Analyse des 49151 grilles de sudoku


## 2018.10.26

* Nettoyage du code : identificateurs  harmonisés en anglais pour les variables en tout cas.
* Optimisation du calcul des pair cachées, triple cachés ainsi que la recherche des singletons.
* Création de deux fichiers avec les noms des grilles : 
	1. avec_backtrack contient les noms des 22833 grilles nécessitant encore du backtracking
	2. sans_backtrack contient les 26318 autres

Dernières stats effectuées (rangées dans le dossier Stats) :

* Sans backtrack : 26318 grilles, temps moyen : 0.007s
* Avec backtrack : 22833 grilles, temps moyen : 0.034s


## 2018.10.28

* Ajout recherche locked type 1. A permis à qq grilles de passer sans backtrack

Dernières stats effectuées (rangées dans le dossier Stats) :

* Sans backtrack : 37381 grilles, temps moyen : 0.008s
* Avec backtrack : 11770 grilles, temps moyen : 0.017s
