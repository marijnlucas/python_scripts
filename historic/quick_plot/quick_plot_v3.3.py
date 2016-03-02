#!/usr/local/bin/python3
#-*-coding:utf-8 -*-

#version2: ajout de la fonction offset
#version2.1: modification des legendes. Inclusion de la frequence et amplitude à chaque fois
#version3: ajout de la fonction auto_offset
#version3.1: ajout de liste des courbes à tracer
#version3.2(20151103): ajustement de l'échelle aux courbes tracées uniquement
#version3.3(20151105): permet de traiter des .dat avec des quantités variables de colonnes

from scipy import *
from pylab import *
import matplotlib.pyplot as plt
import glob, inspect, os
	
script_dir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+'/' # to get the path to the directory containing the script and the data
liste_fichiers=glob.glob(script_dir+'*.dat') #list of all .dat files in script_dir
nombre_de_courbes=len(liste_fichiers)
offset=zeros((nombre_de_courbes,3)) #initialise la matrice des offsets des courbes (col1: offset sur x et col2: offset sur y)
matrice_donnees_exp=zeros((2,1)) #stock la fréquence (ligne0) et l'amplitude (ligne1)

# NE MODIFIER QUE LES VARIABLES ENTRES LES BARRES #
#######################################################
################## PEUT ETRE MODIFIE ##################
##################VVVVVVVVVVVVVVVVVVV##################

tracer=(0) #pour tout tracer: 0, sinon liste de numeros (1,2,3,5,8,...) représentant l'id du graph dans la matrice offset

#informations relatives aux tracés
titref="Comparaison_differentes_frequences"
nom_axe_x='Temperature (K)'
nom_axe_y='Magnitude (V)'
grille='oui' 

#informations relatives aux fichiers de données
data_set_up=10 #nombre de premières lignes ignorées dans le fichier de données .dat
data_set_low=420 #nombre de dernière lignes ignorées dans le fichier de données .dat
data_x_axis=1 #colonne de données correspondant aux abscisses
data_y_axis=4 #colonne de données correspondant aux ordonnées
col_freq=6 #colonne où est indiquée la fréquence des mesures
col_amp=8 #colonne où est indiquée l'amplitude des mesures

#informations relative au traitement des données
liste_offset=('non',[1,0,0.0003259],[2,0,0.0004807],[3,0,0.00043345],[4,0,0.0003258],[7,0,0.00051]) #si offset[0]='oui', alors offset X =3, offset Y=2 sur courbe 1 et offset X =5, offset Y=3 sur courbe 2
								# le nombre de tuples ne peux pas être supérieur on nombre de .dat dans le dossier
auto_offset=('oui', 0) #pour mettre un offset à toutes les courbes de telle sorte qu'elles commencent toutes
							# au point d'ordonnée indiquée. Cette option est maître sur liste_offset (y seulement).

#######################################################
################### NE PAS MODIFIER ###################
##################VVVVVVVVVVVVVVVVVVV##################


#pour pas que tracer indique plus de courbes à tracer qu'il n'y a de graphs
if type(tracer)==int:
	if tracer>nombre_de_courbes:
		tracer=0
elif max(tracer)>nombre_de_courbes: #si plus de courbes indiquées, alors on les trace toutes
	tracer=0

#remplissage de la matrice des offsets si liste_offset[0]=='oui'
if liste_offset[0]=='oui' or liste_offset[0]=='OUI' or liste_offset[0]=='O' or liste_offset[0]=='o' and auto_offset[0]!='oui' and auto_offset[0]!='OUI' and auto_offset[0]!='Oui' and auto_offset[0]!='O' and auto_offset[0]!='o':
	nombre_offset=len(liste_offset)-1
	k=1
	while k <=nombre_offset:
		offset[liste_offset[k][0]-1, 0]=liste_offset[k][1] #ajoute offset X pour la courbe liste_offset[k][0] à la ligne liste_offset[k][0]-1 dans la matrice offset (col0)
		offset[liste_offset[k][0]-1, 1]=liste_offset[k][2] #ajoute offset Y pour la courbe liste_offset[k][0] à la ligne liste_offset[k][0]-1 dans la matrice offset (col1)
		k+=1

