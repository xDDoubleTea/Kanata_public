from bs4 import BeautifulSoup
import discord 
import random
from discord import ActivityType, Message, Reaction, ButtonStyle, SelectOption, TextChannel, TextStyle, User, Interaction, app_commands, Member, Guild
from discord.ext import commands
from datetime import datetime, timedelta, date
from pytz import timezone
import yt_dlp
import emoji
import time
from pytube.__main__ import YouTube
import requests
from config.pie_chart import get_result_pie_chart
from discord.ui import View, button, Modal, Button, select, Select
import random
import os, psutil
import io
import math
import chat_exporter
from discord.ext.commands import Context
from typing import List, Optional, Union, Literal
from config.bot_info import *
from view.Page_turning_ui import PageTurningSys

Me = My_user_id

class TooManyPages(Exception):
    def __init__(self):
        super().__init__()

class choice(View):
    def __init__(self, user:User, client:discord.Client):
        super().__init__(timeout = None)
        self.user:User = user
        self.client:discord.Client = client


    @button(label = '確認', emoji = '✔️', style = ButtonStyle.green)
    async def confirm_callback(self, interaction:Interaction, button:Button):
        if interaction.user == self.user:
            return await interaction.response.send_modal(choice_Modal(client = self.client))
        else:
            return await interaction.response.send_message('這不是你能按的', ephemeral=True)
    
    @button(label = '取消', emoji = '❎', style = ButtonStyle.red)
    async def cancel_callback(self, interaction:Interaction, button:Button):
        if interaction.user == self.user:
            embed:discord.Embed = await get_embed(client = self.client, title = '已取消動作!')
            return await interaction.response.edit_message(embed = embed, view = None)

        else:
            return await interaction.response.send_message('這不是你能按的', ephemeral=True)


class ptt_btns(View):
    def __init__(self, client):
        super().__init__(timeout=None)
        top5 = find_top5()
        self.options = []
        for i in top5:
            self.options.append(SelectOption(label = i[1], value = f'{i[0]}&{i[1]}'))
        self.client = client
        new_select = Select(options = self.options, placeholder='請選擇看板')
        new_select.callback = self.other_bbs
        self.add_item(new_select)


    @button(label = '關閉', style = ButtonStyle.danger)
    async def close(self ,interaction:Interaction, button:Button):
        await interaction.response.defer()
        return await interaction.message.delete()
    
    async def other_bbs(self ,interaction:Interaction):
        return await interaction.response.send_modal(pages_Modal(choice = interaction.data['values'][0].split('&')[0], client = self.client, name = interaction.data['values'][0].split('&')[1]))

class pages_Modal(Modal):
    def __init__(self, choice:str, client:commands.Bot, name:str):
        super().__init__(timeout = None, title = '輸入頁數')
        self.choice = choice
        self.name = name
        self.client = client

    pages = discord.ui.TextInput(label = '請輸入頁數', style=TextStyle.long, placeholder='3', default='3', required=True)

    async def handling(self, interaction:Interaction, choice, page):
        await interaction.response.send_message('Loading...')
        await interaction.message.delete()

        if choice == 'joke':
            view, embed = await get_ptt_joke_embed_view(pages = page, client = self.client)
        elif choice == 'gossip':
            view, embed = await get_ptt_gossip_embed_view(pages = page, client = self.client)
        else:
            view, embed = await get_ptt_embed_view(url = choice, pages = page ,client = self.client, name = self.name)

        for item in ptt_btns(client = interaction.client).children:
            view.add_item(item)
        msg = await interaction.original_response()
        return await msg.edit(content = 'Done!',view = view, embed = embed)

    async def on_submit(self, interaction: Interaction):
        try:
            page = int(self.pages.value)
            if page > 100:
                raise TooManyPages
        except TooManyPages:
            return await interaction.response.send_message('太多頁數了！', ephemeral=True)
        except:
            return await interaction.response.send_message('請輸入整數！')
        await self.handling(interaction=interaction, choice = self.choice, page = page)
        
