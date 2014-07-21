#!/usr/bin/env python
import httplib
import json
import sys

f = open('d:/_repos/Twitter/TwitterMining/tagger/simple_tagger/stop_words/englishST.txt', 'r')
lines = f.readlines()

def wordIsStopWord(word):
	for line in lines:
		if word in line:
			return True
	return False

def getMostCommonWords():

	ELASTIC_SEARCH_HOST = '127.0.0.1'
	ELASTIC_SEARCH_PORT = 9200


	elasticSearch = httplib.HTTPConnection(ELASTIC_SEARCH_HOST, ELASTIC_SEARCH_PORT)
	elasticSearch.connect()

	query = """
	{
		\"query\" : {
			\"match_all\" : {  }
		},
		\"facets\" : {
			\"tags\" : {
				\"terms\" : {
					\"field\" : \"text\",
					\"size\" : 1000
				}
			}
		}
	}"""

	elasticSearch.request('POST', '/twitter/_search?pretty=true', query)

	raw_response = elasticSearch.getresponse()

	js = json.loads(raw_response.read())

	terms = js["facets"]["tags"]["terms"]



	words = []
	for x in terms:
		try:
			if not wordIsStopWord(x[u'term'].encode('ascii', 'ignore')):
				words.append(x[u'term'].encode('ascii', 'ignore'))
		except Exception:
			raise

	elasticSearch.close()
	return words