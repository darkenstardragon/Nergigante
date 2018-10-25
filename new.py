import random
import asyncio
import aiohttp
import json
from testing_method import *
import discord
from discord import Game
from discord.ext.commands import Bot

BOT_PREFIX = ("n!")
TOKEN = "NTAwOTYwMjc3NjY0MzY2NjAy.DqSjwg.KHvktaWimh2TK06MWcHyQq2hLy0"
BOT_CHANNEL_ID = "503919801169870849"
LFG_CHANNEL_ID = "501020750115766282"
authorized_user = set()

client = Bot(command_prefix=BOT_PREFIX, pm_help=True)
client.remove_command('help')



@client.command(pass_context = True)
async def help(ctx):
    commands = dict()
    commands['`n!cr [Session ID] [Voice channel] คำอธิบาย...`'] = 'สร้างโพสต์หาเพื่อนเล่น (เวลาพิมพ์คำสั่งจริงๆไม่ต้องมี [] นะ แต่ว่าตรงคำอธิบายจำเป็นต้องมี "..." ครอบ'
    commands['`n!setchannel [lfg หรือ bot] [Channel ID]`'] = 'Set Channel ไว้ให้บอทประกาศใส่'
    commands['`n!authorize [+ หรือ -]`'] = 'เวลาลบโพสต์ของตัวเองไม่ได้ ให้พิมพ์ `n!authorize +`'
    msg = discord.Embed(title='Nergigante',
                        description="Written by darkenstardragon#2672",
                        color=0x0000ff)
    for command, description in commands.items():
        msg.add_field(name=command, value=description, inline=False)
    await client.send_message(ctx.message.channel, embed=msg)

@client.command(pass_context = True)
async def square(context, number):
    squared_val = int(number) * int(number)
    await client.say(context.message.author.mention + " " + str(number) + "'s square is " + str(squared_val))

@client.event
async def on_ready():
    await client.change_presence(game = Game(name = "with Darken"))
    print("Logged in as " + client.user.name)

@client.command(pass_context = True)
async def test(ctx):
    await client.send_message(ctx.message.channel, "Hello! " + ctx.message.author.mention)

@client.command(pass_context = True)
async def cr(ctx, *args):
    global LFG_CHANNEL_ID
    global authorized_user
    ls_msg = []
    if ctx.message.author in authorized_user:
        await client.send_message(ctx.message.channel, 'เจ้ามีโพสต์ LFG ใน <#%s> อยู่แล้วนะ! ลบอันเก่าออกก่อนซะถ้าเจ้าอยากจะโพสต์ใหม่'.format(ctx.message) % LFG_CHANNEL_ID)
        return
    '''
    if len(args) == 0:
        await client.send_message(ctx.message.channel, "สวัสดี {0.author.mention} ... เจ้ากำลังจะสร้างโพสต์ LFG ก่อนอื่นก็บอก **Session ID** ของเจ้ามาก่อนสิ \n \
        แต่ถ้าต้องการจะหยุดสร้าง LFG ให้พิทพ์ `stop` มาได้เลย".format(ctx.message))
        msg = client.wait_for_message(timeout=60, author=ctx.message.author)
        if msg == "stop": return
        ls_msg.append(msg)

        await client.send_message(ctx.message.channel,"{0.author.mention} เยี่ยม! **Session ID** ของเจ้าคือ **%s** สินะ \n ต\่อไปก็บอกข้าหน่อยสิว่าเจ้าจะใช้ **Voice Channel** ห้องไหน ถ้าไม่ใช้ ให้พิมพ์ - มาเฉยๆ".format(ctx.message) % msg.content)
        msg = client.wait_for_message(timeout=60, author=ctx.message.author)
        if msg == "stop": return
        ls_msg.append(msg)

        await client.send_message(ctx.message.channel, "{0.author.mention} สุดท้ายแล้ว **อธิบาย**มาหน่อยว่าปาร์ตี้เจ้านั้นต้องการทำอะไร ล่าตัวอะไร หาของอะไร หรือต้องการความช่วยเหลือ ก็ว่ามาได้เลย!".format(ctx.message))
        msg = client.wait_for_message(timeout=60, author=ctx.message.author)
        if msg == "stop": return
        ls_msg.append(msg)
    '''

    if len(args) >= 3 or len(ls_msg) >= 3:
        if len(ls_msg) < 3: ls_msg = [e for e in args]
        (sessionID, voice_channel) = ls_msg[:2]
        description = " ".join(ls_msg[2:])
        await client.send_message(ctx.message.channel,'สวัสดี {0.author.mention} ... ข้าสร้าง LFG ของเจ้าไว้ที่ <#%s> เรียบร้อยแล้ว \n**!!!อย่าลืมลบโพสต์โดยการคลิก \U0001F5D1 บนโพสต์ของเจ้าหลังใช้งานเสร็จด้วย!!!**'.format(ctx.message) % LFG_CHANNEL_ID)
        userID = ctx.message.server.get_member(ctx.message.author.id)
        embed = embedCreate(str(ctx.message.author.mention), getUrl(userID), sessionID, description, voice_channel)
        await client.send_message(discord.Object(id=LFG_CHANNEL_ID), embed=embed)

        messages = []
        async for msg in client.logs_from(discord.Object(id=LFG_CHANNEL_ID), limit=50):
            messages.append(msg)
            break
        for msg in messages:
            # await client.add_reaction(msg, emoji="🔁")
            await client.add_reaction(msg, emoji='\U0001F5D1')
            authorized_user.add(ctx.message.author)
    else: await client.send_message(ctx.message.channel, "รูปแบบคำสั่งที่ถูกต้อง จะต้องเป็น `n!cr [Session ID] [Voice channel] คำอธิบาย...` เท่านั้นนะ!")

