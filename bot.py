# bot.py
import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import random
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.ticker import MaxNLocator


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('SERVER_NAME')

intent = discord.Intents.default()
intent.members = True
intent.message_content = True
intent.messages = True

class userResponse:
    def __init__(self, name, response):
        self.username = name
        self.response = response

class graphResponses:
    def __init__(self, response, votes):
        self.response = response
        self.votes = votes

bot = commands.Bot(command_prefix='!', intents=intent)

class pollView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, answer, author, timeout):
        super().__init__(timeout=timeout)
        #self.callback = callback
        self.answer = answer
        self.savedResponses = []
        self.author = author
        self.createButton()

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True


    def createButton(self):
        endButton = discord.ui.Button(label="End", custom_id="End", style=discord.ButtonStyle.danger)
        self.add_item(endButton)

        async def end_callback(interaction: discord.Interaction):
            
            print(f"{interaction.data['custom_id']} button clicked by {interaction.user}")
            if(interaction.user == self.author):
                for x in self.children:
                    x.disabled=True
                self.timeout = 1
                await interaction.response.edit_message(view=self)
                
            else:
                print(f"Not original author: {self.author} ")

        endButton.callback = end_callback

        for x in self.answer:
            tempButton = discord.ui.Button(label=x, custom_id=x, style=discord.ButtonStyle.primary)
            self.add_item(tempButton)
        
        async def button_callback(interaction: discord.Interaction): #onclick...run all this
            await interaction.response.defer()
            inResponse = False
            for index in range(0, len(self.savedResponses)):
                if(interaction.user.name == self.savedResponses[index].username):
                    print("user is in list...not saving response")
                    inResponse = True
                    break
            if(inResponse == False):
                self.savedResponses.append(userResponse(interaction.user.name, interaction.data['custom_id']))
            for y in self.savedResponses:
                 print(y.username, y.response)
        for z in range(0, len(self.children)):
            if(self.children[z].label != "End"):
                self.children[z].callback = button_callback


@bot.event
async def on_ready():
    print ("connected")
    guild = discord.utils.get(bot.guilds, name=SERVER)
    print(f"in {guild.name}")
    print(
             f'{bot.user} is connected to the following guild:\n'
             f'{guild.name}(id: {guild.id})\n'
         )

@bot.command(name='spongebob')
async def spongebob(ctx):

    some_response = ['hinga dinga durgin', "these claws ain't just for attractin' mates", "goodbye everyone! i'll remember you all in therapy",
                     "is mayonnaise an instrument?", "give to the children's fund? why?! what have the children ever done for me?", 
                     "i'll have you know, i stubbed my toe last week, while watering my spice garden, and i only cried for 20 minutes!",
                     "patrick, don't you have to be stupid somewhere else?\nnot until 4", "wake me up when i care","you like krabby patties don't you squidward?", 
                     "don't encourage them! they'll never leave", "squidward that's not the peace treaty that's a copy of the peace treaty", 
                     "excuse me, sir, you are sitting on my body...which is also my face", 
                     "well this is stupid, there's no room in here!\ni told you you wouldn't fit!\nwe've been stuck up here for 3 days", 
                     "this is not your average everyday darkness...this is...ADVANCED DARKNESS!!"]

    response = random.choice(some_response)
    await ctx.send(response)

