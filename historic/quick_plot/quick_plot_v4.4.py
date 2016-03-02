#!/usr/local/bin/python3
#-*-coding:utf-8 -*-

#version2: ajout de la fonction offset
#version2.1: modification des legendes. Inclusion de la frequence et amplitude à chaque fois
#version3: ajout de la fonction auto_offset
#version3.1: ajout de liste des courbes à tracer
#version3.2(20151103): ajustement de l'échelle aux courbes tracées uniquement
#version3.3(20151105): permet de traiter des .dat avec des quantités variables de colonnes
#version4.0(20151105): refonte de l'organisation du code source pour corriger certains bugs:
#		les courbes non tracées (non nommées dans tracer() ne sont pas traitées du tout et donc
#		évite certains messages d'erreurs 
#version4.1(20151105): permet de sélectionner des fichiers avec une extension autre que .dat
#version4.2(20151123): permet le choix de l'unité de l'amplitude du signal d'entrée
#version4.3(20151207): correction mineures des informations affichées dans la console
#version4.3(20160113): change la façon de titrer les graphs .png pour permettre un .png par combinaison de courbes tracées

from scipy import *
from pylab import *
import matplotlib.pyplot as plt
import glob, inspect, os

# NE MODIFIER QUE LES VARIABLES ENTRES LES BARRES #
#######################################################
################## PEUT ETRE MODIFIE ##################
##################VVVVVVVVVVVVVVVVVVV##################

extension='.dat' #extension des fichiers à considérer pour tracer les courbes (inclure le .)
delimiteur='' #rien par default
tracer=(0) #pour tout tracer: 0, sinon liste de numeros (1,2,3,5,8,...) représentant l'id du graph dans la matrice offset

#informations relatives aux fichiers de données
data_set_up=5 #nombre de premières lignes ignorées dans le fichier de données .dat
data_set_low=0 #nombre de dernières lignes ignorées dans le fichier de données .dat
data_x_axis=1 #colonne de données correspondant aux abscisses
data_y_axis=4 #colonne de données correspondant aux ordonnées
col_freq=6 #colonne où est indiquée la fréquence des mesures
col_amp=8 #colonne où est indiquée l'amplitude des mesures
unit_amp='V' #unité de l'amplitude du signal en entrée

#informations relatives aux tracés
titref="default title: x-axis --> column " +str(data_x_axis) + " y-axis --> column " +str(data_y_axis) + " of " + extension + " files in folder"
nom_axe_x='Temperature (K)'
nom_axe_y='Magnitude (V)'
grille='oui'

#informations relative au traitement des données
liste_offset=('non',[1,0,0.0003259],[2,0,0.0004807],[3,0,0.00043345],[4,0,0.0003258],[7,0,0.00051]) #si offset[0]='oui', alors offset X =3, offset Y=2 sur courbe 1 et offset X =5, offset Y=3 sur courbe 2
								# le nombre de tuples ne peux pas être supérieur on nombre de .dat dans le dossier
auto_offset=('oui', 0) #pour mettre un offset à toutes les courbes de telle sorte qu'elles commencent toutes
							# au point d'ordonnée indiqué. Cette option est maîtresse sur liste_offset (y seulement).

###/ \#################################################/ \###  ||
##/ | \############### NE PAS MODIFIER ###############/ | \##  ||
#/__°__\#############VVVVVVVVVVVVVVVVVVV#############/__°__\# _||_
															# \  /
															#  \/

script_dir=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+'/' # to get the path to the directory containing the script and the data
liste_fichiers=glob.glob(script_dir+'*'+extension) #list of all .dat files in script_dir
nombre_fichiers=len(liste_fichiers)

#fabrication et initialisation matrice des offsets
offset=array(zeros((nombre_fichiers+1,3)),str)
offset[0,0]='id courbe'
offset[0,1]='offset X'
offset[0,2]='offset Y'
i=1
while i<=nombre_fichiers:
	offset[i,0]=i
	i+=1
	
