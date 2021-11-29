import re
import random
import discord
from collections import defaultdict
with open('raphael_token.txt','r') as f:
    DISCORD_TOKEN = f.readline()

class book:
    def __init__(self,title=None):
        self.title = title
        with open(title+'.txt','r') as f:
            self.content = f.readlines()
        self.page = 0
    def read(self):
        if 0<=self.page<len(self.content):
            text = self.content[self.page]
            if text != '\n':
                text = text.replace('_______','\n\n')
                return text.strip()
            else:
                return text+'\n'
        else:
            return 'Reading content out of bound'
class Raphael(discord.Client):
    book = defaultdict(lambda: None) 
    def respond(self,content,name):
        reply = None
        arr = content.strip().split()
        
        if self.book[name] == None:
            if len(arr)==2 and arr[0].lower() == 'read':
                book_name = arr[1].lower()
                try:
                    self.book[name] = book(book_name)
                    reply = 'Finish loading'
                except OSError:
                    reply = 'File not found'
        else: 
            if len(arr)==1:
                command = arr[0]
                if command in ['i','n','inc','next']:
                    reply = self.book[name].read()
                    self.book[name].page += 1
                elif command in ['d']:
                    self.book[name].page -= 2
                    reply = self.book[name].read()
                elif command in ['del']:
                    self.book[name] = None 
                    reply = 'Reset book cache'
                elif command in ['name']:
                    reply = self.book[name].title
                elif command in ['page']:
                    reply = self.book[name].page
            elif len(arr)==2:
                command, num = arr
                if command in ['split','j']:
                    self.book[name].page = num
                    reply = self.book[name].read()
                elif command in ['i','n','inc','next']:
                    num = int(num)
                    reply = []
                    for _ in range(num):
                        reply.append(self.book[name].read())
                        self.book[name].page += 1
                    reply = ' '.join(reply)

        if reply == None:
            return 'What\'s up!'
        if reply == '':
            reply = ' ' 
        return reply
        
    async def on_ready(self):
        # Runs when successfully connected to the server
        print('Logged on as', self.user)
    
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
