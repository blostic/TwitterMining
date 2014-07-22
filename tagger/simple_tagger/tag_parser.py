import json
import re
import traceback
import sys
from types import StringType
import pymongo
import time
import datetime

class TagParser():
    
    def __init__(self):
        #set of tags mapped to a list of categories
        self.__tag_dict={}
        #a key in __geo_set contains tag and coordinates separated by commas
        self.__geo_set=set()
        self.__tags_filenames=[]
        self.__tweets_filename=None
        self.__output_filename=None
        
    def add_tag_filename(self,name):
        if type(name) is StringType:
            self.__tags_filenames.append(name)
        #print self.__tags_filenames
    
    def set_input_filename(self,name):
        if type(name) is StringType:
            self.__tweets_filename=name
    
    def set_output_filename(self, name):
        if type(name) is StringType:
            self.__output_filename=name
    
    def get_tag_filenames(self, ):
        return self.__tags_filenames
    
    def get_input_filename(self, ):
        return self.__tweets_filname
    
    def get_output_fileaname(self):
        return self.__get_output_filename
    
    
    def read_tags(self):
        for tags_filename in self.__tags_filenames:        
            tags_file=open(tags_filename,"r")
            for line in tags_file.readlines():
                tag_with_categories=line.rstrip("\n").split(",")
                self.__tag_dict[tag_with_categories[0]]=tag_with_categories[1:]
        #print self.__tag_dict
            
    def process_tags(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client.twitter
		
        #tweets_file=open(self.__tweets_filename,"r")
        #output_file=open(self.__output_filename,"w")
        self.__regex_dict={}
        for cat in self.__tag_dict.keys():
            self.__regex_dict[cat]=re.compile(cat.lower())
        
        #for line in tweets_file:
        for line in db.generic_tweet.find():
            tweet_object=line
            ts = time.time()
            print datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'), " - retrieving tweet: ", tweet_object[u'tweetid']
            #print tweet_object
            categories=set()
            
            for cat in self.__tag_dict.keys():
                prog_regular=self.__regex_dict[cat]
                #prog_at=re.compile(u"@"+cat)
                #prog_hash=re.compile(u"#"+cat)
                
                text_result_regular=prog_regular.match(tweet_object[u'text'].lower())
                #text_result_at=prog_at.match(tweet_object[u'text'])
                #text_result_hash=prog_hash.match(tweet_object[u'text'])
                if u'description' in tweet_object:
                    description_result_regular=prog_regular.match(tweet_object[u'description'].lower())
                    #description_result_at=prog_at.match(tweet_object[u'description'])
                    #description_result_hash=prog_hash.match(tweet_object[u'description'])
                else:
                    description_result_regular=None
                    #description_result_at=None
                    #description_result_hash=None
                if text_result_regular!=None or description_result_regular!=None:#\
                                        #or text_result_at!=None or text_result_hash!=None or desceiption_result_at!=None or description_result_hash!=None:
                    #hsh=cat+','+','.join([ i.__str__() for i in tweet_object[u'geo']])
                    #print hsh
                    #if not (hsh in self.__geo_set):   
                    #self.__geo_set.add(hsh)
                        #output_file.write(hsh+','+','.join(self.__tag_dict[cat])+'\n')
                    categories.add(cat)
                    for c in self.__tag_dict[cat]:
                        categories.add(c)
                    
            if categories:
                tweet_object[u'tags']=list(categories)
                db.generic_tweet.update({'_id' : tweet_object[u'_id']}, {"$set": tweet_object})
            #output_file.write(json.dumps(tweet_object)+'\n')
            
                    
if __name__ == '__main__':
    t=TagParser()
    #you can add aditional tag filenames as program arguments
    for arg in sys.argv[1:]:
        t.add_tag_filename(arg)
    #t.add_tag_filename("./tags/muzycy")
    #t.add_tag_filename("./tags/sporty.txt")
    #t.add_tag_filename("./tags/video_games.txt")
    #here you can add more tag filenames
    t.read_tags()
    t.process_tags()