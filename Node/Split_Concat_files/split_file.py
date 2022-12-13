import sys
import glob
import os
from natsort import natsorted, ns
import binascii

def get_file_length(file):
	fp = open(file,'rb')
	#Lire les donnees du fichier
	data = fp.read()
	#Avoir la taille du fichier
	number_of_characters = len(data)
	fp.close()
	return number_of_characters

def split_file(file,nb_parts):
	#Diviser la longeur du fichier su le nombre de noeuds ayant le fichier a telecharger pour avoir la taille dun bloc a telecharger d'un noeud
	chunksize = int(get_file_length(file)) / int(nb_parts)
	print(int(chunksize))

	#Transformer le fichier en fome hexadecimale pour ne pas avoir des problemes pour les unprintable characters
	file = open(file,'rb')
	content= file.read()
	with open("inter.txt","wb") as inter:
		inter.write(binascii.hexlify(content))
	part=1
	file.close()

	# Lire un bloc tant qu'il n'est pas vide et le mettre dans un fichier
	file = open("inter.txt","r")
	while (chunk := file.read(int(chunksize*2))):
		outfile = open(str(part)+ "_splitText.txt", 'w')
		if outfile.write(chunk) != len(chunk):
			print('write error')
			break
		outfile.close()
		part += 1
	file.close()
	os.system('rm inter.txt TP*')

def concatenate_files(common_name,nb_parts,original_name):
	#lire les fichiers separes
	read_files = glob.glob("*"+common_name+".txt")
	print(natsorted(read_files, key=lambda y: y.lower()))

	#concatener les fichiers
	with open("result.txt", "wb") as outfile:
		for f in natsorted(read_files, key=lambda y: y.lower()):
			with open(f, "rb") as infile:
				outfile.write(infile.read())

	#Transformer le fichier de l'hexadecimal au code ascii
	hexfile = open("result.txt", "rb")
	hex_content = hexfile.read()
	with open(original_name, "wb") as final:
		final.write(binascii.unhexlify(hex_content))

os.system('rm *splitText*')
split_file(sys.argv[2],sys.argv[1])