#définition de la fonction traitement des données relatives aux axes:
def import_axe_data(nom_fichier, delimiteur, data_set_up, data_set_low, data_x_axis, data_y_axis):
	# Import the data from a text file and save as a 2D matrix. Adapter le 'skip_header' au .dat
	print("---> fichier", extension, "en cours de traitement :", nom_fichier)
	return genfromtxt(nom_fichier, delimiter=delimiteur, skip_header=data_set_up, skip_footer=data_set_low, usecols=(data_x_axis-1, data_y_axis-1))#stock que les données utilisées

#définition de la fonction traitement des données relatives aux conditions expérimentales:
def import_exp_data(nom_fichier, delimiteur, data_set_up, data_set_low, col_freq, col_amp):
	matrice_donnees_exp=zeros((2,1)) #stock la fréquence (ligne0) et l'amplitude (ligne1)
	#on utilise genfromtxt à 2 endroits différents du fichier données usecols(col_freq-1 et col_amp-1) car ces colonnes peuvent être de longueur différentes
	matrice_donnees_exp[0] = genfromtxt(nom_fichier, delimiter=delimiteur, skip_header=data_set_up, skip_footer=data_set_low, usecols=(col_freq-1))[0]#stock la fréquence
	matrice_donnees_exp[1] = genfromtxt(nom_fichier, delimiter=delimiteur, skip_header=data_set_up, skip_footer=data_set_low, usecols=(col_amp-1))[0]#stock l'amplitude
	return matrice_donnees_exp

#remplissage de la matrice des offsets si liste_offset[0]=='oui' et auto_offset[0]!='oui'
if liste_offset[0]=='oui' or liste_offset[0]=='OUI' or liste_offset[0]=='O' or liste_offset[0]=='o' and auto_offset[0]!='oui' and auto_offset[0]!='OUI' and auto_offset[0]!='Oui' and auto_offset[0]!='O' and auto_offset[0]!='o':
	nombre_offset=len(liste_offset)-1
	i=1
	while i <=nombre_offset:
		offset[liste_offset[i][0], 1]=liste_offset[i][1] #complète offset (col 2) avec les offset X renseignés dans liste_offset
		offset[liste_offset[i][0], 2]=liste_offset[i][2] #complète offset (col 3) avec les offset Y renseignés dans liste_offset
		i+=1

if type(tracer)==int: #cas où tracer ne contient qu'une seule valeur
	#quand tracer est un int invalide ou nul, alors on trace toutes les courbes
	if tracer>nombre_fichiers or tracer<0 or tracer==0:
		tracer=arange(nombre_fichiers)+1
	else:
		tracer=(tracer, tracer) #on crée une liste de 2 éléments identiques pour que ce soit une liste

elif max(tracer)>nombre_fichiers: #si n° courbe > nombre de fichiers, alors on les trace toutes
	tracer=arange(nombre_fichiers)+1

nombre_courbes=len(set(tracer)) #autant de courbes que d'éléments distincts dans tracer
print(nombre_courbes)
xscale=zeros((nombre_courbes, 2)) #matrice de stockage du X max et du X min
yscale=zeros((nombre_courbes, 2)) #matrice de stockage du Y max et du Y min

