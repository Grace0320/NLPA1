import sys
import re

#regex patterns from files
slangPattern = ""
firstPPattern = ""
secondPPattern = ""
thirdPPattern = ""

#regex patterns for verbs
#modals for future tense
# MD (not|n't)? VB (VBG|VBN)? (PRP|PRP$ VBG)? 
# possible adverbs with verbs
# eg will be taking them swimming
# eg will not have taken them swimming
# special case: need to VB (PRP VB)?
futurePattern = "\w*\/MD(( not| n't)\/RB)?( \w*\/RB)* \w*\/VB ((\w*\/VBG |(\w*\/VBN)) (\w*\/(PRP|PRP\$) \w*\/VBG)?)?"
futureNeedPattern = "need (to/TO|2/NN) \w*\/VB (\w*(\/VBG|\/VBN))?"

#past tense
pastPattern = "\w*(?<!MD) ((\w*\/VB( \w*\/RB)* \w*\/VBN)|(\w*\/VBD ((( \w*\/RB)* (\w*\/VBG|\w*\/VBN)?)|(\w*\/TO( \w*\/RB)* \w*\/VB))?))"

### input: tweet
### output: dict with kv pairs as follows ((token, tag) : numOccurrences)
def getTokenTagFreqDict(tweet):
	POSDict = {}

	#discard A=
	lines = tweet.split("\n")
	for line in lines[1:]:
		tokens = line.split()
		for t in tokens:
			w = t.split("/")
			if (w[0], w[1]) in POSDict:
				POSDict[(w[0],w[1])] += 1
			else:
				POSDict[(w[0],w[1])] = 1
	return POSDict

### input: tweet
### output: dict with kv pairs as follows (token : numOccurrences)
def getTokenOnlyFreqDict(tweet):
	freqDict = {}
	#discard A=
	lines = tweet.split("\n")
	for line in lines[1:]:
		tokens = line.split()
		for t in tokens:
			w = t.split("/")
			if w[0] in freqDict:
				freqDict[w[0]] += 1
			else:
				freqDict[w[0]] = 1
	return freqDict

### input: tweet
### output: dict with kv pairs as follows (POS Tag : numOccurrences)
def getTagOnlyFreqDict(tweet):
	freqDict = {}
	#discard A=
	lines = tweet.split("\n")
	for line in lines[1:]:
		tokens = line.split()
		for t in tokens:
			w = t.split("/")
			if w[1] in freqDict:
				freqDict[w[1]] += 1
			else:
				freqDict[w[1]] = 1
	return freqDict

### input: tweet, list of POS tags; eg ["(", ")"]
### output: num occurences of all POS tags in list in tweet
def getCountPOS(tweet, tagList):
	freqDict = getTagOnlyFreqDict(tweet)
	count = 0
	for tag in tagList:
		if tag in freqDict:
			count += freqDict[tag]
	return count 

### input: fileName
### output: regex ready pattern of OR'd wordlist eg "^(lmao|omg|lol)$"
def loadWordList(fileName):
	f = open(fileName, 'r')
	listWords = f.readlines()
	pattern = "^("
	lim = len(listWords)
	for i in range(0, lim):
		pattern +=listWords[i].strip('. \n\t')
		if i < lim - 1:
			pattern += r'|'
	pattern += ")$"
	return pattern

def feat1(tweet): #first person pronouns
	posDict = getTokenTagFreqDict(tweet)
	count = 0
	for token, tag in posDict:
		if tag == "PRP" or tag == "PRP$":
			if re.search("^" + firstPPattern + "$", token):
				count += posDict[(token, tag)]
	return count

def feat2(tweet): #second person pronouns
	posDict = getTokenTagFreqDict(tweet)
	count = 0
	for token, tag in posDict:
		if tag == "PRP" or tag == "PRP$":
			if re.search("^" + secondPPattern + "$", token):
				count += posDict[(token, tag)]
	return count

def feat3(tweet): #third person pronouns
	posDict = getTokenTagFreqDict(tweet)
	count = 0
	for token, tag in posDict:
		if tag == "PRP" or tag == "PRP$":
			if re.search("^" + thirdPPattern + "$", token):
				count += posDict[(token, tag)]
	return count

def feat4(tweet): #coordinating conjunctions
	return getCountPOS(tweet, ["CC"])

def feat5(tweet): # past tense verbs
	return len(re.findall(pastPattern, tweet))

def feat6(tweet): #future tense verbs
	count = 0;
	count += len(re.findall(futurePattern, tweet))
	count += len(re.findall(futureNeedPattern, tweet, re.IGNORECASE))
	return count

def feat7(tweet): #commas
	return getCountPOS(tweet, ",")

def feat8(tweet): #colons & semi-colons
	freqDict = getTokenTagFreqDict(tweet)
	count = 0
	for token, tag in freqDict:
		if tag == ":":
			if re.search("^(:|;)*$", token):
				count += freqDict[(token, tag)]
	return count

def feat9(tweet): #dashes
	tokenDict = getTokenOnlyFreqDict(tweet)
	count = 0
	for token in tokenDict:
		if re.search("^-*$", token):
			count += tokenDict[token]
	return count

