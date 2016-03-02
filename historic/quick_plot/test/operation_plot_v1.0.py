#!/usr/local/bin/python3
#-*-coding:utf-8 -*-

############### FONCTION ###############
#le but de ce script est d'effectuer des opérations sur des courbes; elle permet de soustraire 
#à un .dat, un autre .dat pour s'affranchir des certain phénomènes parasites de fond

############### VERSION 1 ###############
#version 1.0 (2016/02/05): création du script

############### AMELIORATIONS ###############
#intégration de ce code dans quick_plot en indiquant quelle courbe opère sur toutes les autres

# on reprend la même base que quick_plot, mais on va interpoler les données pour manipuler plus simplement
from numpy import *
from scipy import *
from scipy.interpolate import interp1d
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
inter='linear'		#type de l'interpolation sur les données ('linear' ou 'cubic'). 'cubic' est beaucoup plus long
tracer=3			#tracer la courbe indiquée
background=1		#courbe qui va agir sur tracer
action='-'			#quelle action 'background' opère sur les 'tracer' (+,-,/,*)

#informations relatives aux fichiers de données
data_set_up=5	#nombre de premières lignes ignorées dans le fichier de données .dat
data_set_low=0	#nombre de dernières lignes ignorées dans le fichier de données .dat
data_x_axis=1	#colonne de données correspondant aux abscisses
data_y_axis=4	#colonne de données correspondant aux ordonnées
col_freq=6		#colonne où est indiquée la fréquence des mesures
col_amp=8		#colonne où est indiquée l'amplitude des mesures
unit_amp='V'	#unité de l'amplitude du signal en entrée

#informations relatives aux tracés
titref="default title: x-axis --> column " +str(data_x_axis) + " y-axis --> column " +str(data_y_axis) + " of " + extension + " files in folder"
nom_axe_x='Temperature (K)'
nom_axe_y='Magnitude (V)'
grille='oui'

#informations relative au traitement des données
liste_offset=['non',(3,2),(0,1)] #si offset[0]='oui', 1er chiffre du tuple --> offset X, 2e --> offset Y. 1er tuple pour 'tracer' et 2e tuple pour 'background'
								# le nombre de tuples ne peux pas être supérieur on nombre de .dat dans le dossier
auto_offset=('oui', 0) #pour mettre un offset à toutes les courbes de telle sorte qu'elles commencent toutes
							# au point d'ordonnée indiqué. Cette option est maîtresse sur liste_offset (y seulement).

###/ \#################################################/ \###  ||
##/ | \############### NE PAS MODIFIER ###############/ | \##  ||
#/__°__\#############VVVVVVVVVVVVVVVVVVV#############/__°__\# _||_
															# \  /
															#  \/

script_dir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+'/'	# to get the path to the directory containing the script and the data
liste_fichiers=glob.glob(script_dir+'*'+extension)	#list of all .dat files in script_dir
	
nombre_fichiers=len(liste_fichiers)	#number of files in directory
	
######## AFFICHAGE INFO ########	
print('--> plot '+str(tracer)+' '+str(action)+' '+str(background)+' on column 4')
	
######## DEFINITION FONCTIONS TRAITEMENT ########
# fonction importation des données des axes à tracer:
def import_axe_data(nom_fichier, delimiteur, data_set_up, data_set_low, data_x_axis, data_y_axis):
	# Import the data from a text file and save as a 2D matrix. Adapter le 'skip_header' au .dat
	print("---> fichier", extension, "en cours de traitement :", nom_fichier) 
	return genfromtxt(nom_fichier, delimiter=delimiteur, skip_header=data_set_up, skip_footer=data_set_low, usecols=(data_x_axis, data_y_axis))#stock que les données utilisées
	
# fonction importation des données relatives aux conditions expérimentales:
def import_exp_data(nom_fichier, delimiteur, data_set_up, data_set_low, col_freq, col_amp):
	matrice_donnees_exp=zeros((2,1)) #stock la fréquence (ligne0) et l'amplitude (ligne1)
	#on utilise genfromtxt à 2 endroits différents du fichier données usecols(col_freq-1 et col_amp-1) car ces colonnes peuvent être de longueur différentes
	matrice_donnees_exp[0] = genfromtxt(nom_fichier, delimiter=delimiteur, skip_header=data_set_up, skip_footer=data_set_low, usecols=(col_freq-1))[0]#stock la fréquence
	matrice_donnees_exp[1] = genfromtxt(nom_fichier, delimiter=delimiteur, skip_header=data_set_up, skip_footer=data_set_low, usecols=(col_amp-1))[0]#stock l'amplitude
	return matrice_donnees_exp

######## REMPLISSAGE DES MATRICES DE DONNEES ########
donnees_tracer=import_axe_data(liste_fichiers[tracer-1], delimiteur, data_set_up, data_set_low, data_x_axis-1, data_y_axis-1)
donnees_background=import_axe_data(liste_fichiers[background-1], delimiteur, data_set_up, data_set_low, data_x_axis-1, data_y_axis-1)

