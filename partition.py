import sys

def main():
	# parse command line options
	if len(sys.argv) != 2:
		print('Incorrect number of arguments. Should be "partition.py <input.arff>".')
		sys.exit(2)
	args = sys.argv
	inFileName = args[1]
	inFile = open(inFileName, "r")
	data = inFile.readlines()[25:]

	outFiles = [ open('d'+str(i)+'.txt', 'wb') for i in range(10) ]
	
	#write zeroes
	for i in range(0,10):
		for j in range(0,1000):
			outFiles[i].write(data[(1000*i)+j])

	#write fours
	for i in range(0, 10):
		for j in range(0,1000):
			outFiles[i].write(data[10000+j+(1000*i)])

	for i in range(0, 10):
		outFiles[i].close()

if __name__ == '__main__':
	main()