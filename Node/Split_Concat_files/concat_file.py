import sys
import glob
import os
from natsort import natsorted, ns
import binascii

def get_file_length(file):
	fp = open(file,'rb')
	#read the data in the file
	data = fp.read()
	#get the length of the data
	number_of_characters = len(data)
	fp.close()
	return number_of_characters

def split_file(file,nb_parts):
	chunksize = int(get_file_length(file)) / int(nb_parts);
	print(int(chunksize))
	file = open(file,'rb')
	content= file.read()
	with open("inter.txt","wb") as inter:
		inter.write(binascii.hexlify(content))
	part=1
	file.close()
	file = open("inter.txt","r")
        # Read a chunk and continue as long as chunk is non-empty.
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
	read_files = glob.glob("*"+common_name+".txt")
	print(natsorted(read_files, key=lambda y: y.lower()))

	with open("result.txt", "wb") as outfile:
		for f in natsorted(read_files, key=lambda y: y.lower()):
			with open(f, "rb") as infile:
				outfile.write(infile.read())
	hexfile = open("result.txt", "rb")
	hex_content = hexfile.read()
	with open(original_name, "wb") as final:
		final.write(binascii.unhexlify(hex_content))

concatenate_files("_splitText",sys.argv[1],sys.argv[2])

