#!/usr/local/bin/python3
#-*-coding:utf-8 -*-

############### VERSION 2 ###############
#version2: ajout de la fonction offset
#version2.1: modification des legendes. Inclusion de la frequence et amplitude à chaque fois
############### VERSION 3 ###############
#version3: ajout de la fonction auto_offset
#version3.1: ajout de liste des courbes à tracer
#version3.2(20151103): ajustement de l'échelle aux courbes tracées uniquement
#version3.3(20151105): permet de traiter des .dat avec des quantités variables de colonnes
############### VERSION 4 ###############
#version4.0(20151105): refonte de l'organisation du code source pour corriger certains bugs:
#		les courbes non tracées (non nommées dans tracer() ne sont pas traitées du tout et donc
#		évite certains messages d'erreurs 
#version4.1(20151105): permet de sélectionner des fichiers avec une extension autre que .dat
#version4.2(20151123): permet le choix de l'unité de l'amplitude du signal d'entrée
#version4.3(20151207): correction mineures des informations affichées dans la console
#version4.4(20160113): change la façon de titrer les graphs .png pour permettre un .png par combinaison de courbes tracées
#version4.5(20160122): permet la désactivation de l'option print graph in .png
############### VERSION 5 ###############
#version5.0(20160122): permet de tracer plusieurs colonnes d'un même fichier (ou de plusieurs fichiers) sur un même graph
#version5.1(20160205): correction de la matrice donnees_exp qui n'était pas remplie correctement dans le code
#version5.2(20160209): correction erreur lorsque tous les éléments dans 'tracer'>'nombre_fichiers'
#version5.3(20160218): correction erreur dans la génération du titre du .png lorsqu'il faut le créer

############### AMELIORATIONS POSSIBLES ###############
# utilisation de l'option '0' en id courbe pour appliquer offset à toutes les courbes pour la colonne souhaitée
# utilisation de la fonction interpolation de scipy pour manipuler des fonctions plutôt que des matrices de données
# proposer différentes options pour tracer des courbes: nuage de points, lignes, couleurs différentes ou formes différentes, ...

from scipy import *
from pylab import *
import matplotlib.pyplot as plt
import glob, inspect, os

# NE MODIFIER QUE LES VARIABLES ENTRES LES BARRES #
#######################################################
################## PEUT ETRE MODIFIE ##################
##################VVVVVVVVVVVVVVVVVVV##################

extension='.dat'	#extension des fichiers à considérer pour tracer les courbes (inclure le .)
print_graph='non'	#'oui'/'non' pour générer ou non une copie .png
delimiteur=''		#rien par default
tracer=[0]			#tout tracer: 0, sinon liste [1,2,3,5,8,...] AVEC CROCHETS

#informations relatives aux fichiers de données
data_set_up=5	#nombre de premières lignes ignorées dans le fichier de données .dat
data_set_low=0	#nombre de dernières lignes ignorées dans le fichier de données .dat
data_x_axis=1	#colonne de données correspondant aux abscisses
data_y_axis=[4]	#colonne(s) de données correspondant aux ordonnées (garder les crochets)
col_freq=6		#colonne où est indiquée la fréquence des mesures
col_amp=8		#colonne où est indiquée l'amplitude des mesures
unit_amp='V'	#unité de l'amplitude du signal en entrée

#informations relatives aux tracés
titref="default title: x-axis --> column " +str(data_x_axis) + " y-axis --> column " +str(data_y_axis) + " of " + extension + " files in folder"
nom_axe_x='Temperature (K)'
nom_axe_y='Magnitude (V)'
grille='oui'

#informations relative au traitement des données
liste_offset=['non',(2,2,3,2),(2,3,0,3)] #si offset[0]='oui', 1er chiffre du tuple --> id courbe, 2e --> id colonne, 3e --> offset X, 4e --> offset Y
								# le nombre de tuples ne peux pas être supérieur on nombre de .dat dans le dossier
auto_offset=('non', 0) #pour mettre un offset à toutes les courbes de telle sorte qu'elles commencent toutes
							# au point d'ordonnée indiqué. Cette option est maîtresse sur liste_offset (y seulement).

###/ \#################################################/ \###  ||
##/ | \############### NE PAS MODIFIER ###############/ | \##  ||
#/__°__\#############VVVVVVVVVVVVVVVVVVV#############/__°__\# _||_
															# \  /
															#  \/

# supprime les doublons dans tracer et data_y_axis s'il y a
tracer=list(set(tracer))
data_y_axis=list(set(data_y_axis))
liste_offset=list(set(liste_offset))

