from Tkinter import *
import tag_parser
from tag_parser import TagParser
import most_common_words
import ntpath
import os

class Application(Frame):
    
    def retagAllTweets(self):
        t=TagParser()
        for file in os.listdir("./tags"):
            print "./tags" + "/" + file
            t.add_tag_filename("./tags" + "/" + file)
            t.read_tags()
            t.process_tags()
	
    def mostCommon(self):
        self.text.config(state=NORMAL) 
        self.text.delete(1.0, END)
        for word in most_common_words.getMostCommonWords():
            self.text.insert(END, word + "    ")
        self.text.config(state=DISABLED)
		
    def tagTweets(self):
        t=TagParser()
        t.add_tag_filename("./tags/custom_tags.txt")
        t.read_tags()
        t.process_tags()
		
    def addTag(self):
        tagContent = self.text2.get(1.0, END)
        with open("d:/_repos/Twitter/TwitterMining/tagger/simple_tagger/tags/custom_tags.txt ", "a") as custom_tags:
		    custom_tags.write(tagContent)
        self.text2.delete(1.0, END)
        self.text2.insert(END, "[ADDED]")
		
    def createWidgets(self):
        textPad=Frame()
        self.text=Text(textPad,height=20,width=150)
        self.text.config(font=("Calibri",11))
        self.text.config(state=DISABLED) 
        self.text.pack(side=TOP)
        textPad.pack()
		
        textPad2=Frame()
        self.text2=Text(textPad2,height=2,width=150)
        self.text2.config(font=("Calibri",11))
        self.text2.config(state=NORMAL) 
        self.text2.pack(side=TOP)
        
	
        self.MOST_COMMON_WORDS = Button(textPad, bg="slate gray")
        self.MOST_COMMON_WORDS["text"] = "Most common words"
        self.MOST_COMMON_WORDS["command"] =  self.mostCommon

        self.MOST_COMMON_WORDS.pack(side=LEFT)

        self.add_tag = Button(textPad2, bg="slate gray")
        self.add_tag["text"] = "Add tag"
        self.add_tag["command"] = self.addTag
        self.add_tag.pack(side=LEFT)
		
        self.tag = Button(textPad2, bg="slate gray")
        self.tag["text"] = "TAG TWEETS"
        self.tag["command"] = self.tagTweets
        self.tag.pack(side=LEFT)
        textPad2.pack()
		
        retagFrame=Frame()
        self.retagAll = Button(retagFrame, bg="slate gray")
        self.retagAll.config(height = 3, width = 100)
        self.retagAll["text"] = "RETAG ALL"
        self.retagAll["command"] = self.retagAllTweets
        self.retagAll.pack(side=LEFT)
        retagFrame.pack()
		
        self.pack(padx=20, pady=20)


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
root.attributes('-fullscreen', True)

app = Application(master=root)
app.mainloop()

root.destroy()