def find_top5():
    top5 = []
    r = requests.get("https://www.ptt.cc/bbs/hotboards.html")
    soup = BeautifulSoup(r.text, "html.parser")
    
    sel = soup.select("div.b-ent a")
    board_name = soup.select("div.board-class")
    board_eng = soup.select("div.board-name")
    
    for i in range(5):
        top5.append((sel[i]["href"], board_name[i].text, board_eng[i].text))
    return top5

async def get_ptt_embed_view(url, client, pages, name):
    url = f'https://www.ptt.cc{url}'
    page = []
    for i in range(pages):
        r= requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        sel = soup.select("div.title a")
        u = soup.select("div.btn-group.btn-group-paging a")
        for s in sel:
            page.append({"name":s.text, "value":f"https://www.ptt.cc/{s['href']}"})
        
        url = f"https://www.ptt.cc/{u[1]['href']}"
    view = PageTurningSys(data = page)
    embed = await get_embed(client = client, title = f'批踢踢實業坊({name})', desc = f'抓取PTT版上頁數：{pages}')
    for idx in range(10):
        embed.add_field(name = page[idx]["name"], value = page[idx]["value"], inline = False)
    return (view, embed)
    

async def get_ptt_joke_embed_view(pages, client):
    url = "https://www.ptt.cc/bbs/joke/index.html"
    page = []
    for i in range(pages):
        r= requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        sel = soup.select("div.title a")
        u = soup.select("div.btn-group.btn-group-paging a")
        for s in sel:
            page.append({"name":s.text, "value":f"https://www.ptt.cc/{s['href']}"})
        
        url = f"https://www.ptt.cc/{u[1]['href']}"
    
    view = PageTurningSys(data = page)
    embed = await get_embed(client = client, title = '批踢踢實業坊(笑話版)', desc = f'抓取PTT版上頁數：{pages}')
    for idx in range(10):
        embed.add_field(name = page[idx]["name"], value = page[idx]["value"], inline = False)

    return (view , embed)

async def get_ptt_gossip_embed_view(pages, client):
    url = "https://www.ptt.cc/bbs/Gossiping/index.html"
    r = requests.Session()
    payload ={"from":"bbs/Gossiping/index.html","yes":"yes"}
    r1 = r.post("https://www.ptt.cc/ask/over18?from=%2Fbbs%2FGossiping%2Findex.html", payload)
    page = []
    for i in range(pages):
        r2 = r.get(url)
        soup = BeautifulSoup(r2.text, "html.parser")
        sel = soup.select("div.title a")
        u = soup.select("div.btn-group.btn-group-paging a")
        #main-container > div.r-list-container.action-bar-margin.bbs-screen > div:nth-child(18) > div.title > a
        for s in sel:
            page.append({"name":s.text, "value":f"https://www.ptt.cc/{s['href']}"})

        url = f"https://www.ptt.cc/{u[1]['href']}"

    view = PageTurningSys(data = page)
    embed = await get_embed(client = client, title = '批踢踢實業坊(八卦版)', desc = f'抓取PTT版上頁數：{pages}')
    for idx in range(10):
        embed.add_field(name = page[idx]["name"], value = page[idx]["value"], inline = False)
    return (view , embed)

