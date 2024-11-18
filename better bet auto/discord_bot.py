import discord
import asyncio

import utils


g_discordClient = discord.Client()
g_discordClientIsReady = False
g_discordChannelId = None
g_QueueToDiscordMessage = []


def discordWriteMessage(message):
    g_QueueToDiscordMessage.append(str(message))
    pass

@g_discordClient.event
async def on_ready():
    global g_discordClientIsReady

    g_discordClientIsReady = True

    utils.log('Bot (name: ' + str(g_discordClient.user.name) +
              ', userid: ' + str(g_discordClient.user.id) + ') is ready')

async def loop():
    await g_discordClient.wait_until_ready()

    channel = discord.Object(id='468619192208326657')

    while True:
        if g_discordClientIsReady:
            if len(g_QueueToDiscordMessage) > 0:
                await g_discordClient.send_message(channel, g_QueueToDiscordMessage[0])
                g_QueueToDiscordMessage.pop(0)

        await asyncio.sleep(0.1)

def init():
    utils.log('discord_bot start')
    g_discordClient.loop.create_task(loop())
    g_discordClient.run('NDY4OTcwMTg1NzM1NTM2Njcx.DjA6bg.NPHbeTN3rz07nPE-L8vrS5ZsOaE')