# CREATES A PICKLE FILE FOR SEARCHING

from bs4 import BeautifulSoup
from urllib.request import urlopen
import os, re, time, string
from nltk.stem import WordNetLemmatizer 
from pprint import pprint
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
import nltk
from collections import Counter
import pickle

# enters 10-k page, still have to return actual document 
def enter_10k_page(ticker):
	html_str = urlopen('https://www.sec.gov/cgi-bin/browse-edgar?CIK=+'+ ticker +'&owner=exclude&action=getcompany&Find=Search')
	soup = BeautifulSoup(html_str, 'html.parser')
	href = None
	
	# goes through all filings in table and returns href of first 10-K page
	filings = soup.findAll('tr')

	for i in filings:
		if '10-K' in i.get_text():
			href = (i.findAll('a', href=True)[0]['href'])
			break

	return href

# entering actual 10-k, returns href for actual 10-K
def enter_10k(ticker):
	href = enter_10k_page(ticker)

	if href == None: # if doesn't work
		return None

	html_str = urlopen('https://www.sec.gov/' + href)
	soup = BeautifulSoup(html_str, 'html.parser')

	filings = soup.findAll('tr')

	for i in filings:
		if '10-K' in i.get_text():
			href = (i.findAll('a', href=True)[0]['href'])
			break

	return href

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

def getBusinessDesc(ticker):
	href = enter_10k(ticker)
	if href == None: # if doesn't work
		return None

	href = href.strip('ix?doc=/') # strip this portion to bypass XBRL menu if available and go to HTML
	text = ""
	html_str = urlopen('https://www.sec.gov/' + href)
	soup = BeautifulSoup(html_str, 'html.parser')

	text = soup.findAll(text=True)
	visible_text = filter(visible, text) # filter out non-visible elements 
	text = " ".join(t.strip() for t in visible_text)
	text = text.replace(u'\xa0', u' ') # remove some formatting text

	results = re.findall("(?i)Item.1.*Item.2", text) # regex to get Business Description portion of 10k

	for x in results:
		if len(x) > 500:
			y = x.split('.')
			z = "\n".join(y)
			return z

def saveBusinessDesc(ticker):
	f = open(ticker + "DESC" + ".txt", "w+")
	f.write(getBusinessDesc(ticker))
	f.close()

def remove_stop_words(text):
	stop_words = set(stopwords.words('english')) 
	word_tokens = word_tokenize(text) 

	filtered_sentence = [] 
  
	for w in word_tokens: 
		# remove punctuation and numbers 
	    if w not in stop_words and w not in string.punctuation and w.isalpha(): 
	        filtered_sentence.append(w) 

	return filtered_sentence

# lemmatizes, removes duplicates, and only keeps nouns
def lemmatization(text):
	lemmatizer = WordNetLemmatizer()

	# text = list(dict.fromkeys(text)) # remove duplicates
	tags = nltk.pos_tag(text) 
	nouns = [word for word, pos in tags if (pos=='NN' or pos=='NNP' or pos=='NNS' or pos=='NNPS')]
	lemmatized_output = ' '.join([lemmatizer.lemmatize(w) for w in nouns if len(w) > 4 ])

	return(lemmatized_output.split(" "))

def load_tickers(file):
	# returns list of tickers
	f = open(file)
	tickers = f.read()
	tickers = tickers.strip('\',')
	return (list(tickers.split("', '")))

# grab data from Wikipedia of current S&P500 Stocks
def update_sp500_tickers():
	tickers = []

	html_str = urlopen('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
	soup = BeautifulSoup(html_str, 'html.parser')
	table = soup.find("table", { "class" : "wikitable sortable" })

	rows = table.findAll('tr')

	for row in rows:
		fields = row.findAll('td')

		try:
			ticker = fields[0].get_text()
			tickers.append(ticker.strip('\n'))
		except:
			print("None")

	pickle.dump(tickers, open("sp500.p", "wb"))

def update_stock_data_dict():
	ret_dict = {}
	error_count = 0
	tickers = load_tickers('sp500.csv')
	
	for ticker in tickers:
		txt = getBusinessDesc(ticker) # get business desc of ticker

		if txt == None: # if business desc doesn't load 
			error_count += 1
			print("ERROR ON: ", ticker)
			continue

		removed_stop_words = remove_stop_words(txt) # take out stop words from business desc
		txt_lemmatized = lemmatization(removed_stop_words) # lemmatize and only keep nouns
		dict_terms = Counter(txt_lemmatized) # create dictionary from terms 

		ret_dict[ticker] = dict_terms # nested dict of tickers and keywords 
		print("FINISHED LOADING...", ticker)

	pickle.dump(ret_dict, open("stockData.p", "wb"))
	print("TOTAL ERRORS: ", error_count, "ERROR %: ", error_count/len(tickers))


# TODO 
# front end 
# place more financial stop words 
# find out why the 20% not working (incl. DIS)
# add nasdaq to total stocks
