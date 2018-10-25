import random
import discord
import asyncio
from discord import Game
from discord.ext.commands import Bot

BOT_PREFIX = "n!"
TOKEN = "NTAwOTYwMjc3NjY0MzY2NjAy.DqSjwg.KHvktaWimh2TK06MWcHyQq2hLy0"
BOT_CHANNEL_ID = "503919801169870849"
LFG_CHANNEL_ID = "501020750115766282"

client = Bot(command_prefix=BOT_PREFIX, pm_help=True)
client.remove_command('help')

ls_messagePack = []

class MessagePack:
    def __init__(self, message, timestamp, embed, owner):
        (date, time) = datetime_to_string(timestamp)
        self.countdown = 2
        self.commandMessage = message
        self.date = date
        self.time = time
        self.embedMessage = embed
        self.owner = owner

def embedCreate(username, link, sessionID, description, voice_channel, timeformat):
    (date, time) = datetime_to_string(timeformat)
    colors = [0xFF0000,0x00FF00,0x0000FF,0xFFFF00,0xFF00FF,0x00FFFF]
    embed = discord.Embed(title="```\n" + description + "\n```",description=username, color=random.choice(colors))
    embed.set_thumbnail(url=link)
    embed.add_field(name="Session ID", value=sessionID, inline=True)
    embed.add_field(name="Voice Channel: ", value=voice_channel, inline=False)
    embed.add_field(name="Time Created", value=date + " " + time, inline=False)
    return embed

def datetime_to_string(timeformat):
    (date, time) = str(timeformat).split()
    time = time[:-10]
    intTime = (int(time[:2])+7) % 24
    time = str(intTime) + time[2:]
    return (date, time)

def getUrl(user):
    if not user:
        return  # Can't find the user, then quit
    return user.avatar_url

async def task():
    global LFG_CHANNEL_ID
    global ls_messagePack
    await client.wait_until_ready()
    while not client.is_closed:
        for e in ls_messagePack:
            if e.countdown == 0:
                await client.send_message(discord.Object(id=BOT_CHANNEL_ID), e.owner.mention + "โพสต์ของเจ้าได้หมดเวลาลงแล้ว!")
                await client.delete_message(e.embedMessage)
                ls_messagePack.remove(e)
            else:
                e.countdown -= 1;
        await asyncio.sleep(5)

@client.event
async def on_ready():
    await client.change_presence(game = Game(name = "with Darken"))
    print("Logged in as " + client.user.name)

@client.command(pass_context = True)
async def cr(ctx, *args):
    global LFG_CHANNEL_ID
    global messageMap
    ls_msg = []
    if len(args) != 0:
        ls_msg = [e for e in args]
    if(len(ls_msg) >= 3):
        (sessionID, voice_channel) = ls_msg[:2]
        description = " ".join(ls_msg[2:])
        userID = ctx.message.server.get_member(ctx.message.author.id)
        embed = embedCreate(str(ctx.message.author.mention), getUrl(userID), sessionID, description, voice_channel, str(ctx.message.timestamp))
        await client.send_message(discord.Object(id=LFG_CHANNEL_ID), embed=embed)
        messages = []
        async for msg in client.logs_from(discord.Object(id=LFG_CHANNEL_ID), limit=50):
            messages.append(msg)
            break
        for msg in messages:
            # await client.add_reaction(msg, emoji="🔁")
            messagePack = MessagePack(ctx.message, ctx.message.timestamp, msg, ctx.message.author)
            ls_messagePack.append(messagePack)
            await client.add_reaction(msg, emoji='\U0001F5D1')

    else:
        await client.send_message(ctx.message.channel, "รูปแบบคำสั่งที่ถูกต้อง จะต้องเป็น `n!cr [Session ID] [Voice channel] คำอธิบาย...` เท่านั้นนะ!")

@client.event
async def on_reaction_add(reaction, user):
    global ls_messagePack
    authorized = False
    for e in ls_messagePack:
        if e.owner == user and e.commandMessage.author == user:
            authorized = True
            break
    if reaction.emoji == '\U0001F5D1' and user != client.user:
        if authorized:
            await client.send_message(discord.Object(id=BOT_CHANNEL_ID), "ลบโพสต์เรียบร้อย! " + user.mention)
            await client.delete_message(reaction.message)
        else:
            await client.send_message(discord.Object(id=BOT_CHANNEL_ID), "ข้าแอบเห็นนะว่าเจ้าพยายามจะลบโพสต์ของคนอื่นน่ะ! " + user.mention)
            await client.remove_reaction(reaction.message, '\U0001F5D1', user)

client.loop.create_task(task())
client.run(TOKEN)
