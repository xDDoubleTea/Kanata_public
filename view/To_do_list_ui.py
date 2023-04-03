from typing import Union
import discord
from discord import Message, Client, Interaction, ButtonStyle, TextStyle, User
from discord.ui import Button, button,Modal, View, TextInput
import json
from view.Page_turning_ui import PageTurningSys
from config.bot_info import get_embed
from config.bot_info import pre

class TodoListNotAvailable(Exception):
    def __init__(self):
        super().__init__()


class append_Modal(Modal):
    def __init__(self):
        super().__init__(title = '新增待辦事項', timeout = 600)
    
    new = TextInput(label = '待辦事項', style = TextStyle.long, max_length = '1000', placeholder = '明天要寫完化學講義P.34~P.50', required = True)
    status = TextInput(label = '狀態(選填，預設值為【未完成】)', style = TextStyle.short, max_length = '50', placeholder = '目前進度到P.43', required = False)

    async def on_submit(self, interaction: Interaction):
        stats = '【未完成】'
        if self.status.value != '':
            stats = self.status.value
        append_to_do(data = self.new.value, stats = stats, dc_user = interaction.user)
        embed = await get_embed(client = interaction.client, title = '✅完成動作', desc = '**加入待辦事項**')
        await interaction.message.edit(embed = embed)
        tmp = await get_page_turning_view(client = interaction.client, user = interaction.user)
        return await interaction.response.send_message(f'已將`{self.new.value}`加入到待辦清單內！目前的待辦清單', ephemeral = True, embed = tmp[1], view = tmp[0])

class edit_Modal(Modal):
    def __init__(self, type:str):
        self.out = ''
        if type == 'stats':
            self.out = '狀態'
        else:
            self.out = '內容'
        super().__init__(title = f'編輯事項{self.out}', timeout = 600)
    
    index = TextInput(label = '事項編號', style = TextStyle.short, max_length = '10', placeholder = '3', required = True)
    col = TextInput(label = f'編輯', style = TextStyle.long, max_length = '500', placeholder = '完成(或修你的錯字)', required = True)

    async def on_submit(self, interaction: Interaction):
        try:
            await edit_stats(user = interaction.user, index = self.index.value, stats = self.col.value)
        except IndexError:
            return await interaction.response.send_message('❌你的待辦清單沒有那麼多項！', ephemeral=True)
        except TypeError:
            return await interaction.response.send_message('❌索引值必須是一個正整數！', ephemeral=True)
        except TodoListNotAvailable:
            return await interaction.response.send_message('❌你還沒有創建一個待辦清單！', ephemeral=True)
        embed = await get_embed(client = interaction.client, title = '✅完成動作', desc = '**編輯待辦事項**')
        await interaction.message.edit(embed = embed)
        tmp = await get_page_turning_view(client = interaction.client, user = interaction.user)
        return await interaction.response.send_message(f'✅已將編號第`{int(self.index.value)}`個事項之{self.out}設為`{self.col.value}`', embed = tmp[1],ephemeral=True, view = tmp[0])

class del_Modal(Modal):
    def __init__(self):
        super().__init__(title = '移除事項', timeout = 600)

    index = TextInput(label = '事項編號', style = TextStyle.short, max_length = '10', placeholder = '3', required = True)

    async def on_submit(self, interaction: Interaction):
        try:
            await del_item(user = interaction.user, index = self.index.value)
        except IndexError:
            return await interaction.response.send_message('❌你的待辦清單沒有那麼多項！', ephemeral=True)
        except TypeError:
            return await interaction.response.send_message('❌索引值必須是一個正整數！', ephemeral=True)
        except TodoListNotAvailable:
            return await interaction.response.send_message('❌你還沒有創建一個待辦清單！', ephemeral=True)
        embed = await get_embed(client = interaction.client, title = '✅完成動作', desc = '**移除待辦事項**')
        await interaction.message.edit(embed = embed)
        tmp = await get_page_turning_view(client = interaction.client, user = interaction.user)
        return await interaction.response.send_message(f'✅已將編號第`{int(self.index.value)}`個事項移除', embed = tmp[1], ephemeral=True, view = tmp[0])

