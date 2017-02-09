import sys

def main():
    # parse command line options
	if len(sys.argv) != 3 && len(sys.argv) != 4:
		print('Incorrect number of arguments. Should be "buildarff.py <input.twt> <output.arff> <OPTnumtweets>".')
		sys.exit(2)
	args = sys.argv