#initialisation de deux tableaux (un pour x et un pour y) qui vont contenir le max 
#et le min des donnees de chaque fichier .dat traite
if type(tracer)==int: #cas où tracer ne contient qu'une seule valeur
		if tracer==0: #il faut tracer toutes les courbes et on doit considérer les max/min de toutes les courbes
			xscale=zeros((nombre_de_courbes, 2))
			yscale=zeros((nombre_de_courbes, 2))
		else: #si trace=!0 alors il n'y a qu'une seule courbe à tracer
			xscale=zeros((1, 2))
			yscale=zeros((1, 2))
else: #si pas int alors liste et donc on peut utiliser len()
	xscale=zeros((len(set(tracer)), 2)) #set() compte le nombre unique d'éléments d'une liste
	yscale=zeros((len(set(tracer)), 2))
	
plt.figure()

i=0
j=0 #compteur de remplissage des matrices des max et min
while i<=nombre_de_courbes-1:
	# Import the data from a text file and save as a 2D matrix. Adapter le 'skip_header' au .dat
	print("---> fichier .dat en cours de traitement :", liste_fichiers[i])
	matrice_donnees_axes = genfromtxt(liste_fichiers[i], skip_header=data_set_up, skip_footer=data_set_low, usecols=(data_x_axis-1, data_y_axis-1))#stock que les données utilisées
	#on utilise genfromtxt à 2 endroits différents du fichier données usecols(col_freq-1 et col_amp-1) car ces colonnes peuvent être de longueur différentes
	matrice_donnees_exp[0] = genfromtxt(liste_fichiers[i], skip_header=data_set_up, skip_footer=data_set_low, usecols=(col_freq-1))[0]#stock la fréquence
	matrice_donnees_exp[1] = genfromtxt(liste_fichiers[i], skip_header=data_set_up, skip_footer=data_set_low, usecols=(col_amp-1))[0]#stock l'amplitude
	#print(genfromtxt(liste_fichiers[i], skip_header=data_set_up, skip_footer=data_set_low, usecols=(col_freq-1,col_amp-1))) #pour ctrl seulement
	#print(matrice_donnees_exp) #pour ctrl seulement
	# Slice out required abscissae and ordinate vectors. Column vector data_x_axis --> x axis and data_y_axis --> y axis.
	if auto_offset[0]=='oui' or auto_offset[0]=='OUI' or auto_offset[0]=='O' or auto_offset[0]=='o':
		auto_offset_i=auto_offset[1]-matrice_donnees_axes[0,1]#calcul de l'offset y à appliquer pour la courbe i
		offset[i, 1]=auto_offset_i #remplace les offset en y de la matrices par les auto_offset_i
		offset[i, 2]=i+1 #ajoute identifiant de la courbe pour une lecture de matrice plus claire
		
	x = matrice_donnees_axes[:,0]+offset[i,0]
	y = matrice_donnees_axes[:,1]+offset[i,1]
	#on cherche a obtenir le nom du fichier sans le chemin (ce serait trop encombrant sur les graphs
	#1: on decoupe le chemin vers le fichier .dat en cours de traitement
	decoupage=liste_fichiers[i].split('/')
	#decoupage est une liste d'elements de chemin vers le .dat (chaque partie encadree par / est un element de la liste)
	#2: on prend le dernier element, qui est aussi le nom du fichier de donnees
	if offset[i,0]!=0 or offset[i,1]!=0:
		nom_fichier='graph '+str(i+1)+' : '+decoupage[len(decoupage)-1]+'\n ---> f='+str(matrice_donnees_exp[0,0])+'Hz | Vo='+str(matrice_donnees_exp[1,0])+'V | offset X='+str(offset[i,0])+' | offset Y='+str(offset[i,1])
	else:
		nom_fichier='graph '+str(i+1)+' : '+decoupage[len(decoupage)-1]+'\n ---> f='+str(matrice_donnees_exp[0,0])+'Hz | Vo='+str(matrice_donnees_exp[1,0])+'V'
	
	if type(tracer)==int: #cas où tracer ne contient qu'une seule valeur
		if tracer==0 or tracer==i+1: #si tracer=0 il faut tracer toutes les courbes, donc celle là aussi
			# on recupere le max et le min des x et y du i actuel pour déterminer les échelles
			xscale[j,0]=max(x)
			xscale[j,1]=min(x)
			yscale[j,0]=max(y)
			yscale[j,1]=min(y)
			j+=1
			plt.plot(x,y,label=nom_fichier) #si tracer=i+1 il faut tracer cette courbe
			print("\t ----traitement accompli sans erreur (courbe", i+1, "tracée)----")
		else:
			print("\t ----traitement accompli sans erreur (courbe", i+1, "non tracée)----")
	elif i+1 in tracer: #cas où les courbes à tracer sont renseignées dans une liste 'tracer'
		# on recupere le max et le min des x et y du i actuel pour déterminer les échelles
		xscale[j,0]=max(x)
		xscale[j,1]=min(x)
		yscale[j,0]=max(y)
		yscale[j,1]=min(y)
		j+=1
		plt.plot(x,y,label=nom_fichier)
		print("\t ----traitement accompli sans erreur (courbe", i+1, "tracée)----")
	else:
		print("\t ----traitement accompli sans erreur (courbe", i+1, "non tracée)----")
	i+=1