class check_single_item(Modal):
    def __init__(self):
        super().__init__(title = '查看單一事項', timeout=600)
    
    val = TextInput(label = '事項編號', style=TextStyle.short, max_length=10, placeholder = '2')

    async def on_submit(self, interaction: Interaction):
        idx = self.val.value
        try:
            idx = int(idx)
        except:
            return await interaction.response.send_message('❌索引值必須是一個正整數！', ephemeral=True)
        if idx < 0:
            return await interaction.response.send_message('❌索引值必須是一個正整數！', ephemeral=True)
        try:
            tmp = await single_item(user = interaction.user, item_idx=idx)
        except TodoListNotAvailable:
            return await interaction.response.send_message('❌你還沒有創建一個待辦清單！', ephemeral=True)
        except IndexError:
            return await interaction.response.send_message('❌你的待辦清單沒有那麼多項！', ephemeral=True)


        embed = await get_embed(client = interaction.client, title = '神奇待辦事項功能')
        embed.add_field(name = f"事項編號：{idx}\n📑📝{tmp['content']}", value = f"**事項狀態：{tmp['stats']}**", inline = False)
        if tmp['image_url'] != '':
            embed.set_image(url = tmp['image_url'])
        return await interaction.response.send_message(embed = embed, ephemeral=True)

class todolist_edit(View):
    def __init__(self, attached_msg:Message):
        super().__init__(timeout = 600)
        self.attached_msg:Message = attached_msg

    async def on_timeout(self):
        try:
            return await self.attached_msg.edit(view = None)
        except:
            pass
    
    @button(label = '新增待辦事項', emoji = '➕', style = ButtonStyle.blurple, row = 0)
    async def append_callback(self, interaction:Interaction, button:Button):
        return await interaction.response.send_modal(append_Modal())

    @button(label = '查看待辦清單', emoji = '📝', style = ButtonStyle.blurple, row = 1)
    async def output_list_callback(self, interaction:Interaction, button:Button):
        tmp = await get_page_turning_view(client = interaction.client, user = interaction.user)
        return await interaction.response.send_message(embed = tmp[1], ephemeral = True, view = tmp[0])
    
    @button(label = '查看單一待辦事項', emoji = '📝', style = ButtonStyle.blurple, row = 1)
    async def check_single_callback(self, interaction:Interaction, button:Button):
        return await interaction.response.send_modal(check_single_item())
    

    @button(label = '編輯事項狀態', emoji = '⌨️', style = ButtonStyle.green, row =2)
    async def edit_callback(self, interaction:Interaction, button:Button):
        return await interaction.response.send_modal(edit_Modal(type = 'stats'))

    @button(label = '編輯事項內容', emoji = '⌨️', style = ButtonStyle.green, row =2)
    async def edit_content_callback(self, interaction:Interaction, button:Button):
        return await interaction.response.send_modal(edit_Modal(type = 'content'))
    
    @button(label = '移除事項', emoji = '🚮', style = ButtonStyle.danger, row = 3)
    async def del_callback(self, interaction:Interaction, button:Button):
        return await interaction.response.send_modal(del_Modal())


async def output_list(client:Client, user:Union[discord.User, discord.Member]):
    with open('to_do_list.json', 'r') as file:
        data = json.load(file)

    user_todo_data = 0
    for todo in data['todo']:
        if todo['user_id'] == user.id:
            user_todo_data = todo
            break
    if user_todo_data != 0:
        embed = await get_embed(client = client, title = f'{user.display_name}的待辦事項', desc = '====**說明**====\n若要查看個別事項的附圖，請輸入/td後按下「查看單一待辦事項」按鈕')
        #Check length of to-do list, if length == 0 then return '✅沒有待辦事項'
        for x,i in enumerate(user_todo_data['list']):
            if x < min(len(user_todo_data['list']), 10):
                embed.add_field(name = f"事項編號：{x+1}\n📑📝{i['content']}", value = f"**事項狀態：{i['stats']}**", inline = False)
            else:
                break
        return embed
    else:
        return await get_embed(client = client, title = f'❌ | 你還沒新增待辦事項！', desc = f'利用`{pre}add_td [事項]`來新增選項，可直接輸入`{pre}add_td`或`{pre}td`來呼叫ui介面')