i=0
j=0 #pour remplir la matrice des x/yscale
for i in set(tracer): #on traite tous les fichiers distincts donnés par la liste tracer
	#on importe les données à tracer dans la matrice donnees_axes
	print(i)
	donnees_axes=import_axe_data(liste_fichiers[i-1], delimiteur, data_set_up, data_set_low, data_x_axis, data_y_axis)
	#on importe les données des conditions expérimentales dans la matrice donnees_exp
	donnees_exp=import_exp_data(liste_fichiers[i-1], delimiteur, data_set_up, data_set_low, col_freq, col_amp)
			
	if auto_offset[0]=='oui' or auto_offset[0]=='OUI' or auto_offset[0]=='O' or auto_offset[0]=='o':
		auto_offset_i=auto_offset[1]-donnees_axes[0,1]#offset y à appliquer pour la courbe i
		offset[i,2]=auto_offset_i #remplace les offset en y de la matrices par les auto_offset_i
			
	#coordonnées finales des points à tracer
	x = donnees_axes[:,0]+float(offset[i,1])
	y = donnees_axes[:,1]+float(offset[i,2])
			
	# on récupère le max et le min des x et y du i actuel pour déterminer les échelles
	xscale[j,0]=max(x)
	xscale[j,1]=min(x)
	yscale[j,0]=max(y)
	yscale[j,1]=min(y)
	j+=1
			
	#obtention nom fichier sans chemin absolu (trop long)
	#1: on decoupe le chemin vers le fichier .dat en cours de traitement
	decoupage=liste_fichiers[i-1].split('/')
	#découpage est une liste d'éléments de chemin vers le .dat (chaque partie encadrée par / est un element de la liste)
	#2: on prend le dernier element, qui est aussi le nom du fichier de donnees
	if float(offset[i,1])!=0 or float(offset[i,2])!=0:
		label_courbe='graph '+str(i)+' : '+decoupage[len(decoupage)-1]+'\n ---> f='+str(donnees_exp[0,0])+'Hz | Vo='+str(donnees_exp[1,0])+unit_amp+' | offset X='+offset[i,1]+' | offset Y='+offset[i,2]
	else:
		label_courbe='graph '+str(i)+' : '+decoupage[len(decoupage)-1]+'\n ---> f='+str(donnees_exp[0,0])+'Hz | Vo='+str(donnees_exp[1,0])+unit_amp
	
	plt.plot(x,y,label=label_courbe) #on trace la courbe pour i
	print("\t ----traitement accompli sans erreur (courbe", i, "tracée)----")
	
#affiche la matrice des offset dans le terminal pour vérification par l'utilisateur
print('------------------------------------')
if liste_offset[0]=='oui' or liste_offset[0]=='OUI' or liste_offset[0]=='O' or liste_offset[0]=='o':
	if auto_offset[0]=='oui' or auto_offset[0]=='OUI' or auto_offset[0]=='Oui' or auto_offset[0]=='O' or auto_offset[0]=='o':
		print('---> le mode liste des offset est ACTIF et les offset sont:\n', liste_offset)
		print('\n---> le mode auto offset est ACTIF et par conséquent les offset sur Y precedents ne sont par considérés. Voici la matrice des offset:\n', offset)
		titre = titref+'\n offset: ON | auto_offset: ON'
	else:
		print('---> le mode liste des offset est ACTIF et les offset sont:\n', liste_offset)
		print('\n---> le mode auto offset est INACTIF. Aucun offset ajouté:\n', offset)
		titre = titref+'\n offset: ON | auto_offset: OFF'
else:
	if auto_offset[0]=='oui' or auto_offset[0]=='OUI' or auto_offset[0]=='Oui' or auto_offset[0]=='O' or auto_offset[0]=='o':
		print('---> le mode liste des offset est INACTIF\n')
		print('\n---> le mode auto offset est ACTIF. Voici la matrice des offset:\n', offset)
		titre = titref+'\n offset: OFF | auto_offset: ON'
	else:
		print('---> le mode liste des offset est INACTIF et les offset sont:\n')
		print('\n---> le mode auto offset est INACTIF. Aucun offset ajouté:\n', offset)
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
	
		
#pour permettre de créer un .png par combinaison de courbes tracées et axes représentés
titreplt="courbe"

for courbe in set(tracer):
	titreplt+=str(courbe)+"-"
	
titreplt+="Xaxis_col" +str(data_x_axis) + "__Yaxis_col" +str(data_y_axis)
plt.savefig(script_dir+titreplt)
plt.show()