@bot.command(name='poll')
async def runPoll(ctx):

    bot_channel = discord.utils.get(ctx.guild.channels, name='☾—robot-friends')
    general = discord.utils.get(ctx.guild.channels, name='☾—friends-we-are-friends')
    bot_channel_id = bot_channel.id
    general_id = general.id

    ending = bot.get_channel(general_id)

    if ctx.channel.id is not bot_channel_id:
        return

    await ctx.author.create_dm() #dm who called !poll
    pollQuestion = '' #init poll question
    pollAnswers = [] #init all poll answers
    userTimeout = 0

    await ctx.author.dm_channel.send(f"Hello {ctx.author}, what will be the poll question?")

    def check(msg): #same user who called !poll
        return msg.author == ctx.author
    
    msg = await bot.wait_for("message", check=check)
    
    pollQuestion = msg.content #fill in poll question with response

    while(True):

        await ctx.author.dm_channel.send("Input how many seconds the poll should run?")

        msg = await bot.wait_for("message", check=check)

        if(msg.content.isdigit()):

            userTimeout = int(msg.content)
            break
        
        else:
            await ctx.author.dm_channel.send("Invalid input...please try again")

    await ctx.author.dm_channel.send("Input answers separated by commas (e.g yes,no,n/a): ")

    msg = await bot.wait_for("message", check=check)

    input_str = msg.content
    pollAnswers = input_str.split(',')

    await ctx.author.dm_channel.send(f"Is this correct?\nPoll Question: {pollQuestion}\nPoll Responses: {pollAnswers}\nDuration: {userTimeout} seconds\n\n(Respond with 'y' for Yes)")

    msg = await bot.wait_for("message", check=check)

    if(msg.content != 'y'):
        await ctx.author.dm_channel.send("Poll generation terminated")

    else:

        await ctx.author.dm_channel.send("Poll submitted!")

        await ending.send(f'Poll Question: {pollQuestion}')

        view = pollView(pollAnswers, ctx.author, timeout=userTimeout)

        await ending.send(f"Poll will run for {userTimeout} seconds!\nPlease Select One:", view=view)

        print(view.timeout)

        await view.wait()

        await ending.send("Poll has concluded! Here are the results...")

        #for x in view.savedResponses:
        #    await ctx.send(f'{x.username}, {x.response}')

        toGraph = []

        for x in view.answer:
            toGraph.append(graphResponses(x, 0))

        for x in toGraph:
            for y in view.savedResponses:
                if(x.response == y.response):
                    x.votes += 1

        # for z in toGraph:
        #     print(f"{z.response}, {z.votes}")

        
        # print(f"here is len of toGraph: {len(toGraph)}") #TEST THESE TWO PRINT STATEMENTS BECAUSE X AND Y ARE ONLY GOING FROM 0 TO 1 INSTEAD OF 0 TO 2
        # print(f"here is max: {max(count.votes for count in toGraph)}")

        x = np.array([*range(0, len(toGraph))])
        # y = np.array([*range(0, max(count.votes for count in toGraph))])
        #y = max(count.votes for count in toGraph)

        # print(f'here is x: {x}')
        # print(f'here is y: {y}')
        
        ax = plt.figure().gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        xLabel = []
        for m in toGraph:
            xLabel.append(m.response)
        plt.xticks(x, xLabel)
        for n in x:
            plt.bar(n,toGraph[n].votes, width = .5, color='#fa4b4b')
        

        plt.xlabel('Responses')
        plt.ylabel('Votes')
        plt.title(f'{pollQuestion}')
        
        plt.savefig('graph.png')
        
        # # Send plot to channel
        with open('graph.png', 'rb') as f:
            picture = discord.File(f)
            await ending.send(file=picture)

    # while(True):

    #     if(addQuestion):

    #         await ctx.author.dm_channel.send("Input answer: ")

    #         msg = await bot.wait_for("message", check=check)

    #         pollAnswers.append(msg.content)

    #         await ctx.author.dm_channel.send("Would you like to add another answer? (y/n)")
            
    #         msg = await bot.wait_for("message", check=check)

    #         if(msg.content == 'y' or msg.content == 'Y'):
    #             addQuestion = True

    #         else:
    #             addQuestion = False

    #     else:
            # await ctx.author.dm_channel.send("Poll completed!")

            # await ctx.send(f'Poll Question: {pollQuestion}')
        
            # view = pollView(pollAnswers)

            # await ctx.send(f"Please Select One", view = view)

            # break




bot.run(TOKEN)

#client.run(TOKEN)