#/usr/bin/env python3

# Code adapted from https://discordpy.readthedocs.io/

import random

import discord

from dateutil import parser

# This token can be found on the Bot page for your application
with open('calendar_bot.txt',r) as f:
    DISCORD_TOKEN = f.readline().strip()
ACTIVATION_WORD = 'calendar'
class CalendarBot(discord.Client):
    START_DATE = parser.parse('1/1/2021')
    DATE_TO_LUNAR_DAY = []
    # greeting
    def make_reply(self, msg_content, user_name):
        words_splitted_by_space = msg_content.split()
        words_array_length = len(words_splitted_by_space)
        if words_array_length<2:
            return ''

        first_word = words_splitted_by_space[0]

        if first_word != ACTIVATION_WORD:
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

        if first_word != ACTIVATION_WORD:
            return ''
        
        second_word = words_splitted_by_space[1]

        if second_word == 'Aloha':
            return 'Aloha ' + user_name + '!'
        elif self.is_date(second_word):
            date = self.get_date(second_word)
            lunar_day_name = self.get_lunar_day_info(date)
            return second_word + ' is ' + lunar_day_name
        else:
            return 'Aloha I am calendar bot'
    def get_lunar_day_info(self,date):
        day_diff = (date - FIRST_DATE).days
        lunar_day_idx = day_diff % 30
        lunar_day_name = DATE_TO_LUNAR_DAY[lunar_day_idx]
        return lunar_day_name

    # provided:
    def is_date(self,msg):
        try:
            date = parser.parse(msg)
            return True 
        except ValueError:
            return False
    def get_date(self,msg):
        return parser.parse(msg)

    def make_reply(self, msg_content, user_name):
        words_splitted_by_space = msg_content.split()
        words_array_length = len(words_splitted_by_space)
        if words_array_length<2:
            return ''

        first_word = words_splitted_by_space[0]

        if first_word != ACTIVATION_WORD:
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
       
    async def on_ready(self):

        # Runs when successfully connected to the server

        print('Logged on as', self.user)


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

