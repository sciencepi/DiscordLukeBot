import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import sys

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_NAME = os.getenv('DISCORD_GUILD')

client = discord.Client()
def get_roles(msg):
    roles = msg.author.roles
    role_name_list = [i.name.lower() for i in roles]

    return role_name_list

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
        if self.msg[0] == "!kick":
            _user_roles = get_roles(self.raw)
            if ("trusted admin" in _user_roles) or ("trial admin" in _user_roles) or ("emperor! owner rank of all power!" in _user_roles):
                try:
                    self.flag = 200
                    kick_user = self.msg[1]
                    kick_user_dt = kick_user.split("+")
                    kick_user = " ".join(kick_user_dt)
                    temp_kick = self.msg
                    del temp_kick[0]
                    del temp_kick[0]

                    if temp_kick == []:
                        raise IndexError

                    kick_reason = ""
                    kick_reason = " ".join(temp_kick)

                    return [kick_user, kick_reason]
                except IndexError:
                    self.flag = 0xfe
                    return "I'm afraid you haven't used the command correctly. I can show you how though:\n```!kick <username - can't be more than one word. Use + to seperate words> <reason - can contain spaces>\
                            \n```\n"
            else:
                self.flag = 0xfe
                return "I'm afraid you can't use this command - only trusted admins, trial admins, and the server owner and founders can use this command. Sorry - you'll get there one day!\n"

        if self.msg[0] == "!ban":
            _user_roles = get_roles(self.raw)
            if ("trusted admin" in _user_roles) or ("emperor! owner rank of all power!" in _user_roles) or ("all powerful (kings)" in _user_roles):
                try:
                    self.flag = 201
                    kick_user = self.msg[1]
                    kick_user_dt = kick_user.split("+")
                    kick_user = " ".join(kick_user_dt)
                    temp_kick = self.msg
                    del temp_kick[0]
                    del temp_kick[0]

                    if temp_kick == []:
                        raise IndexError

                    kick_reason = ""
                    kick_reason = " ".join(temp_kick)

                    return [kick_user, kick_reason]
                except IndexError:
                    self.flag = 0xfe
                    return "I'm afraid you haven't used the command correctly. I can show you how though:\n```!ban <username - can't be more than one word. Use + to seperate words> <reason - can contain spaces>\
                            \n```\n"
            else:
                self.flag = 0xfe
                return "I'm afraid you can't use this command - only trusted admins, the server owner and the founders can use this command. Sorry - you'll get there one day!\n"
        return ""

    def getflag(self):
        return self.flag

def get_member(members_list, member_name):
    member_index = None
    for x in range(len(members_list)):
        if members_list[x].name == member_name:
            member_index = x
            return member_index
    return member_index

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
        if flag != 255 and flag != 200 and flag != 201:
            await message.channel.send(rm)
        if flag == 200 or flag == 201:
            if flag == 200:
                members = message.guild.members

                m = get_member(members, rm[0])
                if m != None:
                    m = members[m]
                    await m.create_dm()
                    await m.dm_channel.send("Sadly, you have been kicked from the discord sever. I am so sorry I had to deliver the news. The reason for your kick: ```\n"+rm[1]+"\n```\n")
                    await m.kick(reason="")
                if m == None:
                    await message.channel.send("The user you requested to be kicked does not exist.")
            if flag == 201:
                members = message.guild.members

                m = get_member(members, rm[0])
                if m != None:
                    m = members[m]
                    await m.create_dm()
                    await m.dm_channel.send("Sadly, you have been banned from the discord sever. I am so sorry I had to deliver the news. The reason for your ban: ```\n"+rm[1]+"\n```\n")
                    await m.ban(reason="")
                if m == None:
                    await message.channel.send("The user you requested to be banned ('"+rm[0]+"') does not exist.")
        if flag == 255:
            await message.channel.send(rm)
            sys.exit()
    
client.run(TOKEN)
