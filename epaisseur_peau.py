#!/usr/local/bin/python3
#-*-coding:utf-8-*-

#code pour estimer l'épaisseur de peau d'un champ magnétique dans metal

from numpy import *
from scipy import *

#base de données des conductivités
sigma=(['Pb',4.81e6],['Fe',9.93e6],['Co',17.2e6],['Ag', 63e6])
frequences=(1,10,100,1000,10000,100000,1000000)
resultats=zeros((len(sigma)+1, len(frequences)))
elements=[['element'] for x in range(len(sigma))]

i=0
while i<=len(frequences)-1:
	resultats[0,i]=frequences[i]
	i+=1

i=0
j=0
mu0=4*pi*10**(-7)
while i<=len(sigma)-1:
	elements[i]=sigma[i][0]
	while j<=len(frequences)-1:
		resultats[i+1,j]=1000/sqrt(mu0*float(sigma[i][1])*pi*frequences[j])
		j+=1
	j=0
	i+=1

i=0
j=0
while i<=len(sigma)-1:
	while j<=len(frequences)-1:
		print(frequences[j], 'Hz ---> delta', elements[i], '=', resultats[i+1,j], 'mm\n')
		j+=1
	print('-------------------------------------')
	j=0
	i+=1