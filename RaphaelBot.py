import re
import random
import discord
from functools import partial
with open('raphael_token.txt','r') as f:
    DISCORD_TOKEN = f.readline().strip()

class book:
    def __init__(self,title=None):
        self.title = title
        with open(title+'.txt','r') as f:
            self.content = f.readlines()
        self.page = 0
    def read():
        if 0<=self.page<len(self.content):
            return self.content[self.page]
        else:
            return 'Reading content out of bound'
class Rphael(discord.Client):
    def warm_start(self):
        self.book2page = {}
        with open('raphael_db.txt','r') as f:
            book, page = f.readline().strip().split(',')
            page = int(page)
            self.book2page[book] = page
        self.book = None
    def read(self,page):

    def respond(self,content,name):
        reply = ''
        arr = content.strip().split()
        if self.book == None:
            if len(arr)==2 and arr[0].lower() == 'read':
                book_name = arr[1].lower()
                try:
                    self.book = book(book_name)
                    reply = 'Finish loading'
                except OSError:
                    reply = 'File not found'
                else:
                    print('File reading error')
        else: 
            if len(arr)==1:
                command = arr[0]
                if command in ['i','n','inc','next']:
                    reply = self.book.read()
                    self.book.page += 1
                elif command in ['d']:
                    self.book.page -= 2
                    reply = self.book.read()
                elif command in ['del']:
                    self.book = None 

            elif len(arr)==2:
                command, num = arr
                if command in ['split','j']:
                    num = int(num)
                    self.book.page = num
                    reply = self.book.read()
        if not reply == '':
            return 'What\' up!'
        return reply
        
    async def on_ready(self):
        # Runs when successfully connected to the server
        print('Logged on as', self.user)
        self.warm_start()
    
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        reply = self.respond(message.content, message.author.name)
        if reply:
            await message.channel.send(reply)


if __name__ == '__main__':
    client = Raphael()
    client.run(DISCORD_TOKEN)
