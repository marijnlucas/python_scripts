#!/usr/local/bin/python3
#-*-coding:utf-8 -*-

#version2: ajout de la fonction offset
#version2.1: modification des legendes. Inclusion de la frequence et amplitude à chaque fois
#version3: ajout de la fonction auto_offset
#version3.1: ajout de liste des courbes à tracer
#version3.2(20151103): ajustement de l'échelle aux courbes tracées uniquement

from scipy import *
from pylab import *
import matplotlib.pyplot as plt
import glob, inspect, os
	
script_dir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+'/' # to get the path to the directory containing the script and the data
liste_fichiers=glob.glob(script_dir+'*.dat') #list of all .dat files in script_dir
nombre_fichiers=len(liste_fichiers) #compte le nombre de fichiers .dat dans le répertoire courant

recommencer='oui'
while recommencer=='oui' or recommencer=='OUI':

	print('les fichiers presents dans ce repertoire sont:\n')
	print(liste_fichiers)
	fichier_corr=input('modifier quel fichier? (entrer nom complet tel que dans la matrice ci-dessus)')

	k=0 #variable pour stocker la position du fichier à corriger dans liste_fichiers
	# détermine la position du fichier à modifier dans liste_fichiers
	if liste_fichiers[k]!=fichier_corr:
		i=1
		while i<nombre_fichiers:
			if fichier_corr==liste_fichiers[i]:
				k=i
				i=nombre_fichiers
			else:
				i+=1
	
	if liste_fichiers[k]!=fichier_corr: #aucun fichier ayant le nom renseigné n'est trouvé
		print('nom de fichier introuvable, recommencer (oui/non)?')
	else: #cas où le fichier est trouvé à la position i dans liste_fichiers
		# Import the data from a text file and save as a 2D matrix. Adapter le 'skip_header' au .dat
		print("---> fichier .dat en cours de traitement :", liste_fichiers[k])
		matrice_donnees = genfromtxt(liste_fichiers[k], skip_header=5)
		print(matrice_donnees)
		
	recommencer=input('modifier un nouveau fichier? (oui/non)')
	
	
	
	