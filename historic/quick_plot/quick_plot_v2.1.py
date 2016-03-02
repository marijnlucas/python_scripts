#!/usr/local/bin/python3
#-*-coding:utf-8 -*-

#version2: ajout de la fonction offset
#version2.1: modification des legendes. Inclusion de la frequence et amplitude à chaque fois

from scipy import *
from pylab import *
import matplotlib.pyplot as plt
import glob, inspect, os
	
script_dir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+'/' # to get the path to the directory containing the script and the data
liste_fichiers=glob.glob(script_dir+'*.dat') #list of all .dat files in script_dir
nombre_de_courbes=len(liste_fichiers)
offset=zeros((nombre_de_courbes,2)) #initialise la matrice des offsets des courbes (col1: offset sur x et col2: offset sur y)

# NE MODIFIER QUE LES VARIABLES ENTRES LES BARRES #
#######################################################
################## PEUT ETRE MODIFIE ##################
##################VVVVVVVVVVVVVVVVVVV##################

titre="titre du graph"
nom_axe_x='Temperature (K)'
nom_axe_y='Magnitude (V)'
data_set_up=5 #nombre de premières lignes ignorées dans le fichier de données .dat
data_set_low=420 #nombre de dernière lignes ignorées dans le fichier de données .dat
grille='oui' #grille sur le graph (oui/non)
liste_offset=('oui',[1,0,0.0000005],[2,0,0]) #si offset[0]='oui', alors offset X =3, offset Y=2 sur courbe 1 et offset X =5, offset Y=3 sur courbe 2
								# le nombre de tuples ne peux pas être supérieur on nombre de .dat dans le dossier

#######################################################
################### NE PAS MODIFIER ###################
##################VVVVVVVVVVVVVVVVVVV##################


#remplissage de la matrice des offsets si offset[0]=='oui'
if liste_offset[0]=='oui' or liste_offset[0]=='OUI' or liste_offset[0]=='O' or liste_offset[0]=='o':
	nombre_offset=len(liste_offset)-1
	k=1
	while k <=nombre_offset-1:
		offset[liste_offset[k][0]-1, 0]=liste_offset[k][1] #ajoute offset X pour la courbe liste_offset[k][0] à la ligne liste_offset[k][0]-1 dans la matrice offset (col0)
		offset[liste_offset[k][0]-1, 1]=liste_offset[k][2] #ajoute offset Y pour la courbe liste_offset[k][0] à la ligne liste_offset[k][0]-1 dans la matrice offset (col1)
		k+=1

#initialisation de deux tableaux (un pour x et un pour y) qui vont contenir le max 
#et le min des donnees de chaque fichier .dat traite
xscale=zeros((nombre_de_courbes, 2))
yscale=zeros((nombre_de_courbes, 2))
plt.figure()

i=0
while i<=nombre_de_courbes-1:
	# Import the data from a text file and save as a 2D matrix. Adapter le 'skip_header' au .dat
	print("---> fichier .dat en cours de traitement :", liste_fichiers[i])
	matrice_donnees = genfromtxt(liste_fichiers[i], skip_header=data_set_up, skip_footer=data_set_low) #, missing_values='???', filling_values='0.2')
	# Slice out required abscissae and ordinate vectors. Column vector 0 --> x axis and 3 --> y axis.
	x = matrice_donnees[:,0]+offset[i,0]
	y = matrice_donnees[:,3]+offset[i,1]
	# on recupere le max et le min des x et y pour determiner les echelles
	xscale[i,0]=max(x)
	xscale[i,1]=min(x)
	yscale[i,0]=max(y)
	yscale[i,1]=min(y)
	#on cherche a obtenir le nom du fichier sans le chemin (ce serait trop encombrant sur les graphs
	#1: on decoupe le chemin vers le fichier .dat en cours de traitement
	decoupage=liste_fichiers[i].split('/')
	#decoupage est une liste d'elements de chemin vers le .dat (chaque partie encadree par / est un element de la liste)
	#2: on prend le dernier element, qui est aussi le nom du fichier de donnees
	if offset[i,0]!=0 or offset[i,1]!=0:
		nom_fichier='graph '+str(i+1)+' : '+decoupage[len(decoupage)-1]+'\n ---> f='+str(matrice_donnees[0,5])+'Hz | Vo='+str(matrice_donnees[0,7])+'V | offset X='+str(offset[i,0])+' | offset Y='+str(offset[i,1])
	else:
		nom_fichier='graph '+str(i+1)+' : '+decoupage[len(decoupage)-1]+'\n ---> f='+str(matrice_donnees[0,5])+'Hz | Vo='+str(matrice_donnees[0,7])+'V'
	plt.plot(x,y,label=nom_fichier)
	print("\t ----traitement accompli sans erreur----")
	i+=1


#on recupere les max et min pour x et y pour les echelles
xscale_up=max(xscale[:,0])
xscale_low=min(xscale[:,1])
yscale_up=max(yscale[:,0])
yscale_low=min(yscale[:,1])
xdelta=(xscale_up-xscale_low)/100
ydelta=(yscale_up-yscale_low)/100
plt.legend(loc='best')
plt.title(titre+'\n frequency : '+str(matrice_donnees[0,5])+'Hz | amplitude : '+str(matrice_donnees[0,7])+'V')
plt.axis([xscale_low-xdelta, xscale_up+xdelta, yscale_low-ydelta, yscale_up+ydelta])
plt.xlabel(nom_axe_x)
plt.ylabel(nom_axe_y)
if grille=='oui' or grille=='OUI' or grille == 'Oui' or grille=='o' or grille=='O':
	plt.grid(True)
else:
	plt.grid(False)
	
		
#plt.text(5, 0.000082, '')
plt.savefig(script_dir+titre)
plt.show()