import re
import random

import discord
#from discord.ext import tasks as discord_tasks
#from discord.ext import commands as discord_commands
from LogDatabaseV2 import *
import os
import time
with open('discordToken.txt','r') as f:
    DISCORD_TOKEN = f.readline().strip()
    STORAGE_FILE = f.readline().strip()
    INTERNAL_KEYWORD = f.readline().strip()
    DELIMIT = f.readline().strip()
    SUBDELIMIT = f.readline().strip()
    NEW_LINE = f.readline().strip()
class Leonardo(discord.Client):
    def __init__(self, storage_file, internal_key, delimit = DELIMIT, sub_delimit = SUBDELIMIT, new_line = NEW_LINE):
        super().__init__()
        self.internal_key = internal_key
        storage_file_for_db = storage_file.split('.')[0]
        exists = os.path.exists(storage_file_for_db + '-v2.txt')
        self.db = LogDatabase2(storage_file,delimit, sub_delimit, new_line)
         
        #self.const_db, self.save_db, self.clock_db = self.db.create_db('CONSTANTS','ListDB'), self.create_db('SAVE','HashDB'),self.create_db('CLOCK','BucketDB')
        if not exists:
            self.const_db, self.save_db, self.clock_db = self.db.create_dbs([['CONSTANTS','ListDB'],['SAVE','HashDB'],['CLOCK','BucketDB',{'buckets':list(range(1,8))}]], write = not exists)
        else:
            self.const_db, self.save_db, self.clock_db = self.db.get_dbs(['CONSTANTS','SAVE','CLOCK'])

        self.wordy = False

        self.names = 'names'
        self.bots = 'bots'
        self.greetings = 'greetings'
        self.fun_replies = 'fun_replies'
        self.developing = 'developing'
        self.tmp_zoom_link = ''
        
        self._init(exists)
        
    def _init(self, exists):
        if not exists:
            constants = {\
                self.bots: ['siri','alexa'],\
                self.greetings:['hi','hello','what\'s up','how are you'],
                self.names: ['leo','leonardo','!&'],
                self.fun_replies: ['Got it','Alright','Very good', 'Ok','Sounds good','好的','没问题','行','확인','괜찮은']}
            for key, val in list(constants.items()):
                if not self.const_db.write(key, val):
                    raise('create initial constants error')

    def greet_commands(self,text,author):
        for bot in self.const_db.get(self.bots): 
            if bot in text:
                response = 'I am better than '+bot
                return response
        greetings = self.const_db.get(self.greetings)
        punctuations = ['!','?','.',',','\'','\"']
        for punctuation in punctuations: 
            text = text.replace(punctuation,'')
        reply = ''
        for greeting in greetings:
            if greeting in text.split():
                reply = self._send_greetings(author)
        return reply
    def _send_greetings(self, author):
        greetings = self.const_db.get( self.greetings)
        response = random.choices(greetings)[0]
        return response[0].upper()+response[1:]+' '+author+'!'
    
    def _update_reply(self,reply):
        if self.wordy:
            return reply
        else:
            return random.choices(self.fun_replies)[0]

    def save_fn(self,commands):
        if len(commands)>=2:
            alias, *content = commands
            content = ' '.join(content)
            self.save_db.write( alias, content)
            reply = 'Leonardo saved content under alias '+alias
            reply = self._update_reply(reply)
        else: reply = 'Ooops save failed'
        return reply

    def get_fn(self,commands):

        if len(commands)==1:
            alias = commands[0]
            reply = self.save_db.get( alias)
            if reply == None: reply = 'Leonardo does not alias '+alias 
        else: reply = 'Ooops get failed'
        return reply
    
    def del_fn(self,commands):
        reply = False
        if len(commands)==1:
            alias = commands[0]
            self.save_db.delete( alias)
            reply =  alias + ' removed'
            reply = self._update_reply(reply)
        else: reply = ''
        return reply

    def zoom_fn(self,commands,author):
        zoom_link = self.save_db.get(author,None)
        if zoom_link == None:
            reply = 'Leo does not have a record of your link, please send your link and Leo can add it'
        else:
            reply = zoom_link
        return reply
    def zoom_del_fn(self,commands,author):
        self.save_db.delete(author);
        reply = 'Your link is deleted'
        reply = self._update_reply(reply)
        return reply
    def external_commands(self,text,author):
        external_commands = {\
            'save': (self.save_fn, 'save <alias> <content>'),\
            'get' : (self.get_fn, 'get <alias>'),\
            'del' : (self.del_fn, 'del <alias>'),\
            'reminder' : (self.set_clock_fn, 'reminder alias <days_of_week: M,T,W,H,F,S,U (sunday)> <HH:MM, 24 hours> <optional: num_occurance> <msg>,'+self.developing),
            'del-reminder' : (self.del_clock_fn, 'del-reminder alias.' +self.developing),
            'zoom' : (self.zoom_fn, 'zoom'),\
            'zoom-del': (self.zoom_del_fn, 'zoom-del'),
        }
        
        use_author = ['zoom','zoom-del']

        done, text = self._remove_activation_code(text)

        if not done: return ''
        
        commands = text.split(' ')
        while commands and commands[0] == '':
            commands.pop(0)
        print('external commands',commands)
        command = commands[0].lower()
        commands = commands[1:]

        if command in ['show-all','help']:
            reply = 'These are functions Leonardo supports: \n'
            for key,(_, explain) in list(external_commands.items()):
                if self.developing in explain:
                    continue
                reply += explain +'\n'
            reply = reply[:-1]
        elif command in external_commands:
    
            fn, msg = external_commands[command]
            if self.developing in msg:
                reply = 'Leonardo is not ready for this function yet'
            elif command in use_author:
                reply = fn(commands, author)
            else:
                reply = fn(commands)
        else:
            reply = ''
        return reply

    def internal_commands(self,text,author):
        done, text = self._remove_activation_code(text)
        if not done: return ''

        commands = text.split()
        if len(commands)<2: return ''

        internal_key = commands[0]
        if internal_key != self.internal_key:
            return ''
        command = commands[1].lower()
        commands = commands[2:]
        
        if command == 'get':
            if len(commands)!=2: return ''
            db, key = commands
            return self.db.get_db[db].get(key)
        elif command == 'write':
            if len(commands)!=3: return ''
            db, key, val = commands
            return self.db.get_db[db].write(key, val)
        elif command == 'del':
            if len(commands)!=2: return ''
            db, key = commands
            return self.db.get_db[db].delete(key)
        elif command == 'pop':
            if len(commands)!=3: return ''
            db, key, val = commands
            return self.db.get_db[db].pop(key, val)
       
        else: return ''
    
    def _remove_activation_code(self, text):
        remove_activation = lambda x: '' if not x in text.lower() else text[text.lower().index(x)+len(x):]
        result = ''
        for name in self.const_db.get(self.names):
            result = remove_activation(name)
            if result != '':
                return True, result
        return False, result

    def _should_activate_bot(self,text):
        if len(text)<2:
            return False
        text = text.lower()
        is_directed_to = lambda x: x[0] in text.lower() and text.lower().index(x[0])<x[1]
        for name in self.const_db.get(self.names):
            length = 3 if name == '!!' else 15
            if is_directed_to([name,length]):
                return True
        return False
    
    def promote_by_saving_commands(self,text,author):
        reply = ''
        if 'https' in text.lower() and 'zoom' in text.lower():
            if self.save_db.get(author,None) == None:
                text = text.split()
                
                while not 'https' in text[0].lower() and not 'zoom' in text[0].lower():
                    text.pop(0)
                self.save_db.write(author,text[0])
                reply = 'Leonardo saved your zoom link. To share your link, say "Leo zoom". To delete, say "Leo zoom delete".'

        return reply

    def promote_by_asking_commands(self, text, author):
        if self.tmp_zoom_link != '':
            text = text.split()
            if 'no' in text:
                self.tmp_zoom_link = ''
                reply = 'Got it! Link is not saved.'
            elif text[0] == 'yes':
                if len(text)==1: 
                    reply = 'Missing alias. say "Yes <alias>"'
                else:
                    alias = ' '.join(text[1:])
                    content = self.tmp_zoom_link
                    self.save_db.write( alias, content)
                    reply = 'Leonardo saved content '+content+' under alias '+alias+ '.\nTo get this link, say "Leo get <alias>"'
                    self.tmp_zoom_link = ''
            else:
                reply = 'Leo will forget about this link'
                self.tmp_zoom_link = ''

        elif 'https' in text and 'zoom' in text:
            self.tmp_zoom_link = text
            reply = 'Want to save this zoom link to Leo? Say "Yes <alias>", or "No".'
        else: reply = ''
        return reply 
    def respond(self, text,author):
        first_function_groups = [self.promote_by_saving_commands]
        for function_group in first_function_groups:
            reply = function_group(text,author)
            if reply!='':
                return reply 
        if not self._should_activate_bot(text):
            return None
        
        function_groups = [self.internal_commands, self.greet_commands, self.external_commands]
        for function_group in function_groups:
            reply = function_group(text,author)
            if reply!='':
                return reply 
        reply = self._send_greetings(author) + ' Say "help" to get help'
        return reply

    async def on_ready(self):
        # Runs when successfully connected to the server
        print('Logged on as', self.user)
    
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        reply = self.respond(message.content, message.author.name)
        if reply!=None:
            await message.channel.send(reply)
    
    def _validate_week_of_day(self, week_of_day):
        week_of_day = week_of_day.lower()
        week_of_day_map = {'monday':'m','tuesday':'t','wednesday':'w','thursday':'h','friday':'f','saturday':'s','sunday':'u'}
        
        if not week_of_day in 'mtwhfsu' or not week_of_day in week_of_day:
            return None, None
        if not week_of_day in 'mtwhfsu':
            week_of_day = week_of_day_map[week_of_day]

        return week_of_day, 'mtwhfsu'.index(week_of_day)

    async def set_clock_fn(self):
        if len(commands) in [4,5]:
            commands = [command.lower() for command in commands]
            week_of_day, week_of_day_num = self._validate_week_of_day(week_of_day)
            if not week_of_day: return 'invalid week of day'
            if len(commands) == 3:
                alias, week_of_day, time, msg = commands
                num_occurance = 100
            else:
                alias, week_of_day, time, num_occurance, msg = commands
                num_occurance = int(num_occurance)
                if num_occurance < 1: return 'invalid num of occurance'
            last_used_time = time.time()

            time = time.split(':')
            if len(time)!=2:
                return 'invalid time'
            else:
                hour, minute = time
                if '.' in hour or '.' in minute: 
                    return 'invalid time'
                hour, minute = int(hour), int(minute)
                if not 0<=hour<24 or not 0<=minute<60:
                    return 'invalid time'
            array = [week_of_day_num, hour, minute, num_occurance, last_used_time, msg]
    

            if not self.clock_db.write( alias, array, overwrite=True):
                return 'Set reminder failed'
            reply = 'Set reminder for alias '+ alias + 'every '+week_of_day[0].upper()+week_of_day[1:]+' '+time+' Pacific Time for '+num_occurance+' occurances. The message is '+msg 
        else: 
            return ''

    async def del_clock_fn(self,commands):
        if not len(commands)==1:
            return 'invalid delete'
        alias = commands[0]
        if not self.clock_db.delete( alias):
            return 'invalid delete'
        else: return 'reminder alias '+alias +' removed!'

    #@discord_tasks.loop(seconds = 60 * 10)
    async def run_clock_fn(self):
        now = time.time()
        keys = self.clock_db.get_keys()
        for key in keys:
            content = self.clock_db.get(key, default = None)
            if not content or len(content)!=5: continue 
            week_of_day, hour, minute, num_occurance, last_used_time = content 
            if now < last_used_time + 60 * 60 * 24 * 7:
                continue 



if __name__ == '__main__':
    client = Leonardo(STORAGE_FILE, INTERNAL_KEYWORD)
    client.run(DISCORD_TOKEN)