@client.command(pass_context = True)
async def authorize(ctx, type):
    global authorized_user
    if type == "+":
        if ctx.message.author not in authorized_user:
            authorized_user.add(ctx.message.author)
        else:
            await client.send_message(ctx.message.channel, '{0.author.mention is already exist in authorized_user}'.format(ctx.message))
    elif type == "-":
        if ctx.message.author in authorized_user:
            authorized_user.remove(ctx.message.author)
        else:
            await client.send_message(ctx.message.channel,'{0.author.mention is not yet exist in authorized_user}'.format(ctx.message))
    else:
        await client.send_message(ctx.message.channel,'คำสั่งจะต้องเป็นรูปแบบ `n!authorize [+ or -]` เท่านั้นนะ!'.format(ctx.message))

@client.command(pass_context = True)
async def setchannel(ctx, type, channelID):
    global LFG_CHANNEL_ID
    global BOT_CHANNEL_ID
    if type == "lfg":
        LFG_CHANNEL_ID = channelID
        await client.send_message(ctx.message.channel,"ต่อไปนี้ข้าจะโพสต์ LFG ลงที่ <#%s> ล่ะนะ!".format(ctx.message) % LFG_CHANNEL_ID)
    elif type == "bot":
        BOT_CHANNEL_ID = channelID
        await client.send_message(ctx.message.channel,"ต่อไปนี้ข้าจะถือว่า <#%s> เป็น channel ของข้าล่ะนะ!".format(ctx.message) % BOT_CHANNEL_ID)
    else:
        await client.send_message(ctx.message.channel, "คำสั่งจะต้องเป็นรูปแบบ `n!setchannel [lfg หรือ bot] [channelID]` เท่านั้นนะ! " + user.mention)

@client.event
async def on_reaction_add(reaction, user):
    global authorized_user
    if reaction.emoji == '\U0001F5D1' and user != client.user and user in authorized_user:
        await client.send_message(discord.Object(id=BOT_CHANNEL_ID), "ลบโพสต์เรียบร้อย! " + user.mention)
        await client.delete_message(reaction.message)
        await client.send_message(reaction.message.channel, reaction.message.timestamp)
        reaction.message.embeds
        authorized_user.remove(user)
    if reaction.emoji == '\U0001F501' and user != client.user:
        await client.send_message(reaction.message.channel, "repeat!")

def embedCreate(username, link, sessionID, description, voice_channel):
    colors = [0xFF0000,0x00FF00,0x0000FF,0xFFFF00,0xFF00FF,0x00FFFF]
    embed = discord.Embed(title="```" + description + "```",description=username, color=random.choice(colors))
    embed.set_thumbnail(url=link)
    embed.add_field(name="sessionID", value=sessionID, inline=False)
    embed.add_field(name="Voice Channel: ", value=voice_channel, inline=False)
    return embed

def getUrl(user):
    if not user:
        return  # Can't find the user, then quit
    return user.avatar_url



# client.loop.create_task(list_servers())
client.run(TOKEN)
