import os
import random
import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv
import sys
from googlesearch import search
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import csv

print("Training chatbot...")
english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")
trainer = ChatterBotCorpusTrainer(english_bot)
trainer.train("chatterbot.corpus.english")

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_NAME = os.getenv('DISCORD_GUILD')

client = discord.Client()

bot = commands.Bot(command_prefix='!')

## defs that don't have @

def GetDiscordGuild(guild_name):
    GUILD = None
    for guild in client.guilds:
        if guild.name == guild_name:
            GUILD = guild
    return GUILD

async def kick_plr_(plr_name):
    await bot.kick(plr_name)

client_guild = GetDiscordGuild(GUILD_NAME)

ASYNC_FLAGS = [
    "Announcement",
    "Poll Announcement",
    "Poll Closed",
    "Quiz Initiated!",
    "",
    "",
    "",
    "",
    "",
    ""
    ]

class Command_Manager:
    def __init__(self, command_ext_file):
        self.file = open(command_ext_file, "a+")

    def write_command(self, command, user):
        self.file.write("User '"+user.name+"' Used command: '"+command+"'. TIMESTAMP: "+str(datetime.datetime.now())+"\n")

    def close(self):
        self.file.close()
        print("File closed successfully!")


class Poll_Handler:
    def __init__(self):
        self.poll_list = {}

    def add_poll(self, poll_name, keys, player):
        generated_keys_dict = {}

        for i in keys:
            generated_keys_dict[i] = 0

        generated_keys_dict["player"] = player.name
        generated_keys_dict["already_voted"] = []
            
        self.poll_list[poll_name] = generated_keys_dict

    def vote(self, poll_name, key, player):
        try:
            if not (player.name in self.poll_list[poll_name]["already_voted"]):
                self.poll_list[poll_name][key] += 1
                self.poll_list[poll_name]["already_voted"].append(player.name)
            else:
                return "There was a problem with your vote - You've already voted!\n"
            return ""
        except KeyError:
            return str("There is a problem with your vote request - Either '"+poll_name+"' or '"+key+"' are incorrect. Here is a reminder on how to use the command:\
                    \n```\n !vote <poll-name> <target-vote-value>\n```")

    def end_vote(self, poll_name, invoke_player):
        try:
            if invoke_player.name == self.poll_list[poll_name]["player"]:
                # the correct player ended the poll.
                poll_stats = self.poll_list[poll_name]
                del poll_stats["player"]
                del poll_stats["already_voted"]
                del self.poll_list[poll_name]

                return poll_stats
        except KeyError:
            return str("There is a problem with your end poll request - Either '"+poll_name+"' or your player ID are incorrect. Here is a reminder on how to use the command:\
                    \n```\n !endpoll <poll-name>\n```")

class Quiz_Handler:
    def __init__(self):
        self.q = {}
        self.csv_ = []

    def add_quiz(self, quiz_id, length):
        self.q[quiz_id] = {"players":{}, "question_count":0, "already_complete_questions":[], "current_question":[], "num_questions":(length-1)}

    def process_csv(self, QUIZ_FILE):
        with open(QUIZ_FILE) as csv_file:
            csv_r = csv.reader(csv_file, delimiter=",")

            for row in csv_r:
                q = [row[0].lower(), row[1].lower()]
                self.csv_.append(q)

        print("Quiz processed, with questions:")
        print(self.csv_)

    def init_new_quiz(self, quiz_id):
        _q  = random.choice(self.csv_)
        self.q[quiz_id]["current_question"] = _q

        return _q[0]

    def run_quiz(self, quiz_id, player, response):
        if not (player in list(self.q[quiz_id]["players"].keys())):
            self.q[quiz_id]["players"][player] = 0
        if player in list(self.q[quiz_id]["players"].keys()):
            if response == self.q[quiz_id]["current_question"][1]:
                self.q[quiz_id]["already_complete_questions"].append(self.q[quiz_id]["current_question"])
                if self.q[quiz_id]["question_count"] == self.q[quiz_id]["num_questions"]:
                    self.q[quiz_id]["players"][player]+=1

                    top_3_p = []
                    z = player
                    for i in range(0, 3):
                        for plr in list(self.q[quiz_id]["players"].keys()):
                            if self.q[quiz_id]["players"][plr] > self.q[quiz_id]["players"][z]:
                                z = plr
                            top_3_p.append(str(i)+") "+z+": "+str(self.q[quiz_id]["players"][z]))
                            try:
                                del self.q[quiz_id]["players"][z]
                                z = list(self.q[quiz_id]["players"].keys())[0]
                            except:
                                pass

                    top_x = "\n".join(top_3_p)
                    return "Well done to "+player+" for getting the right answer.\n The top 3 scores of the quiz are:\n```"+top_x+"```\n"
                if self.q[quiz_id]["question_count"] != self.q[quiz_id]["num_questions"]:
                    next_q = []
                    i = True

                    while i:
                        next_q = random.choice(self.csv_)
                        if not (next_q in self.q[quiz_id]["already_complete_questions"]):
                            i = False

                    self.q[quiz_id]["current_question"] = next_q
                    self.q[quiz_id]["players"][player]+=1

                    self.q[quiz_id]["question_count"]+=1
                    return "Well done to "+player+" for getting the right answer.\n The next question ["+str(self.q[quiz_id]["question_count"])+"/"+str(self.q[quiz_id]["num_questions"])+"] will be: ```"+next_q[0]+"```\n"
            if response != self.q[quiz_id]["current_question"][1]:
                return "Sorry, "+player+", that's not the right answer. You'll get it next time!"

