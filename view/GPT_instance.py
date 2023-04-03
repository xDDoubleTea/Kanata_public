import discord
from discord import Message, TextChannel, Client, User, Member, Embed, TextStyle, Interaction, ButtonStyle, SelectOption
from typing import List, Union, Dict
from discord.ui import Button, button, Modal, View, TextInput, select
from config.bot_info import get_embed
from config.ChatGPT import MODEL, API_KEY
from datetime import datetime
import openai

openai.api_key = API_KEY

class gpt_options(View):
    def __init__(self, message_data:dict, attached_msg:Message, user:User, embeds:List[Dict], gpt_model = MODEL):
        super().__init__(timeout = None)
        self.message_data = message_data
        self.attached_msg = attached_msg
        self.user:User = user
        self.gpt_generating = False
        self.embeds = embeds
        self.now_embed_idx = 0
        self.gpt_model = gpt_model


    async def on_timeout(self):
        try:
            return await self.attached_msg.edit(view = None)
        except:
            return 
        
    
    async def new_instance(self, interaction:Interaction, keep_old:bool):
        if self.gpt_generating:
            return await interaction.response.send_message('Chat GPT還在輸入訊息！', ephemeral=True)
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message('你不是開啟此對話串的人！', ephemeral=True)
        await interaction.message.delete()
        word = "Hi"
        gpt = GPT_handler()
        embed = await get_embed(client = interaction.client, title = 'ChatGPT對話串', desc=f'開啟者：{interaction.user.display_name}')
        embed.set_author(name = interaction.user.display_name, icon_url=interaction.user.display_avatar)
        embed.add_field(name = f'{interaction.user.display_name}：',value = f'```{word}```',inline=False)
        embed.add_field(name = f'ChatGPT：', value = '```輸入中...```',inline=False)
        await interaction.response.send_message(embed = embed)
        msg = await interaction.original_response()
        message_data = [{"role": "system", "content": "You are a chatbot"},{"role": "user", "content": word}]
        if keep_old:
            message_data = self.message_data
        
        res = await gpt.generate_new_response_text(message_data=message_data, model = self.gpt_model)

        new_embed = await gpt.get_new_embed(client = interaction.client, user_message=word, response_message=res, user = interaction.user)
        view = gpt_options(message_data=[{"role": "system", "content": "You are a chatbot"},{"role": "user", "content": word}], attached_msg=msg, user=interaction.user, embeds =[new_embed.to_dict()])
        return await msg.edit(embed = new_embed, view = view)


    @button(label='輸入訊息...', style = ButtonStyle.green)
    async def input_callback(self, interaction:Interaction, button:Button):
        if self.gpt_generating:
            return await interaction.response.send_message('Chat GPT還在輸入訊息！', ephemeral=True)
        
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message('你不是開啟此對話串的人！', ephemeral=True)
        
        await interaction.response.send_modal(gpt_input(message_data=self.message_data, main = self))
        return 
    
    @button(label = '開啟新對話串(將不會針對舊對話進行解析)', style = ButtonStyle.gray, row = 2)
    async def completely_new_instance(self, interaction:Interaction, button:Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message('你不是開啟此對話串的人！', ephemeral=True)
        return await self.new_instance(interaction = interaction, keep_old=False)

    @button(label = '開啟新對話串(會針對舊對話進行解析)', style=ButtonStyle.gray, row = 2)
    async def old_chat_instance(self, interaction:Interaction, button:Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message('你不是開啟此對話串的人！', ephemeral=True)
        return await self.new_instance(interaction = interaction, keep_old=True)


    @button(label = '關閉', style=ButtonStyle.red)
    async def close(self, interaction:Interaction, button:Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message('你不是開啟此對話串的人！', ephemeral=True)
        return await interaction.message.delete()

    @button(label = '匯出對話檔案' , style=ButtonStyle.blurple)
    async def close_n_save(self, interaction:Interaction, button:Button):
        write_data = '------\n'
        write_data += f'檔案開始生成時間：{datetime.now().strftime("%Y/%m/%d %H:%M:%S")}\n'
        write_data += f'開啟對話串使用者：{interaction.user.display_name}\n\n'
        for embed in self.embeds:
            embed_tool = Embed()
            ebd = embed_tool.from_dict(embed)
            title = ebd.title
            desc = ebd.description
            write_data += f'{title}\n\n{desc}\n\n------\n'
        with open('Chats.txt', 'w', encoding='utf-8') as file:
            file.write(str(write_data))
            file.close()
        
        with open('Chats.txt', 'rb') as file:
            result = discord.File(fp = file, filename = 'Chat_output.txt')
            return await interaction.response.send_message(file = result)



    @button(label = '上一個問題', style = ButtonStyle.blurple, row = 1)
    async def prev(self, interaction:Interaction, button:Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message('你不是開啟此對話串的人！', ephemeral=True)
        if self.now_embed_idx > 0:
            self.now_embed_idx -= 1
        else:
            return await interaction.response.send_message('這已經是第一頁了！', ephemeral=True)
        ebd = Embed()
        new_embed = ebd.from_dict(self.embeds[self.now_embed_idx])
        new_embed.set_author(icon_url=interaction.user.display_avatar, name = f'第{self.now_embed_idx+1}/{len(self.embeds)}頁')
        return await interaction.response.edit_message(embed = new_embed)
    
    @button(label = '下一個問題', style = ButtonStyle.blurple, row =1)
    async def next(self, interaction:Interaction, button:Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message('你不是開啟此對話串的人！', ephemeral=True)
        if self.now_embed_idx < len(self.embeds)-1:
            self.now_embed_idx += 1
        else:
            return await interaction.response.send_message('這已經是最後一頁了！', ephemeral=True)
        ebd = Embed()
        new_embed = ebd.from_dict(self.embeds[self.now_embed_idx])
        new_embed.set_author(icon_url=interaction.user.display_avatar, name = f'第{self.now_embed_idx+1}/{len(self.embeds)}頁')
        return await interaction.response.edit_message(embed = new_embed)
    
    @select(
        placeholder = '選擇回應的模型',
        options = [
            SelectOption(label = 'GPT-3.5', value = 'gpt-3.5-turbo-0301'),
            SelectOption(label = 'GPT-4', value = 'gpt-4')
            ],
        disabled = True
        )
    async def model(self, interaction:Interaction, select:discord.ui.Select):
        self.gpt_model = interaction.data["values"][0]
        return await interaction.response.edit_message(content = f'目前模型：{interaction.data["values"][0]}')

class gpt_input(Modal):
    def __init__(self, message_data, main:gpt_options):
        self.message_data:List[dict] = message_data
        self.main = main
        super().__init__(timeout = None, title = '輸入區')
    
    text = TextInput(label = '輸入文字...', style=TextStyle.long, placeholder='我好棒', max_length=200)

    async def on_submit(self, interaction: Interaction):
        gpt = GPT_handler()
        self.main.gpt_generating = True
        self.message_data.append({"role":"user","content":self.text.value})
        tmp_embed = await gpt.get_new_embed(client = interaction.client, user_message=self.text.value, response_message='輸入中...', user=interaction.user)
        await interaction.response.edit_message(embed = tmp_embed)        
        new_response = await gpt.generate_new_response_text(message_data=self.message_data,model = self.main.gpt_model)
        new_embed = await gpt.get_new_embed(client = interaction.client, user_message=self.text.value, response_message=new_response, user = interaction.user)
        self.main.embeds.append(new_embed.to_dict())
        self.main.gpt_generating = False
        if self.main.now_embed_idx+1 == len(self.main.embeds):
            new_embed.set_author(icon_url=interaction.user.display_avatar, name = f'第{self.main.now_embed_idx+1}/{len(self.main.embeds)}頁')
            self.main.now_embed_idx += 1
        else:
            new_embed.set_author(icon_url=interaction.user.display_avatar, name = f'第{len(self.main.embeds)}/{len(self.main.embeds)}頁')
            self.main.now_embed_idx = len(self.main.embeds)-1
        await interaction.message.edit(embed = new_embed)
        return await interaction.message.edit(view = self.main) 
    
class GPT_handler:
    async def generate_new_response_text(self, message_data:list, model:str):
        response = openai.ChatCompletion.create(model=model,messages=message_data)
        result = ''
        for i in response.choices:
            result += i.message.content
        return result

    async def get_new_embed(self, client:Client, user_message, response_message, user:User):
        new_embed = await get_embed(client = client, title = f'{user.display_name}：\n{user_message}', desc = f'**ChatGPT：**\n{response_message}')
        return new_embed