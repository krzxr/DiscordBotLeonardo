import re
import random

import discord
#from discord.ext import tasks as discord_tasks
#from discord.ext import commands as discord_commands
from LogDatabase import *
import os
import time
with open('discordToken.txt','r') as f:
    DISCORD_TOKEN = f.readline().strip()
    STORAGE_FILE = f.readline().strip()
    INTERNAL_KEYWORD = f.readline().strip()

class Leonardo(discord.Client):
    def __init__(self, storage_file, internal_key):
        super().__init__()
        exists = os.path.exists(storage_file)
        self.internal_key = internal_key
        self.db = LogDatabase(storage_file)
        self.const_db, self.save_db, self.clock_db ='CONSTANTS','SAVE','CLOCK'
        self.names = 'names'
        self.bots = 'bots'
        self.greetings = 'greetings'
        self.developing = 'developing'

        self._init(exists)
    def _init(self, exists):
        if not exists:
            if not self.db.create_db([self.const_db, self.save_db, self.clock_db]):
                raise('create db error')
            constants = {\
                self.bots: ['siri','alexa'],\
                self.greetings:['hi','hello','what\'s up','how are you'],
                self.names: ['leo','leonardo','!!']}
            for key, val in list(constants.items()):
                if not self.db.write_to_ls(self.const_db, key, val):
                    raise('create initial constants error')

    def greet_commands(self,text,author):
        for bot in self.db.get(self.const_db,self.bots): 
            if bot in text:
                response = 'I am better than '+bot
                return response
        greetings = self.db.get(self.const_db, self.greetings)
        for greeting in greetings:
            if greeting in text:
                response = random.choices(greetings)[0]
                return response[0].upper()+response[1:]+' '+author+'!'
        return ''
    
    def save_fn(self,commands):
        if len(commands)==2:
            alias, content = commands
            self.db.write_val(self.save_db, alias, content)
            reply = 'Leonardo saved content '+content+' under alias '+alias
        else: reply = 'Ooops save failed'
        return reply

    def get_fn(self,commands):

        if len(commands)==1:
            alias = commands[0]
            reply = self.db.get(self.save_db, alias)
            if reply == None: reply = 'Leonardo does not alias '+alias 
        else: reply = 'Ooops get failed'
        return reply
    
    def del_fn(self,commands):
        reply = False
        if len(commands)==1:
            alias = commands[0]
            reply = self.db.delete(self.save_db, alias)
        if reply:
            return alias + ' removed'
        else:
            return 'Ooops delete failed'

    def external_commands(self,text,author):
        external_commands = {\
            'save': (self.save_fn, 'save <alias> <content>'),\
            'get' : (self.get_fn, 'get <alias>'),\
            'del' : (self.del_fn, 'del <alias>'),\
            'reminder' : (self.set_clock_fn, 'reminder alias <days_of_week: M,T,W,H,F,S,U (sunday)> <HH:MM, 24 hours> <optional: num_occurance> <msg>,'+self.developing),
            'del-reminder' : (self.del_clock_fn, 'del-reminder alias.' +self.developing)
        }
        
        done, text = self._remove_activation_code(text)

        if not done: return ''
        
        commands = text.split()
        command = commands[0]
        commands = commands[1:]

        if command == 'show-all':
            reply = 'These are functions Leonardo supports: \n'
            for key,(_, explain) in list(external_commands.items()):
                if self.developing in explain:
                    continue
                reply += explain +'\n'
            reply = reply[:-1]
        elif command in external_commands:
            
            fn, msg = external_commands[command]
            if self.DEVELOPPING in msg:
                reply = 'Leonardo is not ready for this function yet'
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
        command = commands[1]
        commands = commands[2:]
        
        if command == 'get':
            if len(commands)!=2: return ''
            db, key = commands
            return self.db.get(db, key)
        elif command == 'set':
            if len(commands)!=3: return ''
            db, key, val = commands
            return self.db.write_val(db, key, val)
        elif command == 'append':
            if len(commands)!=3: return ''
            db, key, val = commands
            return self.db.write_to_ls(db, key, val)
        elif command == 'del':
            if len(commands)!=2: return ''
            db, key = commands
            return self.db.delete(db, key)
        elif command == 'pop':
            if len(commands)!=3: return ''
            db, key, val = commands
            return self.db.pop_from_ls(db, key, val)
       
        else: return ''
    
    def _remove_activation_code(self, text):
        remove_activation = lambda x: '' if not x in text else text[text.index(x)+len(x):]
        result = ''
        for name in self.db.get(self.const_db, self.names):
            result = remove_activation(name)
            if result != '':
                return True, result
        return False, result

    def _should_activate_bot(self,text):
        if len(text)<2:
            return False
        text = text.lower()
        is_directed_to = lambda x: x[0] in text and text.index(x[0])<x[1]
        for name in self.db.get(self.const_db, self.names):
            length = 3 if name == '!!' else 15
            if is_directed_to([name,length]):
                return True
        return False
    def respond(self, text,author):
        text = text.lower()
        if not self._should_activate_bot(text):
            return None
            
        function_groups = [self.internal_commands, self.greet_commands, self.external_commands]
        for function_group in function_groups:
            reply = function_group(text,author)
            if reply!='':
                return reply 
        reply = 'This is Leonardo bot. To get all supported functions, type "!!show-all".\n'+\
                'Typically, a command follows this pattern: "!!<action name, such as help, save, or get> <additional arguments>"'
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
    

            if not self.db.write_to_ls(self.clock_db, alias, array, overwrite=True):
                return 'Set reminder failed'
            reply = 'Set reminder for alias '+ alias + 'every '+week_of_day[0].upper()+week_of_day[1:]+' '+time+' Pacific Time for '+num_occurance+' occurances. The message is '+msg 
        else: 
            return ''

    async def del_clock_fn(self,commands):
        if not len(commands)==1:
            return 'invalid delete'
        alias = commands[0]
        if not self.db.delete(self.clock_db, alias):
            return 'invalid delete'
        else: return 'reminder alias '+alias +' removed!'

    #@discord_tasks.loop(seconds = 60 * 10)
    async def run_clock_fn(self):
        now = time.time()
        keys = self.db.get_keys(self.clock_db, default = [])
        for key in keys:
            content = self.db.get(db, key, default = None)
            if not content or len(content)!=5: continue 
            week_of_day, hour, minute, num_occurance, last_used_time = content 
            if now < last_used_time + 60 * 60 * 24 * 7:
                continue 



if __name__ == '__main__':
    client = Leonardo(STORAGE_FILE, INTERNAL_KEYWORD)
    client.run(DISCORD_TOKEN)
