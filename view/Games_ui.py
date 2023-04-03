from typing import List
from discord.ui import Modal, Button, View, Select, button, select
from view.Word_chain import word_chain, first_words
from config.bot_info import *
import random
from discord import Interaction, Message, User
from view.Tic_tac_toe import tic_tac_toe_buttons, TicTacToe
from view.Paper_sissors_stone import Paper_sissors_stone, Paper_sissors_stone_view


class GameSelect(View):
    def __init__(self, client, players:list):
        super().__init__(timeout = None)
        self.players:List[discord.User] = players
        self.client:discord.Client = client

    @select(
        placeholder ='選擇遊戲', 
        options = [
            discord.SelectOption(label = 'Tic Tac Toe', description = '圈圈叉叉', emoji = '⭕',value = '⭕Tic Tac Toe'),
            discord.SelectOption(label = 'Black Jack', description = '21點', emoji = '♦️',value = '♦️Black Jack'),
            discord.SelectOption(label = 'Word Chain', description = '文字接龍', emoji = '🔁', value = '🔁Word Chain'),
            discord.SelectOption(label = 'Paper sissors stone', description = '剪刀石頭布', emoji = '✊', value = '✊Paper sissors stone')
        ],
        custom_id='game_selection',
        min_values=1,
        max_values=1
    )
    async def game_callback(self, interaction:Interaction, select:Select):
        if select.custom_id == 'game_selection':
            await interaction.response.defer()
            select.disabled = True
            await interaction.message.edit(view = self)
            desc = f'玩家列表:\n還沒有玩家加入!'
            for i in self.players:
                desc += i

            embed = await get_embed(client = interaction.client, title = f'遊戲{select.values[0]}', desc = desc)
            embed.color = discord.Colour.dark_red()
            msg = await interaction.channel.send(embed = embed)
            joinGame_view = joinGame(selection = self, game = select.values[0], msg = msg, starter = interaction.user)
            await msg.edit(view = joinGame_view)
    
class joinGame(View):
    def __init__(self, selection:GameSelect, game:str, msg:Message, starter:User):
        super().__init__(timeout = None)
        self.selection = selection
        self.game = game
        self.msg = msg
        self.starter = starter

    async def to_embed(self, msg:Message):
        embed_raw = msg.embeds[0].to_dict()
        embed_raw['description'] = '玩家列表:'
        for player in self.selection.players:
            embed_raw['description'] += f'\n{player.display_name}'
        if len(self.selection.players) == 0:
            embed_raw['description'] += '\n還沒有玩家加入!'
            embed_raw['color'] = discord.Colour.dark_red().value
        else:
            embed_raw['color'] = discord.Colour.blue().value
        return discord.Embed.from_dict(embed_raw)

    async def start_game(self, interaction:discord.Interaction):
        msg:discord.Message = interaction.message
        embed = discord.Embed
        if self.game == '⭕Tic Tac Toe':
            if len(self.selection.players) == 2:
                await msg.delete()
                embed = msg.embeds[0]
                embed.title = f'⭕ | 現在是{self.selection.players[0].display_name}的回合'
                view = tic_tac_toe_buttons(
                        main = TicTacToe(
                            message=msg, 
                            client = self.selection.client, 
                            players = self.selection.players
                        )
                )
                for i in range(9):
                    btn = Button(label = None, emoji = '⏹️', style = discord.ButtonStyle.gray, disabled = False, custom_id = f'{floor(i/3)}, {i%3}', row = {floor(i/3)})
                    btn.callback = view.all_callback
                    view.add_item(btn)
                return await msg.channel.send(embed = embed, view = view)
            elif len(self.selection.players) > 2:
                return await interaction.response.send_message('太多人了!', ephemeral= True)
            elif len(self.selection.players) < 2:
                return await interaction.response.send_message('太少人了!', ephemeral= True)
        elif self.game == '♦️Black Jack':
            return await interaction.response.send_message('此遊戲還在開發中!請耐心等候!', ephemeral= True)
        elif self.game == '🔁Word Chain':
            embed = discord.Embed(
                title = f'文字接龍Word Chain(由{self.selection.players[0].display_name}開始)',
                description = '有沒有合規定自由心證啦ouo',
                colour = discord.Colour.blue()
            )
            dev:discord.User = interaction.client.get_user(My_user_id)
            word = random.choice(first_words)
            embed.add_field(name = '電腦ouo', value = word)
            embed.set_author(name = f"{interaction.client.user}", icon_url=interaction.client.user.avatar.url)
            embed.set_footer(text = f"第1/1頁", icon_url=dev.avatar.url)
            await interaction.response.edit_message(view = None)
            msg = await interaction.message.channel.send(embed = embed)
            return await msg.edit(view = word_chain(message = msg, words = [(interaction.client.user, word)], players = self.selection.players))
        elif self.game == '✊Paper sissors stone':
            if len(self.selection.players) > 2:
                return await interaction.response.send_message('太多人了！', ephemeral= True)
            elif len(self.selection.players) <2:
                return await interaction.response.send_message('太少人了！', ephemeral= True)
            embed = await get_embed(client=interaction.client, title = '剪刀石頭布')
            embed.set_author(name = f'現在由{self.starter}出拳')
            new_game = Paper_sissors_stone(starter = self.starter, players = self.selection.players)
            view = Paper_sissors_stone_view(main = new_game)
            await interaction.response.edit_message(embed = embed, view = view)


    async def has_user(self, interaction:Interaction):
        has_user = False
        for i in self.selection.players:
            if i == interaction.user:
                has_user = True
                break
        return has_user


    @button(label = '✔️加入遊戲', style = discord.ButtonStyle.green, disabled = False)
    async def join_callback(self, interaction:Interaction, button:Button):
        if not await self.has_user(interaction = interaction):
            self.selection.players.append(interaction.user)
            return await interaction.response.edit_message(embed = await self.to_embed(msg = interaction.message), view = self)
        else:
            return await interaction.response.send_message(content = '你已經在遊戲中!', ephemeral= True)


    @button(label = '🔄️退出遊戲', style = discord.ButtonStyle.red, disabled = False)
    async def leave_callback(self, interaction:Interaction, button:Button):
        if await self.has_user(interaction = interaction):
            self.selection.players.remove(interaction.user)
            return await interaction.response.edit_message(embed = await self.to_embed(msg = interaction.message), view = self)
        else:
            return await interaction.response.send_message(content = '你不在遊戲中!', ephemeral= True)


    @button(label = '✅開始遊戲', style = discord.ButtonStyle.green, disabled = False, row = 1)
    async def start_callback(self, interaction:Interaction, button:Button):
        if await self.has_user(interaction = interaction):
            return await self.start_game(interaction = interaction)
        else:
            return await interaction.response.send_message('你不在遊戲內!', ephemeral= True)


    @button(label = '⛔結束遊戲', style = discord.ButtonStyle.red, disabled = False, row = 1)
    async def end_callback(self, interaction:Interaction, button:Button):
        if await self.has_user(interaction = interaction) or interaction.user == self.starter:
            await interaction.message.edit(view = None)
            return await interaction.response.send_message(f'{interaction.user}強制結束了遊戲!')
        else:
            return await interaction.response.send_message(f'你不在遊戲中!', ephemeral= True)