# some stuff like creating classes
                 
cm = Command_Manager("user_utilised_commands.cmdlog")
ph = Poll_Handler()
qh = Quiz_Handler()

qh.process_csv("quiz.qtp")

class Message_Processor:
    def __init__(self, msg, channel):
        self.pre_msg = msg.content
        self.raw_msg = msg
        self.msg = []
        self.channel = channel

        self.flag = 0x00
        
    def process(self):
        processed_msg = []
        if self.pre_msg[0] == "!":
            cm.write_command(self.pre_msg, self.raw_msg.author)
        for i in self.pre_msg.split(" "):
            processed_msg.append(i)
        self.msg = processed_msg

    def get_flag(self): return self.flag
    
    def run_process(self):
        msg_temp = []
        if self.msg[0] == "!msg":
            self.flag = 0x01
            msg_temp = self.msg
            del msg_temp[0]
            reassembled_msg = " ".join(msg_temp)
            return ["User "+self.raw_msg.author.name+" has something important to say!\n", str("""```css\n""" + reassembled_msg + """```""")]
        
        if self.msg[0] == "!gettime":
            current_time = datetime.datetime.now()
            self.flag = 0x0a
            return "Current time GMT is: "+str(current_time.hour)+":"+str(current_time.minute)
        
        if self.msg[0] == "!bot-shutdown":
            print("Bot shutting down...")
            self.flag = 0xff
            return "Bot is now shutting down. Goodnight everyone!"
        
        if self.msg[0] == "!poll":
            poll_args = []
            poll_player = self.raw_msg.author
            poll_name = self.msg[1]

            for i in range(2, len(self.msg)):
                poll_args.append(self.msg[i])

            ph.add_poll(poll_name, poll_args, poll_player)
            self.flag = 0x02

            poll_key_list = ""
            for i in poll_args:
                poll_key_list += "\n -> "+i
            return ["Poll instantiated by user "+self.raw_msg.author.name+". Poll name: "+poll_name+". Vote now!", str("""```\n You can vote for the following: """+poll_key_list+"""\
                                                                                                                        \n```""")]
        if self.msg[0] == "!vote":
            poll_name = self.msg[1]
            poll_vote = self.msg[2]

            self.flag = 0xfe

            x = ph.vote(poll_name, poll_vote, self.raw_msg.author)
            return x

        if self.msg[0] == "!endpoll":
            player = self.raw_msg.author
            poll_name = self.msg[1]
            x = ph.end_vote(poll_name, player)

            
            if str(type(x)) == "<class 'dict'>":
                self.flag = 0x03

                poll_results = ""
                for i in range(len(x)):
                    poll_results += "\n"+list(x.keys())[i]+": "+str(x[list(x.keys())[i]])

                return ["Poll '"+poll_name+"' was just ended! Here are the results:", str("""```\n"""+poll_results+"""\n```""")]
            if str(type(x)) == "<class 'str'>":
                self.flag = 0xfd
                return x

        if self.msg[0] == "!search":
            msg_temp = self.msg
            del msg_temp[0]
            reassembled_msg = " ".join(msg_temp)

            search_results = []

            for j in search(reassembled_msg, tld="co.in", num=10, stop=10, pause=2):
                search_results.append(j)

            search_ = "\n".join(search_results)
            self.flag = 0xfc

            return "I found some useful results for your query!\n```"+search_+"\n```\n"

        if self.msg[0] == "!talkto":
            msg_temp = self.msg
            del msg_temp[0]
            reassembled_msg = " ".join(msg_temp)

            response = str(english_bot.get_response(reassembled_msg))

            self.flag = 0xfb
            return "```\n"+response+"\n```\n"

        if self.msg[0] == "!quiz":
            quiz_id = self.msg[1]
            num_q = int(self.msg[2])

            qh.add_quiz(quiz_id, num_q)
            _nq = qh.init_new_quiz(quiz_id)

            self.flag = 0x04
            return ["A quiz has been started by user "+self.raw_msg.author.name+". It's sure to be lots of fun! Join in!", "```\nThe first question is: "+_nq+"\n```"]

        if self.msg[0] == "!qa":
            quiz_id = self.msg[1]
            msg_temp = self.msg
            del msg_temp[0]
            del msg_temp[0]
            ans = " ".join(msg_temp)
            ans = ans.lower()

            ex = qh.run_quiz(quiz_id, self.raw_msg.author.name, ans)
            self.flag = 0xf9
            return ex
        return ""
            

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print("Bot is ready to run commands.")

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, Welcome to the Titan Doge Simulator discord server, just a heads up - \n all admin commands you enter will be recorded to help\
                                    keep this server happy and healthy. Have fun!')
    print("New member '"+member.name+"' has joined the server.")

@client.event
@commands.has_role('Trusted Admin')
async def on_message(message):
    if message.author == client.user:
        return

    msgp = Message_Processor(message, message.channel)
    msgp.process()
    return_msg = msgp.run_process()
    flag = msgp.get_flag()

    if return_msg != "":
        if flag <= 9:
            emb = discord.Embed(title=ASYNC_FLAGS[flag-1])
            emb.add_field(name=return_msg[0],value=return_msg[1])
            await message.channel.send(embed=emb)
        if flag > 9:
            await message.channel.send(return_msg)
            if flag == 255:
                cm.close()
                sys.exit()
        #await message.channel.send(return_msg)
    #if message.content == ':msg':
    #    response = random.choice(brooklyn_99_quotes)
    #    await message.channel.send(response)

client.run(TOKEN)

