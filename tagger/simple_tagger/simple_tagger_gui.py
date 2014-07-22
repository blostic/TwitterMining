from Tkinter import *
import tag_parser
from tag_parser import TagParser
import most_common_words
import threading
import os
import time
import datetime

def tagTweetsThread():
        t=TagParser()
        t.add_tag_filename("./tags/custom_tags.txt")
        t.read_tags()
        t.process_tags()
		
def retagAllTweetsThread():
        t=TagParser()
        for file in os.listdir("./tags"):
            print "./tags" + "/" + file
            t.add_tag_filename("./tags" + "/" + file)
            t.read_tags()
            t.process_tags()


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.flush()
        self.stream.write(data)
    def __getattr__(self, attr):
        return getattr(self.stream, attr)


class Application(Frame):
    def retagAllTweets(self):
        threading.Thread(target=retagAllTweetsThread).start()
    
	
    def mostCommon(self):
        self.text.config(state=NORMAL) 
        self.text.delete(1.0, END)
        for word in most_common_words.getMostCommonWords():
            self.text.insert(END, word + "    ")
        self.text.config(state=DISABLED)

    def tagTweets(self):
	    threading.Thread(target=tagTweetsThread).start()
		
    
		
    def addTag(self):
        tagContent = self.text2.get(1.0, END)
        with open("d:/_repos/Twitter/TwitterMining/tagger/simple_tagger/tags/custom_tags.txt ", "a") as custom_tags:
		    custom_tags.write(tagContent)
        self.output.delete(1.0, END)
        print "TAG ADDED"
		
    def createWidgets(self):
        textPad=Frame(bg="light gray")
        self.text=Text(textPad,height=20,width=150)
        self.text.config(font=("Calibri",11))
        self.text.config(state=DISABLED) 
        self.text.pack(side=TOP)
        textPad.pack(padx=20, pady=20)
		
        textPad2=Frame(bg="light gray")
        self.text2=Text(textPad2,height=2,width=150)
        self.text2.config(font=("Calibri",11))
        self.text2.config(state=NORMAL) 
        self.text2.pack(side=TOP)
        
	
        self.MOST_COMMON_WORDS = Button(textPad)
        self.MOST_COMMON_WORDS["text"] = "Most common words"
        self.MOST_COMMON_WORDS["command"] =  self.mostCommon

        self.MOST_COMMON_WORDS.pack(side=LEFT, pady=5)

        self.add_tag = Button(textPad2)
        self.add_tag["text"] = "Add tag"
        self.add_tag["command"] = self.addTag
        self.add_tag.pack(side=LEFT)
		
        self.tag = Button(textPad2)
        self.tag["text"] = "TAG TWEETS"
        self.tag["command"] = self.tagTweets
        self.tag.pack(side=LEFT, pady = 5)
        textPad2.pack(padx=20, pady=20)
		
        retagFrame=Frame(bg="light grey")
        self.retagAll = Button(retagFrame)
        self.retagAll.config(height = 3, width = 100)
        self.retagAll["text"] = "RETAG ALL"
        self.retagAll["command"] = self.retagAllTweets
        self.retagAll.pack(side=LEFT, pady = 5)
        retagFrame.pack(pady=20)
		
        statusFrame = Frame(bg="light grey")
        self.output = Text(statusFrame, height=7,width=150)
        self.output.pack()
        sys.stdout = Unbuffered(sys.stdout)
        sys.stdout = self
        statusFrame.pack()


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

		
    def write(self, txt):
        self.output.insert(END,str(txt))
        self.output.see(END)

if __name__ == '__main__':
    root = Tk()
    root.attributes('-fullscreen', True)
    root.configure(background='light gray')

    app = Application(master=root)
    app.mainloop()