######## INTERVALLES DE TRACAGE X ########
#intersection des intervalles X de 'background' et de 'tracer'
intervalle_x=array([max(min(donnees_tracer[:,0]),min(donnees_background[:,0])),min(max(donnees_tracer[:,0]),max(donnees_background[:,0]))])

#matrice contenant tous les points x pour les fonctions interpolées
x=linspace(min(intervalle_x), max(intervalle_x), num=int((max(intervalle_x)-min(intervalle_x))/0.005), endpoint=True)

######## INTERPOLATION ########
#interpolation de 'background'
fonction_background=interp1d(donnees_background[:,0], donnees_background[:,1], kind=inter)
#interpolation de 'tracer'
fonction_tracer=interp1d(donnees_tracer[:,0], donnees_tracer[:,1], kind=inter)

######## MATRICE OFFSET ########
#fabrication et initialisation matrice des offsets
offset=array(zeros((3,3)),str)	# stocke les offset de 'background' et 'tracer'
offset[0,0]='id courbe'	# titre 1ere colonne
offset[0,1]='offset X'	# titre 2e colonne
offset[0,2]='offset Y'	# titre 3e colonne
offset[1,0]=str(tracer)+' (modified)'
offset[2,0]=str(background)+' (background)'

if 'oui' in liste_offset or 'Oui' in liste_offset or 'OUI' in liste_offset or 'O' in liste_offset or 'o' in liste_offset:
	#on remplit les offset sur X
	offset[1,1]=liste_offset[1][0]
	offset[2,1]=liste_offset[2][0]
	#auto_offset[0]='oui'
	if 'oui' in auto_offset or 'Oui' in auto_offset or 'OUI' in auto_offset or 'O' in auto_offset or 'o' in auto_offset:
		offset[1,2]=auto_offset[1]-donnees_tracer[0,1]	
		offset[2,2]=auto_offset[1]-donnees_background[0,1]
		#on peut aussi choisir de remplacer donnees_tracer[0,1] (ou donnees_background[0,1]) par le Y en Xmax. Dans ce cas on utilisera:
		#float(donnees_tracer[where(donnees_tracer==max(donnees_tracer[:,0]))[0],1])
		#donnees_[where(donnees_==max(donnees_[:,0]))[0],1] --> donne l'ordonnée à l'abscisse maximale (where est une fonction de numpy)
	#cas où auto_offset[0]!='oui'
	else:
		# on change les offset en y seulement dans la matrice offset
		offset[1,2]= liste_offset[1][1]
		offset[2,2]= liste_offset[2][1]
elif 'oui' in auto_offset or 'Oui' in auto_offset or 'OUI' in auto_offset or 'O' in auto_offset or 'o' in auto_offset:
	offset[1,2]=auto_offset[1]-donnees_tracer[0,1]
	offset[2,2]=auto_offset[1]-donnees_background[0,1]

######## DONNEES ET TRACAGE ########
#données expérimentales
donnees_exp_tracer=import_exp_data(liste_fichiers[tracer-1], delimiteur, data_set_up, data_set_low, col_freq, col_amp)
donnees_exp_background=import_exp_data(liste_fichiers[background-1], delimiteur, data_set_up, data_set_low, col_freq, col_amp)

#obtention nom fichier sans chemin absolu (trop long)
decoupage_tracer=liste_fichiers[tracer-1].split('/')	# decoupage est une liste d'éléments de chemin vers le .dat (chaque partie encadrée par / est un element de la liste)
decoupage_background=liste_fichiers[background-1].split('/')

#label des courbes pour 'tracer' et 'background'
if float(offset[1,1])!=0 or float(offset[1,2])!=0:
	label_tracer='graph '+str(1)+'(col '+str(data_y_axis)+'): '+decoupage_tracer[len(decoupage_tracer)-1]+'\n ---> f='+str(donnees_exp_tracer[0,0])+'Hz | Vo='+str(donnees_exp_tracer[1,0])+unit_amp+' | offset X='+offset[1,1]+' | offset Y='+offset[1,2]
else:
	label_tracer='graph '+str(1)+'(col '+str(data_y_axis)+'): '+decoupage_tracer[len(decoupage_tracer)-1]+'\n ---> f='+str(donnees_exp_tracer[0,0])+'Hz | Vo='+str(donnees_exp_tracer[1,0])+unit_amp

if float(offset[2,1])!=0 or float(offset[2,2])!=0:
	label_background='graph '+str(1)+'(col '+str(data_y_axis)+'): '+decoupage_background[len(decoupage_background)-1]+'\n ---> f='+str(donnees_exp_background[0,0])+'Hz | Vo='+str(donnees_exp_background[1,0])+unit_amp+' | offset X='+offset[2,1]+' | offset Y='+offset[2,2]