class choice_Modal(Modal):
    def __init__(self, client:discord.Client):
        super().__init__(title = '讓我來為你做決定吧!', timeout = None)
        self.client:discord.Client = client

    theme = discord.ui.TextInput(label = '主題', placeholder = '晚餐吃啥(可不填)', style = discord.TextStyle.short, custom_id = 'main',  required=False)
    choices = discord.ui.TextInput(label = '選項', placeholder = '屋馬\n海底撈(以換行區隔)', style = discord.TextStyle.long, custom_id = 'choices')
    
    async def output_embed(self, choices:list ,result:str, theme:str = None):
        for i,j in enumerate(choices):
            if i == len(choices)-1:
                pre = '__'
                pre += j
                pre += '__'
                j = pre
                choices[i] = j
            else:
                pre = '__'
                pre += j
                pre += '__、'
                j = pre
                choices[i] = j
        
        choices:str = "".join(choices)
        embed:discord.Embed = await get_embed(title = result, desc = f'**從{choices}中選出：\n__{result}__**', client = self.client)
        if theme != None:
            embed.set_author(name = theme, icon_url=self.client.user.avatar.url)
        return embed

    
    async def on_submit(self, interaction: Interaction):
        input_choices = self.choices.value.splitlines()
        if len(input_choices) < 2:
            return await interaction.response.send_message('太少選項了!', ephemeral=True)
        else:
            await interaction.response.defer()

            result = random.choice(input_choices)

            embed = await self.output_embed(theme = self.theme.value ,choices = input_choices, result = result)
            await interaction.message.reply(embed = embed)
            return await interaction.message.delete()
        
