import random
import discord
import asyncio
from discord import Game
from discord.ext.commands import Bot

BOT_PREFIX = "n!"
TOKEN = "NTAwOTYwMjc3NjY0MzY2NjAy.DqSjwg.KHvktaWimh2TK06MWcHyQq2hLy0"
BOT_CHANNEL_ID = "503919801169870849"
LFG_CHANNEL_ID = "501020750115766282"

REFRESH_RATE = 60
COUNTDOWN = 30

client = Bot(command_prefix=BOT_PREFIX, pm_help=True)
client.remove_command('help')

ls_messagePack = []
posted_user = set()

class MessagePack:
    def __init__(self, message, timestamp, embed, owner):
        global COUNTDOWN
        (date, time) = datetime_to_string(timestamp)
        self.countdown = COUNTDOWN
        self.commandMessage = message
        self.date = date
        self.time = time
        self.embedMessage = embed
        self.owner = owner

def embedCreate(username, link, sessionID, description, voice_channel, timeformat):
    (date, time) = datetime_to_string(timeformat)
    (hour, minute) = time_to_expire(time)
    colors = [0xFF0000,0x00FF00,0x0000FF,0xFFFF00,0xFF00FF,0x00FFFF]
    embed = discord.Embed(title="```\n" + description + "\n```",description=username, color=random.choice(colors))
    embed.set_thumbnail(url=link)
    embed.add_field(name="Session ID", value=sessionID, inline=True)
    embed.add_field(name="Voice Channel: ", value=voice_channel, inline=False)
    embed.add_field(name="Expire on", value=hour + ":" + minute, inline=False)
    return embed

def datetime_to_string(timeformat):
    (date, time) = str(timeformat).split()
    time = time[:-10]
    intTime = (int(time[:2])+7) % 24
    time = str(intTime) + time[2:]
    return (date, time)

def time_to_expire(time):
    global REFRESH_RATE
    global COUNTDOWN
    timeAmount = (REFRESH_RATE * COUNTDOWN) // 60
    (strhour, strminute) = time.split(":")
    hour = int(strhour)
    minute = int(strminute)
    minute += timeAmount
    while minute > 60:
        hour += 1
        minute -= 60
    if minute < 10: strminute = "0" + str(minute)
    else: strminute = str(minute)
    strhour = str(hour % 24)

    return (strhour, strminute)

def getUrl(user):
    if not user:
        return  # Can't find the user, then quit
    return user.avatar_url

async def task():
    global LFG_CHANNEL_ID
    global ls_messagePack
    global posted_user
    global REFRESH_RATE
    await client.wait_until_ready()
    while not client.is_closed:
        for e in ls_messagePack:
            if e.countdown == 0:
                await client.send_message(discord.Object(id=BOT_CHANNEL_ID), e.owner.mention + "โพสต์ของเจ้าได้หมดเวลาลงแล้ว!")
                await client.delete_message(e.embedMessage)
                posted_user.remove(e.owner)
                ls_messagePack.remove(e)
            else:
                e.countdown -= 1;
        await asyncio.sleep(REFRESH_RATE)

@client.event
async def on_ready():
    await client.change_presence(game = Game(name = "with Darken"))
    print("Logged in as " + client.user.name)

@client.command(pass_context = True)
async def help(ctx):
    commands = dict()
    commands['`n!cr [Session ID] [Voice channel] คำอธิบาย...`'] = 'สร้างโพสต์หาเพื่อนเล่น (เวลาพิมพ์คำสั่งจริงๆไม่ต้องมี [] นะ)'
    commands['`n!setchannel [lfg หรือ bot] [Channel ID]`'] = 'Set Channel ไว้ให้บอทประกาศใส่'
    commands['`n!getchannel'] = 'สั่งบอทให้รายงาน LFG/BOT Channel ในปัจจุบัน ว่าบอทกำลังใช้ Channel ไหนอยู่'
    msg = discord.Embed(title='Nergigante',
                        description="Written by darkenstardragon#2672",
                        color=0x0000ff)
    for command, description in commands.items():
        msg.add_field(name=command, value=description, inline=False)
    await client.send_message(ctx.message.channel, embed=msg)

@client.command(pass_context = True)
async def newbutton(ctx):
    msg = await client.send_message(ctx.message.channel, "กด React ที่รูป \U0001F195 ด้านล่าง เพื่อโพสต์")
    await client.add_reaction(msg, "\U0001F195")

