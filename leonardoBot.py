import re
import random
import discord
from functools import partial
with open('discordToken.txt','r') as f:
    DISCORD_TOKEN = f.readline().strip()
    STORAGE_FILE = f.readline().strip()
    INTERNAL_KEYWORD = f.readline().strip()
    DELETE_KEY = f.readline().strip()

class Leonardo(discord.Client):
    storage = {}
    constants = {\
        'bots': ['siri','alexa'],\
        'greetings':['hi','hello','what\'s up','how are you'],
        'passcodes': ['leo','leonardo','!!']}
    
    def del_constants(self, key, val):

        if key in self.constants:
            if val == DELETE_KEY:
                self.constants.pop(key)
                self.write_to_file('constants', key, DELETE_KEY)
            else:
                if val in self.constants[key]:
                    self.constants[key].pop(val)
                    self.write_to_file('constants', key, '---'+DELETE_KEY+'---'+val+'---')
        return 'complete'
    def write_constants(self, key, val):
        if key in self.constants:
            if not val in self.constants[key]:
                self.constants[key].append(val)
        self.write_to_file('constants', key, val)
        return 'complete'
    
    def read_constants(self, key):
        if key in self.constants:
            return self.constants[key]
        return 'complete'

    def write_to_file(self, key_group, key, val):
        with open(STORAGE_FILE,'a') as f:
            f.write(key_group + '|' + key + '|' + val + '|\n')
        return 'complete'
        
    def reset_and_read_from_file(self):
        with open(STORAGE_FILE,'r') as f: 
            content = f.readline()
            if content == '':
                return 'complete'
            parent_key, key, val, _ = content.strip().split('|')
            if parent_key == 'constants':
                if val == DELETE_KEY and key in self.constants:
                    self.constants.pop(key)
                elif val[:3] == '---':
                    password, val = val.split('---')
                    if password == DELETE_KEY and key in self.constants[key]:
                        self.constants[key].remove(key)
                elif key in self.constants: self.constants[key].append(val)
                else: self.constants[key] = [val]
            
            elif parent_key == 'storage':
                if val == DELETE_KEY:
                    self.storage.pop(val)
                else:
                    self.storage[key] = val
            else: pass
        


    def storage_store(self,function_name, action_name, key, val):
        key = function_name+'-'+action_name+'-'+key
        self.storage[key] = val
        self.write_to_file('storage', key, val)
    def storage_delete(self,function_name, action_name, key):
        key = function_name+'-'+action_name+'-'+key
        if key in self.storage:
            self.storage.pop(key)
            self.write_to_file('storage', key, DELETE_KEY)
            return True
        else: 
            return False
    def storage_get(self,function_name, action_name, key):
        key = function_name+'-'+action_name+'-'+key
        if key in self.storage:
            return self.storage[key]
        else: 
            return None

    def zoom_function(self, commands):
        function_name = 'zoom'
        help_reply = 'Leonardo\'s zoom function:\n'+\
				'!!zoom set <alias> <zoom link>\n  --> this sets the zoom link with alias (no space)\n'+\
                '!!zoom get <alias>\n  --> this gets the zoom link\n'+\
                '!!zoom del <alias>\n  --> this deletes the alias'
        failure_reply = ' failed, Check help and try again.'
        if len(commands)<2:
            return help_reply
        reply = ''
        action = commands[0]
        commands = commands[1:]
        if action == 'set':
            if len(commands)==2:
                alias, link = commands
                if link.isnumeric():
                    link = 'https://hmc-edu.zoom.us/j/'+link
                self.storage_store(function_name, 'set', alias, link)
                reply = 'Leonardo saved link '+link+' under alias '+alias
            else: reply = 'set'+failure_reply
        elif action == 'del':
            if len(commands)==1:
                alias = commands[0]
                result = self.storage_delete(function_name, 'set', alias)
                if result:
                    reply = 'Leonardo removed alias '+alias
                else:
                    reply = 'Leonardo does not know alias'+alias
        elif action == 'get':
            if len(commands)==1:
                alias = commands[0]
                result = self.storage_get(function_name, 'set', alias)
                if result:
                    reply = result
                else:
                    reply = 'Leonardo does not know alias'+alias
                
        if reply == '' or reply == None: 
            reply = help_reply
        return reply

    def should_activate_bot(self,text):
        if len(text)<2:
            return False
        text = text.lower()
        is_directed_to = lambda x: x[0] in text and text.index(x[0])<x[1]
        for passcode in self.constants['passcodes']:
            length = 3 if passcode == '!!' else 15
            if is_directed_to([passcode,length]):
                return True
        return False
    def greeting(self,text,author):
        for bot in self.constants['bots']: 
            if bot in text:
                response = 'I am better than '+bot
                return response
        for greeting in self.constants['greetings']:
            if greeting in text:
                response = random.choices(self.constants['greetings'])[0]
                return response[0].upper()+response[1:]+' '+author+'!'
        return ''
    
    def external_commands(self,text,author):
        remove_activation = lambda x: '' if not x in text else text[text.index(x)+len(x):]
        for passcode in self.constants['passcodes']:
            result = remove_activation(passcode)
            if result != '':
                text = result
                break
        if result == '': return ''
        commands = text.split()
        function_mappings = {'zoom':self.zoom_function}
        if commands[0] == 'show-all':
            reply = 'These are all functions Leonardo supports: '
            for key, _ in list(function_mappings.items()):
                reply += key + ', '
            reply = reply[:-2]
        elif commands[0] in function_mappings:
            reply = function_mappings[commands[0]](commands[1:])
        else:
            reply = ''
        return reply

    def internal_commands(self,text,author):
        remove_activation = lambda x: '' if not x in text else text[text.index(x)+len(x):]
        for passcode in self.constants['passcodes']:
            result = remove_activation(passcode)
            if result != '':
                text = result
                break
        if result == '': return ''
        commands = text.split()
        passcode = commands[0]
        if passcode != INTERNAL_KEYWORD:
            return ''
        command = commands[1]
        if command == 'get-storage':
            return self.storage
        elif command == 'get-constants':
            return self.constants
        else:
            return ''
    def respond(self, text,author):
        text = text.lower()
        if not self.should_activate_bot(text):
            return None
            
        function_groups = [self.internal_commands, self.greeting, self.external_commands]
        for function_group in function_groups:
            reply = function_group(text,author)
            if reply!='':
                return reply 
        reply = 'This is Leonardo bot. To get all supported functions, type "!!show-all".\n'+\
                'Typically, a command follows this pattern: "!!<product name, such as zoom> <action name, such as help> <additional arguments>"'
        return reply

    async def on_ready(self):
        # Runs when successfully connected to the server
        print('Logged on as', self.user)
        self.reset_and_read_from_file()
        print(self.storage)
        print(self.constants)
        print('Finish reading')
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        reply = self.respond(message.content, message.author.name)
        if reply:
            await message.channel.send(reply)


if __name__ == '__main__':
    client = Leonardo()
    client.run(DISCORD_TOKEN)
