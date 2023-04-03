import os
from datetime import date
from discord import app_commands
import discord
from discord.ext import commands, tasks

from config.bot_info import MY_GUILD, application_id, bot_token, pre

intents = discord.Intents.all()


class Kanata2(commands.Bot):
    def __init__(self, *, intents:discord.Intents):
        super().__init__(command_prefix = pre, intents = intents, application_id = application_id, help_command=None)

    async def setup_hook(self):
        for files in os.listdir('./cogs'):
            if files.endswith('.py'):
                await self.load_extension(f'cogs.{files[:-3]}')


client = Kanata2(intents=intents)

#@client.tree.context_menu(name = 'poke')
#async def poke(interaction:discord.Interaction, member:discord.Member):
#    if member.bot:
#        return await interaction.response.send_message(f'你不能戳機器人！他不會有感覺的！', ephemeral=True)
#    await interaction.response.send_message(f'你戳了{member}', ephemeral=True)
#    from view.poking import poking
#    view = poking(member_poke=interaction.user, member_poked=member)
#    return await member.send(content=f'{interaction.user} aka {interaction.user.display_name} 戳了你一下！', view = view)

@client.event
async def on_ready():
    client.tree.copy_global_to(guild = MY_GUILD)
    await client.tree.sync(guild = MY_GUILD)
    print(f'Bot is ready{client.user}')
    return await client.change_presence(status = discord.Status.online, activity = discord.Game(name = '學測終於結束了接下來是更累的東西'))

client.run(bot_token)