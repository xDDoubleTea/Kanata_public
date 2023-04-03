from typing import List
import discord
from discord import Interaction, app_commands
from discord.ext import commands
from discord.ui import Modal, Button, View, Select, button, select
from view.Word_chain import word_chain, first_words
from config.bot_info import *
import random
from view.Tic_tac_toe import tic_tac_toe_buttons, TicTacToe
from view.Word_chain import word_chain, first_words
from view.Games_ui import GameSelect, joinGame

class BlackJack:
    class gameOptions:
        def __init__(self, author:discord.User, client:discord.Client, players:list):
            self.author = author
            self.client = client
            self.players = players
    
    def __init__(self, cards:list, msg :discord.Message ):
        self.cards = cards
        self.msg = msg

class BlackJack_buttons(View):
    def __init__(self, main:BlackJack):
        super().__init__(timeout = None)
        self.main = main



class games(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'game', description = '遊戲功能：目前只有圈圈叉叉與文字接龍可以玩ouo')
    async def game(self, interaction:Interaction):
        return await interaction.response.send_message(view = GameSelect(client=interaction.client, players=[]))

async def setup(client):
    await client.add_cog(games(client))