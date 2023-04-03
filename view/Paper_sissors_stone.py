from re import I
import re
import discord 
import random
from discord import ActivityType, Message, Reaction, ButtonStyle, TextChannel, User, Interaction, app_commands, Member, Guild
from discord.ext import commands
from datetime import datetime, timedelta, date
from pytz import timezone
import pytz
import emoji
import time
from pytube.__main__ import YouTube
from discord.ui import View, button, Modal, Button
import random
import os, psutil
import io
import math
import chat_exporter
from discord.ext.commands import Context
from typing import List, Optional, Union, Literal
from config.bot_info import *

class NotUsersTrun(Exception):
    def __init__(self):
        super().__init__()

class NotInGame(Exception):
    def __init__(self):
        super().__init__()


class Paper_sissors_stone:
    def __init__(self, starter:discord.Member, players:List[discord.Member], limit = 2):
        self.starter:discord.Member = starter
        self.players:List[discord.Member] = players
        self.limit = limit

class Paper_sissors_stone_view(View):
    def __init__(self, main:Paper_sissors_stone):
        super().__init__(timeout = None)
        self.main = main
        self.nowplayer = 0
        self.ended = False
        self.selection:list = []
    
    def find_selection_emoji(self, selection:str):
        if selection == '1':
            return '✂️'
        elif selection == '2':
            return '🪨'
        elif selection == '3':
            return '📜'

    async def find_winner(self, client:discord.Client):
        select0 = self.selection[0]
        select1 = self.selection[1]
        desc = f'{self.main.players[0]}出了{self.find_selection_emoji(select0)}\n{self.main.players[1]}出了{self.find_selection_emoji(select1)}'
        title = ''
        if select0 == select1:
            title = '平手'
        elif (select0 == '1' and select1 == '3') or (select0 == '3' and select1 == '2') or (select0 == '2' and select1 == '1'):
            title = f'{self.main.players[0]}獲勝！'
        elif (select1 == '1' and select0 == '3') or (select1 == '3' and select0 == '2') or (select1 == '2' and select0 == '1'):
            title = f'{self.main.players[1]}獲勝！'
        embed = await get_embed(client = client, title = title, desc = desc)
        return embed

    async def processing(self,user:Union[discord.User, discord.Member], button:Button, client:discord.Client):
        if user != self.main.players[self.nowplayer] and user in self.main.players:
            raise NotUsersTrun
        elif user not in self.main.players:
            raise NotInGame
        embed = discord.Embed
        if self.nowplayer == 0:
            self.nowplayer += 1
            self.selection.append(button.custom_id)
            embed = await self.to_embed(client = client)
            return embed
        else:
            self.selection.append(button.custom_id)
            embed = await self.find_winner(client = client)
            return embed

        
    async def to_embed(self, client:discord.Client):
        embed = await get_embed(client = client, title = '剪刀石頭布')
        embed.set_author(name = f'現在由{self.main.players[self.nowplayer]}出拳')
        return embed

    @button(label = '剪刀', emoji = '✂️', custom_id='1', style = ButtonStyle.blurple)
    async def sissors_callback(self, interaction:Interaction, button:Button):
        async with interaction.channel.typing():
            try:
                embed = await self.processing(user = interaction.user, button = button, client = interaction.client)
                if not self.ended and self.nowplayer <=1:
                    await interaction.response.send_message(f'你出了{button.emoji}{button.label}！', ephemeral= True)
                else:
                    self.ended = True
                    await interaction.message.edit(view = None)
                return await interaction.message.edit(embed=embed)
            except NotUsersTrun:
                return await interaction.response.send_message('現在不是你的回合！', ephemeral= True)
            except NotInGame:
                return await interaction.response.send_message('你不在遊戲中！', ephemeral= True)

    @button(label = '俗投', emoji = '🪨', custom_id='2',style = ButtonStyle.blurple)
    async def stone_callback(self, interaction:Interaction, button:Button):
        async with interaction.channel.typing():
            try:
                embed = await self.processing(user = interaction.user, button = button, client = interaction.client)
                if not self.ended and self.nowplayer <=1:
                    await interaction.response.send_message(f'你出了{button.emoji}{button.label}！', ephemeral= True)
                else:
                    self.ended = True
                    await interaction.message.edit(view = None)
                return await interaction.message.edit(embed=embed)
            except NotUsersTrun:
                return await interaction.response.send_message('現在不是你的回合！', ephemeral= True)
            except NotInGame:
                return await interaction.response.send_message('你不在遊戲中！', ephemeral= True)

    @button(label = '布', emoji = '📜', style = ButtonStyle.blurple, custom_id='3')
    async def paper_callback(self, interaction:Interaction, button:Button):
        async with interaction.channel.typing():
            try:
                embed = await self.processing(user = interaction.user, button = button, client = interaction.client)
                if not self.ended and self.nowplayer <=1:
                    await interaction.response.send_message(f'你出了{button.emoji}{button.label}！', ephemeral= True)
                else:
                    self.ended = True
                    await interaction.message.edit(view = None)
                return await interaction.message.edit(embed=embed)
            except NotUsersTrun:
                return await interaction.response.send_message('現在不是你的回合！', ephemeral= True)
            except NotInGame:
                return await interaction.response.send_message('你不在遊戲中！', ephemeral= True)
