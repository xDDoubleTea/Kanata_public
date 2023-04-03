from discord import Client, Interaction, Message, app_commands
from discord.ui import button, Button
from discord.ext import commands
from discord.ext.commands import Cog
from config.ChatGPT import MODEL, API_KEY
from typing import Optional, Literal
from view.GPT_instance import GPT_handler, gpt_options
import openai
from config.bot_info import get_embed



openai.api_key = API_KEY

class Chatgpt_cmds(commands.Cog):
    def __init__(self ,client):
        self.client:Client = client 


    @app_commands.command(name = 'gpt_generate_response', description='Using ChatGPT to generate response')
    async def GPT_Generate_response(self, interaction:Interaction, word:str, model:Literal['GPT-3.5', 'GPT-4']='GPT-3.5'):
        await interaction.response.send_message('Loading...')
        if model == 'GPT-3.5':
            model = MODEL
        else:
            model = 'gpt-4'
        msg = await interaction.original_response()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
            {"role": "system", "content": "You are a chatbot"},
            {"role": "user", "content": word},
        ])
        result = ''
        for choice in response.choices:
            result += choice.message.content
        return await msg.edit(content = result)
    
    @app_commands.command(name = 'gpt-start-chat', description='開始對話串')
    async def gpt_start_chat(self, interaction:Interaction,model:Literal['GPT-3.5', 'GPT-4']='GPT-3.5', word:str = None):
        if word == None:
            word = 'Hi'
        if model == "GPT-3.5":
            model = MODEL
        else:
            model = "gpt-4"
            return await interaction.response.send_message('目前開發者還未取得gpt-4的使用權利', ephemeral=True)
        gpt = GPT_handler()
        embed = await get_embed(client = interaction.client, title = 'ChatGPT對話串', desc=f'開啟者：{interaction.user.display_name}')
        embed.set_author(name = interaction.user.display_name, icon_url=interaction.user.display_avatar)
        embed.add_field(name = f'{interaction.user.display_name}：',value = f'```{word}```',inline=False)
        embed.add_field(name = f'ChatGPT：', value = '```輸入中...```',inline=False)
        await interaction.response.send_message(content = f"目前模型：{model}",embed = embed)
        msg = await interaction.original_response()
        message_data = [{"role": "system", "content": "You are a chatbot"},{"role": "user", "content": word}]
        res = await gpt.generate_new_response_text(message_data=message_data, model=model)
        new_embed = await gpt.get_new_embed(client = interaction.client, user_message=word, response_message=res, user = interaction.user)
        view = gpt_options(message_data=message_data, attached_msg=msg, user=interaction.user, embeds = [new_embed.to_dict()])
        new_embed.set_author(icon_url=interaction.user.display_avatar, name = f'第1/1頁')
        return await msg.edit(embed = new_embed, view = view)

        



async def setup(client):
    await client.add_cog(Chatgpt_cmds(client))