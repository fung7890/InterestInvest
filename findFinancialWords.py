import json, csv

file_object = open('./TESTJSON.json', 'r')
datastore = json.load(file_object)

def intersection(lst1, lst2):
	return list(set(lst1) & set(lst2)) 

def main():

	financial_words = []

	for tickers, keywords in datastore.items():
		tmp = []
		for word in keywords:
			tmp.append(word)
		financial_words.append(tmp)


	common_financial_words = intersection(intersection(financial_words[0], financial_words[3]), financial_words[2])

	with open('financialStopWords.csv', 'w') as csvFile:
		writer = csv.writer(csvFile, quoting=csv.QUOTE_ALL)
		writer.writerow(common_financial_words)

# main()