script_dir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+'/'	# to get the path to the directory containing the script and the data
liste_fichiers=glob.glob(script_dir+'*'+extension)	#list of all .dat files in script_dir

######## VARIABLES DES QUANTITES A TRACER ########	
nombre_fichiers=len(liste_fichiers)	#number of files in directory
nombre_colonnes=len(data_y_axis)	#number of columns to plot


######## OPERATION SUR TRACER ########
# si 'tracer' ne contient que des éléments > nombre_fichiers ou < 0, alors on trace tout par défaut (i.e. on ajoute 0 à 'tracer')
if min(tracer)>nombre_fichiers or max(tracer)<0:
	tracer+=[0]
# on sort de tracer tous les éléments >nombre_fichiers et <0
if max(tracer)>nombre_fichiers:
	while max(tracer)>nombre_fichiers:
		tracer.remove(max(tracer))
if min(tracer)<0:
	while min(tracer)<0:
		tracer.remove(min(tracer))

# si 0 dans tracer, on trace toutes les courbes
if 0 in tracer:
	tracer=list(arange(nombre_fichiers)+1)
	
nombre_courbes=len(tracer)			#number of files to plot
	
######## AFFICHAGE INFO ########	
print('---> '+str(nombre_courbes)+' '+extension+' to plot')
print('---> '+str(nombre_colonnes)+' columns to plot per '+extension)
	
######## COLONNES A TRACER ########
plot_cols=[data_x_axis-1]	# creates the list of the columns that must be ploted with the x column
	
for i in data_y_axis:	# adds the other columns that must be ploted
	plot_cols.append(i-1)

######## DEFINITION FONCTIONS TRAITEMENT ########
# fonction importation des données des axes à tracer:
def import_axe_data(nom_fichier, delimiteur, data_set_up, data_set_low, plot_cols):
	# Import the data from a text file and save as a 2D matrix. Adapter le 'skip_header' au .dat
	print("---> fichier", extension, "en cours de traitement :", nom_fichier) 
	return genfromtxt(nom_fichier, delimiter=delimiteur, skip_header=data_set_up, skip_footer=data_set_low, usecols=plot_cols)#stock que les données utilisées
	
# fonction importation des données relatives aux conditions expérimentales:
def import_exp_data(nom_fichier, delimiteur, data_set_up, data_set_low, col_freq, col_amp):
	matrice_donnees_exp=zeros((2,1)) #stock la fréquence (ligne0) et l'amplitude (ligne1)
	#on utilise genfromtxt à 2 endroits différents du fichier données usecols(col_freq-1 et col_amp-1) car ces colonnes peuvent être de longueur différentes
	matrice_donnees_exp[0] = genfromtxt(nom_fichier, delimiter=delimiteur, skip_header=data_set_up, skip_footer=data_set_low, usecols=(col_freq-1))[0]#stock la fréquence
	matrice_donnees_exp[1] = genfromtxt(nom_fichier, delimiter=delimiteur, skip_header=data_set_up, skip_footer=data_set_low, usecols=(col_amp-1))[0]#stock l'amplitude
	return matrice_donnees_exp
	
######## REMPLISSAGE LISTE DE MATRICES DONNEES ########
donnees=[]	# initialisation de la liste des matrices de données des courbes à tracer
# autant de matrices sont crées qu'il y a de courbes à tracer et elles sont rangées dans donnees
# pour accéder à la matrice d'une courbe: donnees[tracer.index(i)]
for i in tracer: 
	donnees.append(import_axe_data(liste_fichiers[i-1], delimiteur, data_set_up, data_set_low, plot_cols))	

######## SI IL FAUT AJOUTER UN OU DES OFFSET ########
#fabrication et initialisation matrice des offsets
offset=array(zeros((len(tracer)+1,nombre_colonnes+2)),str)	# crée une matrice de nombre de courbes à tracer +1 lignes et nombre de colonnes à tracer +2 colonnes
offset[0,0]='id courbe'	# titre 1ere colonne
offset[0,1]='offset X'	# titre 2e colonne
for i in data_y_axis:
	offset[0,data_y_axis.index(i)+2]='offset Y'+str(i)	# titre des autres colonnes
	
for i in tracer:
	offset[tracer.index(i)+1,0]=i	#remplit l'id fichier dans chacunes des matrices offset