class others(commands.Cog):
    def __init__(self, client:discord.Client):
        self.client = client

    async def info_embed(self, get_user_info:Union[User,Member], guild:Guild):
        stats_icon = ''
        stats_display ='offline'
        if get_user_info.desktop_status.name == 'online':
            stats_icon = '🟢'
            stats_display = 'online'
        elif get_user_info.desktop_status.name == 'dnd':
            stats_icon = '🔴'
            stats_display = 'dnd'
        elif get_user_info.desktop_status.name == 'idle':
            stats_icon = '🟡'
            stats_display = 'idle'
        else:
            if get_user_info.is_on_mobile():
                stats_icon = '🟩'
                stats_display = 'online on mobile'
            else:
                if get_user_info.web_status.name == 'online':
                    stats_icon = '☁️🟢'
                    stats_display = 'online on web'
                elif get_user_info.web_status.name == 'dnd':
                    stats_icon = '☁️🔴'
                    stats_display = 'dnd on browser'
                elif get_user_info.web_status.name == 'idle':
                    stats_icon = '☁️🟡'
                    stats_display = 'idle on browser'

        
        custom_act = ''
        custom_act_emoji = ''
        has_custom = False
        for act in get_user_info.activities:
            if act.type == ActivityType.custom:
                has_custom = True
                try:
                    custom_act_emoji = act.emoji
                    custom_act += act.name
                except:
                    break
        if not has_custom:
            custom_act = ''
        if custom_act_emoji !=None:
            custom_act_emoji = custom_act_emoji
        else:
            custom_act_emoji = ''
        embed = await get_embed(client = self.client, title = f'{stats_icon}{get_user_info}的資訊', desc = f'目前上線狀態：{stats_display}\n「{custom_act_emoji}{custom_act}」')
        embed.color = get_user_info.colour
        embed.set_thumbnail(url = get_user_info.avatar.url)
        embed.add_field(name = '使用者ID', value = f'{get_user_info.id}', inline = False)
        embed.add_field(name = '加入此伺服器於', value = f'{get_user_info.joined_at.strftime("%Y/%m/%d %H:%M:%S")}', inline = True)
        embed.add_field(name = '加入discord於', value = f'{get_user_info.created_at.strftime("%Y/%m/%d %H:%M:%S")}', inline = True)
        embed.add_field(name = '身分組', value = ''.join(f"{i.mention} " for i in get_user_info.roles), inline = False)
        embed.set_footer(text = f'{embed.footer.text} | Message in {guild.name}', icon_url = embed.footer.icon_url)
        return embed

    async def activities_embed(self, get_user_info:Union[User,Member], guild:Guild):
        output_embed = []
        btns = []
        for act in get_user_info.activities:
            embed = discord.Embed
            if act.type == ActivityType.playing:
                embed = await get_embed(title = f'正在玩', client = self.client, desc = f'**{act.name}**')
                try:
                    if len(act.buttons) > 0:
                        for i in act.buttons:
                            btns.append(Button(style = ButtonStyle.gray, label = i, disabled = True))
                    embed.description = f'**{act.name}**({act.large_image_text})\n{act.details}\n{act.state}\n{act.small_image_text}'
                    embed.set_image(url = act.large_image_url)
                    embed.set_thumbnail(url = act.small_image_url)
                except:
                    pass
                output_embed.append(embed)
            elif act.type == ActivityType.listening:
                try:
                    if len(act.buttons) > 0:
                        for i in act.buttons:
                            btns.append(Button(style = ButtonStyle.gray, label = i, disabled = True))
                except:
                    pass
                embed = await get_embed(title = f'正在聽{act.name}', client = self.client)
                embed.url = act.track_url
                embed.color = act.color
                embed.set_author(name = f'{"".join(act.artists)}')
                embed.add_field(name = 'Album', value = f'{act.album}')
                embed.add_field(name = f'Song:{act.title}', value = act.track_url)
                embed.add_field(name = 'Duration', value = act.duration, inline = False)
                embed.set_thumbnail(url = act.album_cover_url)
                output_embed.append(embed)
            elif act.type == ActivityType.streaming:
                embed = await get_embed(title = f'正在直播', client = self.client, desc = f'**{act.name}**')
                output_embed.append(embed)
            elif act.type == ActivityType.watching:
                embed = await get_embed(title = f'正在看', client = self.client, desc = f'**{act.name}**')
                output_embed.append(embed)
            elif act.type == ActivityType.competing:
                embed = await get_embed(title = f'正在競爭', client = self.client, desc = f'**{act.name}**')
                output_embed.append(embed)

        return (output_embed,btns)

    @app_commands.command(name = 'choice', description='選擇困難？沒問題！機器人幫你隨機做選擇！')
    @app_commands.describe(choices = '選項以空格隔開')
    async def choice(self, interaction:Interaction, choices:Optional[str]):
        try:
            temp = choices.split()
        except:
            temp = []
        choice_view = choice(user = interaction.user, client = interaction.client)
        if len(temp) <= 1:
            embed = await get_embed(title = '太少選項了!', desc = '新增選項?', client = interaction.client)
            return await interaction.response.send_message(embed = embed, view = choice_view)
        elif len(temp) < 30 and len(choices) < 1000:
            tmp = choice_Modal(client = self.client)
            embed = await tmp.output_embed(choices = temp, result=random.choice(choices.split()))
            return await interaction.response.send_message(embed = embed)
        else:
            return await interaction.response.send_message('太多選項了！')

    @app_commands.command(name = 'change_presence', description='更換顯示的狀態')
    async def change_presence(self, interaction:Interaction, word:str, online_stats:Optional[Literal['Online','Idle','Do not Disturb', 'Offline']]):
        status = discord.Status
        if interaction.user.id != My_user_id:
            return await interaction.response.send_message('你不能更換我的狀態！',ephemeral=True)
        if online_stats != None:
            if online_stats == 'Online':
                status = discord.Status.online
            elif online_stats == 'Idle':
                status = discord.Status.idle
            elif online_stats == 'Do not Disturb':
                status = discord.Status.dnd
            elif online_stats == 'Offline':
                status = discord.Status.invisible
            await interaction.client.change_presence(activity=discord.Game(name = word), status=status)
            return await interaction.response.send_message(f'狀態列已變更為{word},上線狀態變更為{status.name}',ephemeral=True)
        else:
            await interaction.client.change_presence(activity=discord.Game(name = word))
            return await interaction.response.send_message(f'狀態列已變更為{word}',ephemeral=True)
        
    @app_commands.command(name = 'permissions')
    async def check_permission(self, interaction:Interaction):
        member:Member = await interaction.guild.fetch_member(interaction.client.user.id)
        perms = member.guild_permissions
        return await interaction.response.send_message(perms.administrator)

    @app_commands.command(name = 'ptt')
    async def get_PTT_data(self, interaction:Interaction, pages:str, bbs:Literal['八卦版','笑話版']):
        #joke_url "https://www.ptt.cc/bbs/joke/index.html"
        try:
            pages = int(pages)
            if pages > 100:
                raise TooManyPages
        except TooManyPages:
            return await interaction.response.send_message('太多頁數了！', ephemeral=True)
        except:
            return await interaction.response.send_message('頁數只能是整數！', ephemeral=True)
        

        if bbs == '笑話版':
            await interaction.response.send_message('Loading...')
            view,embed = await get_ptt_joke_embed_view(pages = pages, client=interaction.client)
            msg:discord.InteractionMessage = await interaction.original_response()
            for item in ptt_btns(client = interaction.client).children:
                view.add_item(item)
            await msg.edit(view = view, embed = embed, content = 'Done!')
        elif bbs == '八卦版':
            await interaction.response.send_message('Loading...')
            view,embed = await get_ptt_gossip_embed_view(pages = pages, client=interaction.client)
            msg:discord.InteractionMessage = await interaction.original_response()
            for item in ptt_btns(client = interaction.client).children:
                view.add_item(item)
            await msg.edit(view = view, embed = embed, content = 'Done!')
            

    @app_commands.command(name = 'spam_emoji', description = '神奇炸表符功能')
    @app_commands.describe(message_id = '你要送表符的訊息ID', channel = '[選填]訊息所在的頻道，未填則於觸發此指令之頻道尋找訊息')
    async def spam_emoji(self, interaction:Interaction, message_id:str, channel:TextChannel=None):
        message_id = int(message_id)
        got_msg = False
        msg = Message
        if channel != None:
            pass
        else:
            channel = interaction.channel
        try:
            msg = await channel.fetch_message(message_id)
            got_msg = True
            await interaction.response.send_message(content = msg.jump_url, ephemeral = True)
        except:
            return await interaction.response.send_message(ephemeral=True, content = f'找不到訊息！請嘗試提供頻道ID')

        if got_msg:
            spam = []
            try:
                for i in range(20):
                    rand_emoji = random.choice(channel.guild.emojis)
                    if spam.count(rand_emoji) == 0:
                        spam.append(rand_emoji)
                for emoji in spam:
                    await msg.add_reaction(emoji)
            except:
                pass
            return 
    
    @commands.command(name = 'help', aliases = ['hp', 'h'])
    async def help(self, ctx:Context):
        embed = await help_msg_embed(client = self.client)
        return await ctx.send(embed = embed)
    
    @commands.command(name='save_channel', aliases =['save_cnl'])
    async def save_channel(self, ctx:Context, channel_id = -1, limit:int = None):
        async with ctx.channel.typing():
            channel = discord.TextChannel
            if channel_id != -1:
                channel = self.client.get_channel(channel_id)
            else:
                channel = ctx.message.channel
            msg = await ctx.send('Processing...')
            transcript = await chat_exporter.export(channel, limit = limit, tz_info="Asia/Taipei")
            transcript_file = discord.File(
                io.BytesIO(transcript.encode()),
                filename=f"{channel.name}.html"
            )
            new_msg = await msg.reply('Done!')
            new_msg = await new_msg.edit(attachments=[transcript_file])
            link = await chat_exporter.link(new_msg)
            return await new_msg.edit(content = f'{new_msg.content}\nLink to the online version of this transcript:{link}')

    @app_commands.command(name = 'ram',description = '機器人記憶體用量')
    @app_commands.describe(unit = '回傳單位(KB,MB,GB)，預設為MB')
    async def Ram(self, interaction:Interaction, unit:Literal['KB', 'MB', 'GB']):
        process = psutil.Process(os.getpid())
        if unit == '':
            embed = discord.Embed(
                title = 'RAM usage',
                description = f'The RAM usage is:`{round((process.memory_info().rss)/(1024*1024), 5)}`MB',
                color=discord.Colour.blue()
            )
            return await interaction.response.send_message(embed=embed)
        unit_str = unit
        if unit == 'KB':
            unit = 1024
        elif unit == 'MB':
            unit = 1024*1024
        elif unit == 'GB': 
            unit = 1024*1024*1024
        else:
            return await interaction.response.send_message('不支援此單位！',ephemeral = True)
        embed = discord.Embed(
                title = 'RAM usage',
                description = f'The RAM usage is:`{round((process.memory_info().rss)/unit, 5)}`{unit_str}',
                color=discord.Colour.blue()
            )
        return await interaction.response.send_message(embed=embed)

    @commands.command(name = 'get_pt_id')
    async def get_pt_id(self, ctx:Context):
        thread_info = []
        for thread in ctx.guild.threads:
            if discord.Thread.is_private(thread):
                me = self.client.get_user(Me)
                try:
                    await thread.fetch_member(Me)
                    pass
                except:
                    thread_info.append({"name":thread.name, "id":thread.id})
        return print(thread_info)
                    

    
    @app_commands.command(name='cpu', description = '測試cpu使用率(預設測試時間為2秒)')
    @app_commands.describe(duration = '測試時間(預設為2秒)')
    async def CPU(self, interaction:Interaction, duration:str = '2'):
        embed = await get_embed(client = interaction.client, title = 'CPU usage', desc = '💤 | testing...')
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        try:
           duration = int(duration)
        except:
            return await msg.edit('請輸入正數！')
        if duration <= 0:
            return await msg.edit('請輸入正數！')

        test_cpu = psutil.cpu_percent(duration)
        if test_cpu > 70:
            desc = f'❗ | The CPU usage is:`{test_cpu}`% \n Test duration {duration}(sec)'
        else:
            desc = f'✅ | The CPU usage is:`{test_cpu}`% \n Test duration {duration}(sec)'
        embed = await get_embed(client = interaction.client, title = 'CPU usage',desc = desc)
        await msg.edit(embed=embed)

    @commands.command(name = 'del_cnl')
    async def del_cnl(self, ctx:Context, cnl_id):
        cnl = self.client.get_channel(int(cnl_id))
        if cnl != None:
            return await cnl.delete()
        else:
            return
        

    @commands.command(name='pick')
    async def pick(self, ctx:Context, *, dicestuff):
        percentage = abs((random.randint(0,100))*100-(random.randint(3,241)))%100
        yes = False
        reply='abc'
        zeroorone = (random.randint(0,1481))%2

        if zeroorone == 1:
            reply = f'我覺得好像`{percentage}%`是'
        elif zeroorone == 0:
            reply = f'我覺得好像`{percentage}%`不是'

        embed = discord.Embed(
            title = dicestuff,
            description=reply,
            color = discord.Colour.blue()
        )
        embed.set_footer(text = '免責聲明\n此結果皆為亂數生成，若有人當真並依此攻擊，本機器人作者一概不負責任。', icon_url = self.client.user.avatar.url)
        embed.set_author(name = f"{ctx.message.author}", icon_url = ctx.message.author.avatar.url)
        msg = await ctx.message.reply(embed=embed)
        await msg.add_reaction('❓')

    @commands.command(aliases = ["thu","thumb"])
    async def get_yt_thumbnail(self, ctx:Context, url):
        #await ctx.message.edit(embed=None)
        with yt_dlp.YoutubeDL() as yt:
            info = yt.extract_info(url = url, download = False)
            return await ctx.send(f"{info['thumbnail']}")


    async def tets_to_file(self, file:discord.Attachment):
        return await file.to_file()
    

    @commands.command(help = "dont use it", aliases = ['s'])
    @commands.dm_only()
    async def say(self, ctx:Context, channel_id, *, sentence = '\n'):
        global Me
        cmd = ctx.message
        author = cmd.author
        channel = self.client.get_channel(int(channel_id))
        if channel == None:
            channel = self.client.get_user(int(channel_id))
        if author.id == Me:
            if len(ctx.message.attachments) > 0:
                msg = await channel.send(sentence)
                files = []
                for x in ctx.message.attachments:
                    files.append(await x.to_file())

                await msg.edit(attachments = files)
                await author.send('sent!')
            else:
                msg = await channel.send(sentence)
                await author.send('sent!')
        else:
            return


    @commands.command(name = 'get_id')
    async def get_id(self, ctx:Context, *,args):
        args = args.split('<')[1]
        args = args.split('>')[0]
        await ctx.message.channel.send(args[1:])
        

    @commands.command(name = 'get_avatar', aliases = ['get_photo'])
    async def get_avatar(self, ctx:Context, *, args = None):
        if args != None:
            args = args.split('<')[1]
            args = args.split('>')[0]
            user = self.client.get_user(int(args[1:]))
            if user != None:
                return await ctx.send(user.avatar)
        else:
            return await ctx.send(ctx.author.avatar)
    
    @app_commands.command(name = 'pie_chart', description = '神奇圓餅圖')
    async def pie_chart(self, interaction:Interaction, options:str, ratio:str, title:str='', explode:str='',startangle:str = '90'):
        options = options.split(',')
        ratio = ratio.split(',')
        for i in range(len(ratio)):
            try:
                ratio[i] = int(ratio[i])
            except:
                return await interaction.response.send_message('比例只能為數字！')

        explode = explode.split(',')
        if len(options) != len(ratio):
            return await interaction.response.send_message('輸入的比例數量和選項數量不同！')
        out_title = 'Pie Chart'
        out_explode = [0 for i in range(len(options))]
        if title != '':
            out_title = title
        if explode != '':
            out_explode = explode

        return await interaction.response.send_message(file = get_result_pie_chart(options = options, ratio = ratio, title = out_title, explode=out_explode))

    @app_commands.command(name = 'get_info', description = '回傳使用者資訊')
    @app_commands.describe(member = '[選填]tag使用者', user_id = '[選填]輸入使用者id')
    async def get_info(self, interaction:Interaction, member:Optional[discord.Member], user_id:Optional[str]):
        get_user_info = None
        if member!=None and user_id != None:
            return await interaction.response.send_message('一次只能選擇member或user_id其中一個選項', ephemeral=True)
        elif member != None and user_id == None:
            get_user_info = interaction.guild.get_member(member.id)
        elif member == None and user_id != None:
            get_user_info = interaction.client.get_user(int(user_id))
        else:
            get_user_info = interaction.guild.get_member(interaction.user.id)
        embedlist = []
        v = View(timeout = 1000)
        try:
            info_embed = await self.info_embed(get_user_info = get_user_info, guild = interaction.guild)
            embedlist.append(info_embed)
            activities_embed = await self.activities_embed(get_user_info = get_user_info, guild = interaction.guild)
            for embed in activities_embed[0]:
                embedlist.append(embed)

            
            if len(activities_embed[1]) > 0:
                for i in activities_embed[1]:
                    v.add_item(i)
        except:
            user_embed = await get_embed(client = self.client, title = f'{get_user_info}的資訊')
            user_embed.color = get_user_info.colour
            user_embed.add_field(name = '使用者ID', value = f'{get_user_info.id}', inline = False)
            user_embed.add_field(name = '加入discord於', value = f'{get_user_info.created_at.strftime("%Y/%m/%d %H:%M:%S")}', inline = True)
            embedlist.append(user_embed)
            
        return await interaction.response.send_message(embeds = embedlist, view = v)

            

    @say.error
    async def say_error(self, ctx:Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title = "Error!",
                description = "This is an error message",
                colour = discord.Colour.blue()
            )
            t = time.localtime()
            today = date.today()
            today_date = today.strftime("%Y/%m/%d")
            current_time = time.strftime("%H:%M:%S", t)
            
            embed.set_author(name = f"{self.client.user}", icon_url = self.client.user.avatar.url)
            embed.set_footer(text = f"{default_footer} \n Sent at {today_date} , {current_time}", icon_url = self.client.user.avatar.url)
            message = await ctx.send(embed = embed)
            await message.add_reaction(emoji.emojize(":cross_mark:"))



async def setup(client):
    await client.add_cog(others(client))
        