def append_to_do(data:str,stats:str, dc_user:Union[discord.User, discord.Member]):
    with open('to_do_list.json', 'r') as file:
        to_do = json.load(file)
        
    has_user = False
    idx = 0
    for i, user in enumerate(to_do['todo']):
        if user['user_id'] == dc_user.id:
            has_user = True
            idx = i
            break
    
    if has_user:
        to_do['todo'][idx]['list'].append({'content':data ,'stats':stats,"image_url":""})
    else:
        to_do['todo'].append({'user_id':dc_user.id ,'list':[{'content':data ,'stats':stats,"image_url":""}]})
    
    with open('to_do_list.json', 'w') as file:
        json.dump(to_do, file, indent = 4)


async def edit_stats(user:Union[discord.User,discord.Member], index, stats:str):
    try:
        index = int(index)
        index -= 1
    except:
        raise TypeError
        
    with open('to_do_list.json', 'r') as file:
        td = json.load(file)
    user_td_data = None
    for i,u in enumerate(td['todo']):
        if u['user_id'] == user.id:
            user_td_data = i
            break
    if user_td_data == None:
        raise TodoListNotAvailable()
    elif len(td['todo'][user_td_data]['list']) >= index+1:
        td['todo'][user_td_data]['list'][index]['stats'] = stats
    else:
        raise IndexError

    with open('to_do_list.json', 'w') as file:
        json.dump(td, file, indent = 4)


async def del_item(user:Union[discord.User,discord.Member], index):
    try:
        index = int(index)
        index -= 1
    except:
        raise TypeError
    
    with open('to_do_list.json', 'r') as file:
        td = json.load(file)
    user_td_data = None
    for i,u in enumerate(td['todo']):
        if u['user_id'] == user.id:
            user_td_data = i
            break
    if user_td_data == None:
        raise TodoListNotAvailable()
    elif len(td['todo'][user_td_data]['list']) >= index+1:
        td['todo'][user_td_data]['list'].pop(index)
    else:
        raise IndexError
    
    with open('to_do_list.json', 'w') as file:
        json.dump(td, file, indent = 4)


async def get_page_turning_view(client:Client, user:User):
    embed = await output_list(client = client, user = user)
    with open('to_do_list.json', 'r') as file:
        raw_data = json.load(file)
    for i in raw_data["todo"]:
        if i["user_id"] == user.id:
            user_data = i
            break
    data = []
    for x,i in enumerate(user_data["list"]):
        data.append(
            {
                "name":f"事項編號：{x+1}\n📑📝{i['content']}", 
                "value":f"**事項狀態：{i['stats']}**"
            }
    )
    v = PageTurningSys(data = data)
    tup = (v,embed)
    return tup

async def single_item(user:User, item_idx:int):
    item_idx -= 1
    with open('to_do_list.json', 'r') as file:
        data = json.load(file)
    user_data = None
    output = 0
    for i,info in enumerate(data['todo']):
        if user.id == info['user_id']:
            user_data = info
            break
    if user_data == None:
        raise TodoListNotAvailable()
    elif len(user_data['list']) >= item_idx+1:
        output = user_data['list'][item_idx]
    else:
        raise IndexError
    
    return output


def attach_image(user:User, item_idx:int, url:str):
    item_idx -= 1
    with open('to_do_list.json', 'r') as file:
        data = json.load(file)
    user_data = None
    user_data_idx = 0
    for i,info in enumerate(data['todo']):
        if user.id == info['user_id']:
            user_data = info
            user_data_idx = i
            break
    if user_data == None:
        raise TodoListNotAvailable()
    elif len(user_data['list']) >= item_idx+1:
        data['todo'][user_data_idx]['list'][item_idx]['image_url'] = url
        with open('to_do_list.json', 'w') as file:
            json.dump(data, file, indent = 4)
    else:
        raise IndexError

def detach_image(user:User, item_idx:int):
    item_idx -= 1
    with open('to_do_list.json', 'r') as file:
        data = json.load(file)
    user_data = None
    user_data_idx = 0
    for i,info in enumerate(data['todo']):
        if user.id == info['user_id']:
            user_data = info
            user_data_idx = i
            break
    if user_data == None:
        raise TodoListNotAvailable()
    elif len(user_data['list']) >= item_idx+1:
        data['todo'][user_data_idx]['list'][item_idx]['image_url'] = ''
        with open('to_do_list.json', 'w') as file:
            json.dump(data, file, indent = 4)
    else:
        raise IndexError