def feat10(tweet): #parentheses
	return getCountPOS(tweet, ["(", ")"])

def feat11(tweet): #ellipses
	tokenDict = getTokenTagFreqDict(tweet)
	count = 0
	for token, tag in tokenDict:
		if tag == ":" or tag == "CD":
			if re.search("^\.*$", token):
				count += tokenDict[(token, tag)]
	return count

def feat12(tweet): #common nouns
	return getCountPOS(tweet, ["NN", "NNS"])

def feat13(tweet): #proper nouns
	return getCountPOS(tweet, ["NNP", "NNPS"])

def feat14(tweet): #adverbs
	return getCountPOS(tweet, ["RB", "RBR", "RBS"])

def feat15(tweet): #wh-words
	return getCountPOS(tweet, ["WDT", "WP", "WP$", "WRB" ])

def feat16(tweet): #modern slang acronyms
	tokenDict = getTokenOnlyFreqDict(tweet)
	count = 0
	for token in tokenDict:
		if re.search(slangPattern, token.lower()):
			count += tokenDict[token]
	return count

def feat17(tweet): #words all in upper case min 2 letters
	tokenDict = getTokenOnlyFreqDict(tweet)
	count = 0
	for token in tokenDict:
		if len(token) > 2:
			if token.isupper():
				count += tokenDict[token]
	return count

def feat18(tweet): #average length of sentences in tokens
	lines = (tweet.strip()).split("\n")
	sentences = lines[1:]
	numSentences = float(len(sentences))
	sumTokens = 0.0
	for s in sentences:
		sumTokens += len(s.split())
	return sumTokens/numSentences

def feat19(tweet): #average length of tokens excl. punctuation
	tokenDict = getTokenOnlyFreqDict(tweet)
	numTokens = 0.0
	lengthSum = 0.0
	for token in tokenDict:
		if re.search('[a-zA-Z0-9]', token):
			freq = tokenDict[token]
			lengthSum += freq*len(token)
			numTokens += freq
	return lengthSum/numTokens

def feat20(tweet): #num sentences
	return len(tweet.split("\n")) - 2

def main():
    # parse command line options
	if len(sys.argv) != 3 and len(sys.argv) != 4:
		print('Incorrect number of arguments. Should be "buildarff.py <input.twt> <output.arff> <OPTnumtweets>".')
		sys.exit(2)
	args = sys.argv
	inFileName = args[1]
	outFileName = args[2]
	maxTweets = -1
	if len(sys.argv) == 4:
		maxTweets = int(args[3])

	twttArr = []
	inFile = open(inFileName,'r')
	twttX = inFile.readline()
	for line in inFile:
		if (line.startswith("<A=")):
			twttArr.append(twttX)
			twttX = line
		else:
			twttX += line
	twttArr.append(twttX)
	inFile.close()

	global slangPattern, firstPPattern, secondPPattern, thirdPPattern
	slangPattern = loadWordList('slang.english')
	firstPPattern = loadWordList('First-person')
	secondPPattern = loadWordList('Second-person')
	thirdPPattern = loadWordList('Third-person')

	outFile = open(outFileName, "w+")
	outFile.write("@relation sentiment\n\n")
	for i in range(1, 21):
		outFile.write("@attribute feat" + str(i) + " numeric\n")
	outFile.write("@attribute class {0, 4}\n\n")
	outFile.write("@data\n")
	dataString = ""

	numZeroTweets = 0
	numFourTweets = 0
	for tweet in twttArr:
		affect = re.search("<A=(\d+)>", tweet.split("\n")[0]).groups(0)
		if maxTweets != -1:
			if numZeroTweets >= maxTweets and numFourTweets >= maxTweets:
				break
			if affect[0] == '0':
				if numZeroTweets >= maxTweets:
					continue
				else:
					numZeroTweets += 1
			elif affect[0] == '4':
				if numFourTweets >= maxTweets:
					continue
				else:
					numFourTweets += 1

		dataString = (str(feat1(tweet)) + "," + str(feat2(tweet)) + "," + str(feat3(tweet)) + "," + str(feat4(tweet)) + "," + str(feat5(tweet)) + "," + str(feat6(tweet)) + "," + str(feat7(tweet)) + "," +
		str(feat8(tweet)) + "," + str(feat9(tweet)) + "," + str(feat10(tweet)) + "," + str(feat11(tweet)) + "," + str(feat12(tweet)) + "," + str(feat13(tweet)) + "," + str(feat14(tweet)) + "," +
		str(feat15(tweet)) + "," + str(feat16(tweet)) + "," + str(feat17(tweet)) + "," + "{0:.2f}".format(feat18(tweet)) + "," + "{0:.2f}".format(feat19(tweet)) + "," + str(feat20(tweet)))
		affect = re.search("<A=(\d+)>", tweet.split("\n")[0]).groups(0)
		outFile.write(dataString + "," + affect[0] + "\n")



	outFile.close()

if __name__ == '__main__':
	main()