else:
	label_background='graph '+str(1)+'(col '+str(data_y_axis)+'): '+decoupage_background[len(decoupage_background)-1]+'\n ---> f='+str(donnees_exp_background[0,0])+'Hz | Vo='+str(donnees_exp_background[1,0])+unit_amp

#données pour le traçage de 'tracer'
donnees_tracer_off=donnees_tracer
donnees_tracer_off[:,0]+=float(offset[1,1])
donnees_tracer_off[:,1]+=float(offset[1,2])

#données pour le traçage de 'background'
donnees_background_off=donnees_background
donnees_background_off[:,0]+=float(offset[2,1])
donnees_background_off[:,1]+=float(offset[2,2])

#données 'tracer' avec l'action 'action' de 'background' mais sur l'intervalle x seulement et 'offseté' à Y=0 en Xmax
if action=='+':
	offset_add=fonction_tracer(max(x))+fonction_background(max(x))
	y=fonction_tracer(x)+fonction_background(x)-offset_add
	label_modifie='graph '+str(3)+'(col '+str(data_y_axis)+'): '+' graph1 + graph2'
elif action=='-':
	offset_add=fonction_tracer(max(x))-fonction_background(max(x))
	y=fonction_tracer(x)-fonction_background(x)-offset_add
	label_modifie='graph '+str(3)+'(col '+str(data_y_axis)+'): '+' graph1 - graph2'
elif action=='/':
	offset_add=fonction_tracer(max(x))/fonction_background(max(x))
	y=fonction_tracer(x)/fonction_background(x)-offset_add
	label_modifie='graph '+str(3)+'(col '+str(data_y_axis)+'): '+' graph1 / graph2'
elif action=='*':
	offset_add=fonction_tracer(max(x))*fonction_background(max(x))
	y=fonction_tracer(x)*fonction_background(x)-offset_add
	label_modifie='graph '+str(3)+'(col '+str(data_y_axis)+'): '+' graph1 * graph2'
else:
	offset_add=fonction_tracer(max(x))
	y=fonction_tracer(x)-offset_add
	label_modifie='graph '+str(3)+'(col '+str(data_y_axis)+'): '+' graph1'
		
plt.plot(donnees_tracer_off[:,0],donnees_tracer_off[:,1],label=label_tracer) #on trace la courbe de 'tracer'
print("\t ----traitement accompli sans erreur (courbe", tracer, "|colonne", data_y_axis, "tracée)----")

plt.plot(donnees_background_off[:,0],donnees_background_off[:,1],label=label_background) #on trace la courbe de 'background'
print("\t ----traitement accompli sans erreur (courbe", background, "|colonne", data_y_axis, "tracée)----")

plt.plot(x,y,label=label_modifie) #on trace la courbe de 'tracer' 'action' 'background'
print("\t ----traitement accompli sans erreur (courbe ", tracer, action, background, "|colonne", data_y_axis, "tracée)----")

######## GESTION DES ECHELLES DES AXES ########
#2 matrices de stockage des échelles (une pour x et l'autre pour y) avec min en col 0 et max en col 1
xscale=array([min(min(donnees_tracer_off[:,0]),min(donnees_background_off[:,0])),max(max(donnees_tracer_off[:,0]),max(donnees_background_off[:,0]))])
yscale=array([min(min(donnees_tracer_off[:,1]),min(donnees_background_off[:,1]),min(y)),max(max(donnees_tracer_off[:,1]),max(donnees_background_off[:,1]),max(y))])


print('min(donnees_tracer_off[:,0]),min(donnees_background_off[:,0])')
print(min(donnees_tracer_off[:,0]),min(donnees_background_off[:,0]))
print('max(donnees_tracer_off[:,0]),max(donnees_background_off[:,0])')
print(max(donnees_tracer_off[:,0]),max(donnees_background_off[:,0]))
print('min(donnees_tracer_off[:,1]),min(donnees_background_off[:,1]),min(y)')
print(min(donnees_tracer_off[:,1]),min(donnees_background_off[:,1]),min(y))
print('max(donnees_tracer_off[:,1]),max(donnees_background_off[:,1]),max(y)')
print(max(donnees_tracer_off[:,1]),max(donnees_background_off[:,1]),max(y))

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

#on récupère les min et max pour x
xscale_low=min(xscale)
xscale_up=max(xscale)
#on récupère les min et max pour y
yscale_low=min(yscale)
yscale_up=max(yscale)
print('xscale_low,xscale_up')
print(xscale_low,xscale_up)
print('yscale_low,yscale_up')
print(yscale_low,yscale_up)
	
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
	titreplt="courbe"+tracer+" et "+background+ " et courbe"+tracer+action+background+ "| colonne"+data_y_axis
	plt.savefig(script_dir+titreplt)

plt.show()