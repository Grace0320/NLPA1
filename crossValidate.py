import sys
from subprocess import check_output
from scipy import stats

arffHeader = ("@relation sentiment\n\n@attribute feat1 numeric\n@attribute feat2 numeric\n@attribute feat3 numeric\n@attribute feat4 numeric\n"
"@attribute feat5 numeric\n@attribute feat6 numeric\n@attribute feat7 numeric\n@attribute feat8 numeric\n@attribute feat9 numeric\n"
"@attribute feat10 numeric\n@attribute feat11 numeric\n@attribute feat12 numeric\n@attribute feat13 numeric\n@attribute feat14 numeric\n"
"@attribute feat15 numeric\n@attribute feat16 numeric\n@attribute feat17 numeric\n@attribute feat18 numeric\n@attribute feat19 numeric\n"
"@attribute feat20 numeric\n@attribute class {0, 4}\n\n@data\n")

wekaCommandStart = 'java -cp C:/GIT/NLP/WEKA/weka.jar'
SMO = "weka.classifiers.functions.SMO"
NB = "weka.classifiers.bayes.NaiveBayes"
J48 = "weka.classifiers.trees.J48"

def callWeka(classPath, trainingFileName, testFileName, outputFile, partition):
	wekaCommand = wekaCommandStart + ' ' + classPath + ' -t ' + trainingFileName + ' -T ' + testFileName + " -o"
	classifierOut = check_output(wekaCommand)
	testMatrix = classifierOut.split("\n")[38:40]
	aa = float(testMatrix[0].split()[0])
	ab = float(testMatrix[0].split()[1])
	ba = float(testMatrix[1].split()[0])
	bb = float(testMatrix[1].split()[1])

	accuracy = (aa + bb)/(aa + bb + ab + ba)
	precisionA = aa/(aa + ba)
	precisionB = bb/(bb + ab)
	recallA = aa/(aa + ab)
	recallB = bb/(bb + ba) 

	outputFile.write(classPath.split(".")[3].ljust(12) + "|" + " {0:.4f}%".format(accuracy*100).ljust(12) + "|" + " {0:.4f}%".format(precisionA*100).ljust(12) + "|" +" {0:.4f}%".format(precisionB*100).ljust(12) + "|" +" {0:.4f}%".format(recallA*100).ljust(12) + "|" + " {0:.4f}%".format(recallB*100).ljust(12) + "\n")
	return accuracy

def main():
	# parse command line options
	if len(sys.argv) != 2:
		print('Incorrect number of arguments. Should be "crossValidate.py <partition prefix>".')
		sys.exit(2)
	args = sys.argv
	partPrefix = args[1]

	wekaClasses = [SMO, NB, J48]

	overallResultsFile = open("crossValidate.out", "w+")
	overallResultsFile.write("Cross validation results\n")

	SMOaccuracyVector = []
	NBaccuracyVector = []
	J48accuracyVector = []

	for i in range(0, 10):
		testPartFileName = partPrefix+str(i)+".txt"
		testArffFileName = partPrefix+str(i)+".arff"
		trainArffFileName = partPrefix+str(i)+".arff"
		testPart = open(testPartFileName, "r")
		testArff = open(testArffFileName, "w+")
		testArff.write(arffHeader)
		testArff.writelines(testPart.readlines())
		testPart.close()
		testArff.close()

		trainArff = open(trainArffFileName, "w+")
		trainArff.write(arffHeader)
		for j in range(0, 10):
			if j != i:
				tempPart = open(partPrefix+str(j)+".txt")
				trainArff.writelines(tempPart.readlines())
				tempPart.close()
		trainArff.close()

		overallResultsFile.write("\n" + "Partition" + str(i) + "\n")
		overallResultsFile.write("\t\t\t| Accuracy   | PrecisionA | PrecisionB | RecallA    | RecallB    \n")
		overallResultsFile.write("------------+------------+------------+------------+------------+------------\n")
		for wekaClass in wekaClasses:
			accuracy = callWeka(wekaClass, trainArffFileName, testArffFileName, overallResultsFile, partPrefix + str(i))
			if wekaClass == SMO:
				SMOaccuracyVector.append(accuracy)
			elif wekaClass == NB:
				NBaccuracyVector.append(accuracy)
			elif wekaClass == J48:
				J48accuracyVector.append(accuracy)

	

	S_smo_nb = stats.ttest_rel(SMOaccuracyVector, NBaccuracyVector)
	S_nb_j48 = stats.ttest_rel(NBaccuracyVector, J48accuracyVector)
	S_j48_smo = stats.ttest_rel(J48accuracyVector, SMOaccuracyVector)

	overallResultsFile.write("\n\nSMO - NaiveBayes PValue " + str(S_smo_nb.pvalue))
	overallResultsFile.write("\n\nNaiveBayes - J48 PValue " + str(S_nb_j48.pvalue))
	overallResultsFile.write("\n\nJ48 - SMO PValue " + str(S_j48_smo.pvalue))



if __name__ == '__main__':
	main()