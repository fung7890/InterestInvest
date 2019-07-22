# USES PICKLE FILE TO SEARCH THROUGH

from bs4 import BeautifulSoup
from urllib.request import urlopen
import pickle
from nltk.stem import WordNetLemmatizer 
from pprint import pprint
# from kivy.app import App

def run_search(keyword):
	stocks = pickle.load( open( "stockData.p", "rb" ) )
	lemmatizer = WordNetLemmatizer()
	keyword = lemmatizer.lemmatize(keyword) # lemmatize search keyword
	ret_dict = {} # return dictionary

	for company, keywords in stocks.items():
		if keyword in keywords:
			ret_dict[company] = keywords[keyword]/len(keywords)*100

	sorted_d = sorted((value, key) for (key, value) in ret_dict.items())

	print("COMPANY TICKER", "....", "PERCENTAGE OF TOTAL KEYWORDS")
	for i in sorted_d[::-1]:
		print(i[1],"....", "{:.2f}".format(i[0])+"%")


run_search("candy") # EXAMPLE SEARCH