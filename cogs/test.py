import discord
from discord.ext import commands
from discord import Embed, Interaction, app_commands, Message, Attachment
from discord.ext.commands import Context 
from discord.ui import Button , View, Modal
from config.pie_chart import get_result_pie_chart
from config.bot_info import MY_GUILD, get_embed
import yt_dlp

class test(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'ping', description='pings the bot')
    async def ping(self, interaction:Interaction):
        return await interaction.response.send_message(f'✅延遲：{round(interaction.client.latency*1000)}ms')
    
    @app_commands.command(name = 'request', description='身分組申請指令(請先看申請規定)')
    @app_commands.describe(image = '附加圖片(至少一張)', role = '選擇要申請的身分組，可打關鍵字搜尋身分組')
    async def request_cmd(self, interaction:Interaction, role:discord.Role, image:Attachment, image2:Attachment = None, image3:Attachment = None,image4:Attachment=None,image5:Attachment=None,image6:Attachment=None):
        return await interaction.response.send_message('uwu')
            
    @commands.command(name = 'pie_test')
    async def pie_test(self, ctx:Context):
        file = get_result_pie_chart(options = ['中文', 'owo', 'oao'], ratio = [15,60,25], title = 'hi', explode=(0,0,0.2))
        embed = await get_embed(client = self.client, title = 'uwu', desc = 'yay')
        embed.set_image(url = "attachment://uwu.png")
        return await ctx.send(content = 'uwu',embed = embed, file = file)

    @commands.command(name = 'embed_test')
    async def embed_test(self, ctx:Context):
        with yt_dlp.YoutubeDL() as ytdl:
            vid_info = ytdl.extract_info("https://youtu.be/d4IGg5dqeO8", download = False)
            desc = vid_info["description"]
            embed = await get_embed(client = self.client, title = 'test', desc=desc)
        return await ctx.send(embed = embed)


async def setup(client):
    await client.add_cog(test(client), guilds = [MY_GUILD])