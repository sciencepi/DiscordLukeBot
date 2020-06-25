import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import sys

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_NAME = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready(): # when the bot connects to discord
    print(f'{client.user} has learned the way of the force!')
    print("Ready.")

class MSGP:
    def __init__(self, message, message_chn):
        self.raw = message
        self.msg = []
        self.pre_msg = message.content
        self.flag = 0x00

    def process(self):
        processed_msg = []
        for i in self.pre_msg.split(" "):
            processed_msg.append(i)
        self.msg = processed_msg

    def run(self):
        msg_tmp = []
        if self.msg[0] == "!ms":
            msg_tmp = self.msg
            del msg_tmp[0]
            reassembled_msg = " ".join(msg_tmp)
            return reassembled_msg

        if self.msg[0] == "!go-to-sleep": # sleepy yoda
            self.flag = 0xff
            return "You shall learn more of the force tomorrow child."
        return ""

    def getflag(self):
        return self.flag

@commands.has_role('Trusted Admin')
@client.event
async def on_message(message): # this gets called every time a user posts something
    if message.author == client.user:
        return
    msgp = MSGP(message, message.channel)
    msgp.process() # you can't delete this!
    rm = msgp.run()

    flag = msgp.getflag()
    if rm != "":
        if flag != 255:
            await message.channel.send(rm)
        if flag == 255:
            await message.channel.send(rm)
            sys.exit()
    
client.run(TOKEN)