# cas où liste_offset[0]=='oui' et auto_offset[0]!='oui'
if ('oui' in liste_offset or 'Oui' in liste_offset or 'OUI' in liste_offset or 'O' in liste_offset or 'o' in liste_offset) and ('oui' not in auto_offset and 'Oui' not in auto_offset and 'OUI' not in auto_offset and 'O' not in auto_offset and 'o' not in auto_offset):
	for i in liste_offset[1:]:
		if (i[0] in tracer) and (i[1] in data_y_axis):		# seulement si demandé dans data_y_axis et tracer
			offset[tracer.index(i[0])+1,1]=i[2]	# remplit offset X
			offset[tracer.index(i[0])+1,data_y_axis.index(i[1])+2]=i[3]	# remplit offset Y pour la colonne donnée par i[1]

# cas où auto_offset[0]=='oui'
if 'oui' in auto_offset or 'Oui' in auto_offset or 'OUI' in auto_offset or 'O' in auto_offset or 'o' in auto_offset:
	for i in tracer:		# pour chacune des courbes à tracer (indiquées dans tracer)
		for j in data_y_axis:	# pour chaque colonne à tracer (EXCLUANT X)
			# on change les offset en y seulement dans la matrice offset
			offset[tracer.index(i)+1,data_y_axis.index(j)+2]= auto_offset[1]-donnees[tracer.index(i)][0][data_y_axis.index(j)+1]
			
######## AJOUT OFFSET AUX DONNEES ########
donnees_off=donnees	# duplication de donnees pour creer donnees_off qui est la matrice des données avec offset
# il faut maintenant ajouter les offset à donnees_off si nécessaire (i.e. si offset ou auto_offset est 'oui')
if ('oui' in liste_offset or 'Oui' in liste_offset or 'OUI' in liste_offset or 'O' in liste_offset or 'o' in liste_offset) or ('oui' in auto_offset or 'Oui' in auto_offset or 'OUI' in auto_offset or 'O' in auto_offset or 'o' in auto_offset):
	for i in tracer:
		donnees_off_temp=array(donnees_off[tracer.index(i)])	# étape nécessaire pour manipuler les objets de la liste donnees_off comme de vraies matrices et permettre les sommes sur les colonnes/lignes
		for j in plot_cols:
			donnees_off_temp[:,plot_cols.index(j)]+=float(offset[tracer.index(i)+1,plot_cols.index(j)+1])	# on travaille sur donnees_off_temp qui est de type array et permet donc les sommes sur ligne/colonne entière
			donnees_off[tracer.index(i)]=donnees_off_temp	# on remplace la matrice de la courbe i par les données avec offset
# exemple pour sommer sur colonnes :
#>>> A
#array([[1, 1, 1],
#       [2, 2, 2],
#       [3, 3, 3]])
#>>> B=A
#>>> B[:,0]=B[:,0]+4	# ou bien B[:,0]+=4
#>>> B
#array([[5, 1, 1],
#       [6, 2, 2],
#       [7, 3, 3]])

######## OPERATION SUR LES AXES ########
# création des 2 matrices de stockage des échelles (une pour x et l'autre pour y)
xscale=zeros((nombre_courbes, 2))	# matrice des X min et max pour chaque fichier à tracer
yscale=zeros((nombre_courbes, nombre_colonnes, 2))	# matrices des Y min et max de chaque colonnes à tracer pour chaque fichier
# xscale=	[[xmin_courbe1, xmax_courbe1],
#			 [xmin_courbe4, xmax_courbe4],
#			 [xmin_courbe3, xmax_courbe3],...] si tracer=[1,4,3,...]

# yscale=	[[[y1min_courbe1, y1max_courbe1],[y3min_courbe1, y3max_courbe1]],
#			 [[y1min_courbe4, y1max_courbe4],[y3min_courbe4, y3max_courbe4]],
#			 [[y1min_courbe3, y1max_courbe3],[y3min_courbe3, y3max_courbe3]],...] si tracer=[1,4,3,...] et data_y_axis=[1,3]

# remplissage matrices échelles
for i in tracer:	# on traite fichier par fichier
	# on remplit xscale
	xscale[tracer.index(i),0]=min(array(donnees_off[tracer.index(i)])[:,0])
	xscale[tracer.index(i),1]=max(array(donnees_off[tracer.index(i)])[:,0])
	# on remplit yscale
	for j in data_y_axis:
		yscale[tracer.index(i),data_y_axis.index(j),0]=min(array(donnees_off[tracer.index(i)])[:,data_y_axis.index(j)+1])
		yscale[tracer.index(i),data_y_axis.index(j),1]=max(array(donnees_off[tracer.index(i)])[:,data_y_axis.index(j)+1])
	