@client.command(pass_context = True)
async def cr(ctx, *args):
    global LFG_CHANNEL_ID
    global messageMap
    global posted_user
    if ctx.message.author in  posted_user:
        await client.send_message(ctx.message.channel, "เจ้ามีโพสต์ LFG อยู่ที่ <#" + LFG_CHANNEL_ID + "> อยู่แล้วนะ!")
        return
    ls_msg = []
    if len(args) != 0:
        ls_msg = [e for e in args]
    if(len(ls_msg) >= 3):
        (sessionID, voice_channel) = ls_msg[:2]
        description = " ".join(ls_msg[2:])
        if len(sessionID) != 11:
            await client.send_message(ctx.message.channel, "`%s` ไม่น่าจะเป็น Session ID ที่ถูกต้องนะ.. ลองตรวจสอบใหม่ดูก่อนสิ!" % sessionID)
            return
        userID = ctx.message.server.get_member(ctx.message.author.id)
        embed = embedCreate(str(ctx.message.author.mention), getUrl(userID), sessionID, description, voice_channel, str(ctx.message.timestamp))
        await client.send_message(discord.Object(id=LFG_CHANNEL_ID), embed=embed)
        posted_user.add(ctx.message.author)
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
    global posted_user
    authorized = False
    for e in ls_messagePack:
        if e.owner == user and e.commandMessage.author == user:
            authorized = True
            ls_messagePack.remove(e)
            break
    if reaction.emoji == '\U0001F5D1' and user != client.user and user in posted_user:
        if authorized:
            await client.send_message(discord.Object(id=BOT_CHANNEL_ID), "ลบโพสต์เรียบร้อย! " + user.mention)
            await client.delete_message(reaction.message)
            posted_user.remove(user)
        else:
            await client.send_message(discord.Object(id=BOT_CHANNEL_ID), "ข้าแอบเห็นนะว่าเจ้าพยายามจะลบโพสต์ของคนอื่นน่ะ! " + user.mention)
            await client.remove_reaction(reaction.message, '\U0001F5D1', user)

    if reaction.emoji == '\U0001F195' and user != client.user:
        ls_message_input = []
        ls_message_output = [
            "\nสวัสดี! ข้าเห็นว่าเจ้าต้องการจะโพสต์หาปาร์ตี้สินะ ก่อนอื่นก็บอก **Session ID** ของเจ้ามาก่อนสิ!\nแต่ถ้าหากถ้าเจ้าต้องการจะยกเลิก ก็สามารถพิมพ์ `stop` ได้ทุกเมื่อนะ!",
            "\nแล้ว **Voice Channel** ล่ะ เจ้าจะใช้มันหรือไม่ ถ้าใช้ก็**พิมพ์ชื่อห้อง**มาเลย อย่าลืมว่าต้องพิมพ์แบบ*ไม่มีเว้นวรรค*นะ!\nแต่ถ้าหากเจ้าจะ**ไม่ใช้ Voice Channel** ก็พิมพ์ `-` มาเฉยๆเลยก็ได้!",
            "\nสุดท้ายแล้ว **อธิบาย**มาหน่อยสิว่า ปาร์ตี้ของเจ้าต้องการที่จะทำอะไร จะล่าตัวอะไร หรือต้องการความช่วยเหลืออะไร บอกมาให้หมดทีเดียวได้เลย!"
        ]
        for i in range(3):
            await client.send_message(discord.Object(id=BOT_CHANNEL_ID), user.mention + ls_message_output[i])
            msg = await client.wait_for_message(author=user, timeout=60)
            ls_message_input.append(msg.content)
            if ls_message_input[i] == 'stop':
                await client.send_message(discord.Object(id=BOT_CHANNEL_ID), "ยกเลิกการสร้างโพสต์เรียบร้อย!")
                return
        await client.send_message(reaction.message.channel, ls_message_input[0] + ls_message_input[1] + ls_message_input[2])
        # TODO add LFG post

@client.command(pass_context = True)
async def setchannel(ctx, *args):
    global LFG_CHANNEL_ID
    global BOT_CHANNEL_ID
    if len(args) < 2:
        await client.send_message(ctx.message.channel, "รูปแบบคำสั่งจะต้องเป็น `?setchannel [LFG or BOT] [Channel ID]` เท่านั้นนะ!")
        return
    (type, id) = args
    if type.lower() == "lfg":
        id = id[2:-1]
        LFG_CHANNEL_ID = id;
        await client.send_message(ctx.message.channel, "ต่อไปนี้ ข้าจะโพสต์ LFG ที่ <#%s> ล่ะนะ!" % LFG_CHANNEL_ID)
    elif type.lower() == "bot":
        id = id[2:-1]
        BOT_CHANNEL_ID = id;
        await client.send_message(ctx.message.channel, "นับจากนี้ไป ข้าจะถือว่า <#%s> เป็น Channel ของข้าละนะ!" % BOT_CHANNEL_ID)
    else:
        await client.send_message(ctx.message.channel, "รูปแบบคำสั่งจะต้องเป็น `?setchannel [LFG or BOT] [Channel ID]` เท่านั้นนะ!")

@client.command(pass_context = True)
async def getchannel(ctx):
    global LFG_CHANNEL_ID
    global BOT_CHANNEL_ID
    await client.send_message(ctx.message.channel, "LFG Channel: <#%s>\nBOT Channel: <#%s>" % (LFG_CHANNEL_ID, BOT_CHANNEL_ID))

client.loop.create_task(task())
client.run(TOKEN)
