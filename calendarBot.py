#/usr/bin/env python3

# Code adapted from https://discordpy.readthedocs.io/

import random

import discord

import bisect

from dateutil import parser

# This token can be found on the Bot page for your application
with open('calendar_bot.txt','r') as f:
    DISCORD_TOKEN = f.readline().strip()

class CalendarBot(discord.Client):
    start_date = parser.parse('1/1/2021')
    start_date_lunar_idx = 19 - 1
    date_to_lunar_day = dict()
    date_to_lunar_day_info = dict()
    activation_word = 'calendar'
    special_days = []

    # greeting
    def initial_make_reply(self, msg_content, user_name):
        words_splitted_by_space = msg_content.split()
        words_array_length = len(words_splitted_by_space)
        if words_array_length<2:
            return ''

        first_word = words_splitted_by_space[0]

        if first_word != self.activation_word:
            return ''
        
        second_word = words_splitted_by_space[1]

        if second_word == 'Aloha':
            return 'Aloha ' + user_name + '!'
        else:
            return 'Aloha I am calendar bot'
    def make_reply(self, msg_content, user_name):
        words_splitted_by_space = msg_content.split()
        words_array_length = len(words_splitted_by_space)
        if words_array_length<2:
            return ''

        first_word = words_splitted_by_space[0]

        if first_word != self.activation_word:
            return ''
        
        second_word = words_splitted_by_space[1]

        if second_word == 'Aloha':
            return 'Aloha ' + user_name + '!'
        elif self.is_date(second_word):
            
            date = self.get_date(second_word)
            lunar_day_idx = self.get_lunar_day_idx(date)
            lunar_day_name = self.get_lunar_day_name(lunar_day_idx)
            lunar_day_info = self.get_lunar_day_info(lunar_day_idx)
            return second_word + ' is ' + lunar_day_name + '. '+lunar_day_info
        else:
            return 'Aloha I am calendar bot'
    # provided
    def get_lunar_day_idx(self,date):
        left_idx = bisect.bisect_left(self.special_days, self.start_date)    
        right_idx = bisect.bisect_right(self.special_days, date) 
        day_diff = (date-self.start_date).days+(right_idx - left_idx)+self.start_date_lunar_idx
        lunar_day_idx = day_diff % 30
        return lunar_day_idx
    def get_lunar_day_name(self,lunar_day_idx):
        lunar_day_name = self.date_to_lunar_day[lunar_day_idx]
        return lunar_day_name
    def get_lunar_day_info(self,lunar_day_idx):
        lunar_day_info = self.date_to_lunar_day_info[lunar_day_idx]
        return lunar_day_info
    
    # provided:
    def is_date(self,msg):
        try:
            date = parser.parse(msg)
            return True 
        except ValueError:
            return False
    def get_date(self,msg):
        return parser.parse(msg)
   
    def warm_up(self):
        with open('calendar_special_day.txt','r') as f:
            for line in f:
                date = self.get_date(line.strip())
                self.special_days.append(date)
        with open('calendar_lunar_day_name.txt','r') as f:
            for line in f:
                name, date = line.strip().split()
                date = int(date)-1
                self.date_to_lunar_day[date] = name
        
        with open('calendar_lunar_day_info.txt','r') as f:
            for line in f:
                date, *info = line.strip().split()
                date = int(date)
                info = ' '.join(info)
                self.date_to_lunar_day_info[date] = info
        
    async def on_ready(self):

        # Runs when successfully connected to the server
        
        print('Logged on as', self.user)
        self.warm_up()

    async def on_message(self, message):

        # don't respond to ourselves

        if message.author == self.user:

            return


        # This passes the message's text and author name as 

        reply = self.make_reply(message.content, message.author.name)

        if reply:

            await message.channel.send(reply)



if __name__ == "__main__":

    client = CalendarBot()

    client.run(DISCORD_TOKEN)
'''
    def make_reply(self, msg_content, user_name):
        words_splitted_by_space = msg_content.split()
        words_array_length = len(words_splitted_by_space)
        if words_array_length<2:
            return ''

        first_word = words_splitted_by_space[0]

        if first_word != activation_word:
            return ''
        
        second_word = words_splitted_by_space[1]

        if self.said_hi(second_word):
            return 'Aloha ' + user_name

        elif self.ask_for_calendar_info(second_word):
            return self.compute_calendar_info(second_word)

        else:
            return 'Aloha!'
        
    def said_hi(self,word):
        return True
'''