######## TRAÇAGE COURBES ########			
for i in tracer:
	#on importe les données des conditions expérimentales dans la matrice donnees_exp
	donnees_exp=import_exp_data(liste_fichiers[i-1], delimiteur, data_set_up, data_set_low, col_freq, col_amp)
	#obtention nom fichier sans chemin absolu (trop long)
	#1: on decoupe le chemin vers le fichier .dat en cours de traitement
	decoupage=liste_fichiers[i-1].split('/')	# decoupage est une liste d'éléments de chemin vers le .dat (chaque partie encadrée par / est un element de la liste)
	# coordonnées en X
	x = array(donnees_off[tracer.index(i)])[:,0]
	for j in data_y_axis:
		# coordonnées en Y
		y = array(donnees_off[tracer.index(i)])[:,data_y_axis.index(j)+1]
		# la suite sert à indiquer s'il y a un ou plusieurs offset sur la courbe en cours de traçage et de nommer les courbes en fonction
		if float(offset[tracer.index(i)+1,1])!=0 or float(offset[tracer.index(i)+1,data_y_axis.index(j)+2])!=0:
			label_courbe='graph '+str(tracer.index(i)+1)+'(col '+str(j)+'): '+decoupage[len(decoupage)-1]+'\n ---> f='+str(donnees_exp[0,0])+'Hz | Vo='+str(donnees_exp[1,0])+unit_amp+' | offset X='+offset[tracer.index(i)+1,1]+' | offset Y'+str(j)+'='+offset[tracer.index(i)+1,data_y_axis.index(j)+2]
		else:
			label_courbe='graph '+str(tracer.index(i)+1)+'(col '+str(j)+'): '+decoupage[len(decoupage)-1]+'\n ---> f='+str(donnees_exp[0,0])+'Hz | Vo='+str(donnees_exp[1,0])+unit_amp
	
		plt.plot(x,y,label=label_courbe) #on trace la courbe pour i
		print("\t ----traitement accompli sans erreur (courbe", i, "|colonne", j, "tracée)----")	
	
	
	
	
#affiche la matrice des offset dans le terminal pour vérification par l'utilisateur
print('------------------------------------')
if 'oui' in liste_offset or 'Oui' in liste_offset or 'OUI' in liste_offset or 'O' in liste_offset or 'o' in liste_offset:
	if 'oui' in auto_offset or 'Oui' in auto_offset or 'OUI' in auto_offset or 'O' in auto_offset or 'o' in auto_offset:
		print('---> le mode liste des offset est ACTIF et les offset sont:\n', liste_offset)
		print('\n---> le mode auto offset est ACTIF et par conséquent les offset sur Y precedents ne sont par considérés.')
		print('\n---> matrice offset:\n', offset)
		titre = titref+'\n offset: ON | auto_offset: ON'
	else:
		print('---> le mode liste des offset est ACTIF et les offsets sont:\n', liste_offset)
		print('\n---> le mode auto offset est INACTIF.')
		print('\n---> matrice offset:\n', offset)
		titre = titref+'\n offset: ON | auto_offset: OFF'
else:
	if 'oui' in auto_offset or 'Oui' in auto_offset or 'OUI' in auto_offset or 'O' in auto_offset or 'o' in auto_offset:
		print('---> le mode liste des offset est INACTIF. Le mode auto offset est ACTIF.')
		print('\n---> matrice offset:\n', offset)
		titre = titref+'\n offset: OFF | auto_offset: ON'
	else:
		print('---> le mode liste des offset est INACTIF. Le mode auto offset est INACTIF.')
		print('\n---> matrice offset:\n', offset)
		titre = titref+'\n offset: OFF | auto_offset: OFF'

print('------------------------------------')

# on récupère les min et max pour x
xscale_up=max(xscale[:,1])
xscale_low=min(xscale[:,0])
# on récupère les min et max pour y pour toutes les colonnes
# mais pour cela il faut tester pour chaque fichier et colonne
yscale_low=[]
yscale_up=[]
for i in tracer:
	yscale_low.append(min(yscale[tracer.index(i),:,0]))
	yscale_up.append(max(yscale[tracer.index(i),:,1]))
	
# et on prend le min et max de yscale_low/up
yscale_low=min(yscale_low)
yscale_up=max(yscale_up)

#### ICI
		
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
	
if print_graph=='oui' or print_graph=='OUI' or print_graph == 'Oui' or print_graph=='o' or print_graph=='O':		
#pour permettre de créer un .png par combinaison de courbes tracées et axes représentés
	titreplt="courbe"
	for i in tracer:
		titreplt+=str(i)+"-"
	titreplt+="Xaxis_col" +str(data_x_axis) +"__Yaxis_col"
	for j in data_y_axis:
		titreplt+=str(j)
	plt.savefig(script_dir+titreplt)

plt.show()