#!/usr/bin/python
#-*-coding:utf-8 -*-

from scipy import *
from pylab import *
import matplotlib.pyplot as plt
import glob, inspect, os

# les seules choses à renseigner
##############################
titre="titre du graph"
nom_axe_x='Temperature (K)'
nom_axe_y='Magnitude (V)'
grille='oui' #grille sur le graph (oui/non)
##############################

script_dir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+'/' # script directory #to get the path to the directory containing the script and the data
liste_fichiers=glob.glob(script_dir+'*.dat') #list of all .dat files in script_dir
nombre_de_courbes=len(liste_fichiers)

#initialisation de deux tableaux (un pour x et un pour y) qui vont contenir le max 
#et le min des donnees de chaque fichier .dat traite
xscale=zeros((nombre_de_courbes, 2))
yscale=zeros((nombre_de_courbes, 2))
plt.figure()

i=0
while i<=nombre_de_courbes-1:
	# Import the data from a text file and save as a 2D matrix. Adapter le 'skip_header' au .dat
	print("---> fichier .dat en cours de traitement :", liste_fichiers[i])
	matrice_donnees = genfromtxt(liste_fichiers[i], skip_header=5)
	# Slice out required abscissae and ordinate vectors. Column vector 0 --> x axis and 3 --> y axis.
	x = matrice_donnees[:,0]
	y = matrice_donnees[:,3]
	# on recupere le max et le min des x et y pour determiner les echelles
	xscale[i,0]=max(matrice_donnees[:,0])
	xscale[i,1]=min(matrice_donnees[:,0])
	yscale[i,0]=max(matrice_donnees[:,3])
	yscale[i,1]=min(matrice_donnees[:,3])
	#on cherche a obtenir le nom du fichier sans le chemin (ce serait trop encombrant sur les graphs
	#1: on decoupe le chemin vers le fichier .dat en cours de traitement
	decoupage=liste_fichiers[i].split('/')
	#decoupage est une liste d'elements de chemin vers le .dat (chaque partie encadree par / est un element de la liste)
	#2: on prend le dernier element, qui est aussi le nom du fichier de donnees
	nom_fichier=decoupage[len(decoupage)-1]
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
plt.title(titre+'\n frequency : '+str(matrice_donnees[0,5])+'Hz | amplitude : '+str(matrice_donnees[0,6])+'V')
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