#affiche la matrice des offset dans le terminal pour vérification par l'utilisateur
print('------------------------------------')
if liste_offset[0]=='oui' or liste_offset[0]=='OUI' or liste_offset[0]=='O' or liste_offset[0]=='o':
	if auto_offset[0]=='oui' or auto_offset[0]=='OUI' or auto_offset[0]=='Oui' or auto_offset[0]=='O' or auto_offset[0]=='o':
		print('---> le mode liste des offset est ACTIF et les offset sont:\n', liste_offset)
		print('\n---> le mode auto offset est ACTIF et par conséquent les offset sur Y precedents ne sont par considérés.\n\tVoici la matrice des offset (col1: offsetX, col2: offsetY, col3: courbe):\n', offset)
		titre = titref+'\n offset: ON | auto_offset: ON'
	else:
		print('---> le mode liste des offset est ACTIF et les offset sont:\n', liste_offset)
		print('\n---> le mode auto offset est INACTIF, voici la matrice des offset:\n\t\t(col1: offsetX, col2: offsetY, col3: courbe)\n', offset)
		titre = titref+'\n offset: ON | auto_offset: OFF'
else:
	if auto_offset[0]=='oui' or auto_offset[0]=='OUI' or auto_offset[0]=='Oui' or auto_offset[0]=='O' or auto_offset[0]=='o':
		print('---> le mode liste des offset est INACTIF et les offset sont:\n')
		print('\n---> le mode auto offset est ACTIF, voici la matrice des offset:\n\t(col1: offsetX, col2: offsetY, col3: courbe)\n', offset)
		titre = titref+'\n offset: OFF | auto_offset: ON'
	else:
		print('---> le mode liste des offset est INACTIF et les offset sont:\n')
		print('\n---> le mode auto offset est INACTIF, voici la matrice des offset:\n\tAUCUN OFFSET AJOUTE\n',)
		titre = titref+'\n offset: OFF | auto_offset: OFF'

print('------------------------------------')

#on recupere les max et min pour x et y pour les échelles dans les matrices xscale et yscale
xscale_up=max(xscale[:,0])
xscale_low=min(xscale[:,1])
yscale_up=max(yscale[:,0])
yscale_low=min(yscale[:,1])
		
xdelta=(xscale_up-xscale_low)/100
ydelta=(yscale_up-yscale_low)/100
plt.legend(fontsize=8, loc='best')
plt.title(titre)
plt.axis([xscale_low-xdelta, xscale_up+xdelta, yscale_low-ydelta, yscale_up+ydelta])
plt.xlabel(nom_axe_x)
plt.ylabel(nom_axe_y)
if grille=='oui' or grille=='OUI' or grille == 'Oui' or grille=='o' or grille=='O':
	plt.grid(True)
else:
	plt.grid(False)
	
		
#plt.text(5, 0.000082, '')
plt.savefig(script_dir+titref)
plt.show()