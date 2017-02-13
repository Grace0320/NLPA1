import sys
import NLPlib
import csv
import itertools
import re
import unicodedata
import HTMLParser

reload(sys)
sys.setdefaultencoding('utf8')

h = HTMLParser.HTMLParser()
tagger = NLPlib.NLPlib()

# build URL search patterns
# which characters to look for determined from here: http://stackoverflow.com/questions/7109143/what-characters-are-valid-in-a-url
URLAllowedChars = "[A-Za-z0-9-._~:\/?#\[\]@!$&'()*+,;=]*"
tlds = "\.(com|org|net|int|edu|gov|mil|ca|uk|io)"
URLPattern = r"\s*(www\.|http:|https:)" + URLAllowedChars + "\s*"
TLDOnlyPattern = r"\s*" + URLAllowedChars + tlds + "\s*"

#global abbreviation patterns
abbrevPattern = ""
cliticPattern = ""

#build username & hashtag patterns
userPattern = r"(^|\s)(?:@)([a-zA-Z0-9_]{1,15})"   #alphanum or underscore to a max length of 15, preceded by spaces or nothing
hashTagPattern = r"(?:#)([A-Za-z0-9_]{1,140})"	   #alphanum or underscore to max length of tweet length

#Clitics
preClitics = ["o'", "ol'", "y'"]
postClitics = ["n't", "'s", "'ve", "'m", "'re", "'ll","'d", "'"]

# load list of english abbreviations into a an OR statement for regex
def loadEnglishAbbrev():
	f = open('abbrev.english', 'r')
	abbrevList = f.readlines()
	global abbrevPattern
	abbrevPattern += "("
	lim = len(abbrevList)
	for i in range(0, lim):
		abbrevPattern += abbrevList[i].strip('. \n\t')
		if i < lim - 1:
			abbrevPattern += r'|'
	abbrevPattern += ")"

# load list of english clitics into a an OR statement for regex
def loadEnglishClitics():
	f = open('clitic.english', 'r')
	cliticList = f.readlines()
	global cliticPattern
	cliticPattern += "("
	lim = len(cliticList)
	for i in range(0, lim):
		cliticPattern += cliticList[i].strip('. \n\t')
		if i < lim - 1:
			cliticPattern += r'|'
	cliticPattern += ")"

# All html tags and attributes (i.e.,/<[^>]+>/) are removed.
def twtt1(rawTweet): 	
	return re.sub(r'/<[^>]+>/', '', rawTweet)

# Html character codes (i.e.,&...;) are replaced with an ASCII equivalent.
def twtt2(rawTweet): 
	try:
		htmlFree = h.unescape(rawTweet)
		asciiVer = unicodedata.normalize('NFKD', htmlFree.decode('utf-8')).encode('ascii','ignore')
		return asciiVer
	except UnicodeDecodeError:
		asciiVer = rawTweet.decode('ascii','ignore')
		return asciiVer
		
# All URLs (i.e., tokens beginning with http or www) are removed.
def twtt3(rawTweet): 
	remWwwHttp = re.sub(URLPattern, ' ', rawTweet)  
	remTLDs = re.sub(TLDOnlyPattern, ' ', remWwwHttp)
	return remTLDs

# The first character in Twitter user names and hash tags (i.e., @ and #) are removed.
def twtt4(rawTweet): 
	#usernames
	remFirstUserChar = re.sub(userPattern, r"\2", rawTweet)
	#hashtags
	remHashTags = re.sub(hashTagPattern, r"\1", remFirstUserChar)
	return remHashTags

#Each sentence within a tweet is on its own line.
def twtt5(rawTweet):  

	#split tweets on ?!.
	nlOnPeriods = re.sub(r"([^.!?]*)(\.|\!|\?)(\s+|\w+)", r"\1\2\n", rawTweet)
	lines = nlOnPeriods.split('\n')
	procTweet = ""

	#piece lines back together that had abbreviations
	for i in range(0, len(lines)):
		procTweet += lines[i].lstrip()
		if i < len(lines) - 1:
			if not re.search(abbrevPattern + "\.$", lines[i]):
				procTweet += '\n'
			else:
				procTweet += ' '
	return procTweet
			
# Ellipsis (i.e., `...'), and other kinds of multiple punctuation (e.g., `!!!')  are not split
def twtt6(rawTweet): 
	return rawTweet

#Each token, including punctuation and clitics, is separated by spaces.
def twtt7(rawTweet):
	#punctuation
	endOfWordPunc = re.sub(r"""(\w)([.,!?;:~\/\\*+=\-\"^%$#@()[\]{}])""", r'\1 \2', rawTweet)
	beforeWordPunc = re.sub(r"""([.,!?;:~\/\\*+=\-\"^%$#@\(\)[\]{}])(\w)""", r'\1 \2', endOfWordPunc)

	#clitics
	preClitics = re.sub(cliticPattern + r"(\w)",r"", beforeWordPunc, flags=re.IGNORECASE)
	postClitics = re.sub(r"(\w)" + cliticPattern, r"\1 \2", preClitics, flags=re.IGNORECASE)
	return postClitics

# Each token is tagged with its part-of-speech.
def twtt8(rawTweet): 
	lines = rawTweet.split("\n")
	procTweet = ""
	for i in range(0, len(lines)):
		tokenArr  = lines[i].split()
		tags = tagger.tag(tokenArr)
		for j in range(0, len(tokenArr)):
			procTweet += tokenArr[j] + "/" +  tags[j] + " "
		procTweet += "\n"	

	procTweet = procTweet.strip()
	return procTweet

#Before each tweet is demarcation `<A=#>', which occurs on its own line, where # is the numeric class of the tweet (0 or 4).
def twtt9(rawTweet, polarity): 
	return '<A=' + str(polarity) + '>\n' + rawTweet

def main():
    # parse command line options
	if len(sys.argv) != 4:
		print('Incorrect number of arguments. Should be "twtt.py <input.csv> <student#> <output.csv>".')
		sys.exit(2)
	args = sys.argv
	inFileName = args[1]
	studentNum = int(args[2])
	outFileName = args[3]
	constForLineSelect = studentNum%80 * 10000

	inFile = open(inFileName,'r')
	fileObject = csv.reader(inFile)
	numLines = sum(1 for row in fileObject)
	inFile.seek(0)
	if (numLines > 500):  #train
		rows1 = list(csv.reader(itertools.islice(inFile, constForLineSelect, constForLineSelect + 10000)))
		inFile.seek(0)
		rows2 = list(csv.reader(itertools.islice(inFile, constForLineSelect + 800000, constForLineSelect + 810000)))
		rows = rows1 + rows2
	else: #test
		rows = list(csv.reader(inFile))
	inFile.close()
	
	loadEnglishAbbrev()
	loadEnglishClitics()
	outFile = open(outFileName, 'w')
	
	for tweetData in rows:
		v1 = twtt1(tweetData[5])
		v2 = twtt2(v1)
		v3 = twtt3(v2)
		v4 = twtt4(v3)
		v5 = twtt5(v4)
		v6 = twtt6(v5)
		v7 = twtt7(v6)
		v8 = twtt8(v7)
		v9 = twtt9(v8, tweetData[0])
		outFile.write(v9 + "\n")
	outFile.close()

if __name__ == "__main__":
	main()
