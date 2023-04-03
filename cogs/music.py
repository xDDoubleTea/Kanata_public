import discord
from typing import List, Tuple, Dict
from discord.ext import commands
from discord import Embed, FFmpegPCMAudio, Member, VoiceChannel, VoiceState, User, app_commands, Interaction
from discord.utils import get
from discord.ui import Button, View
from discord.ext.commands import Context
import mysql.connector
from config.Mysql_info import *
from typing import Optional
import asyncio

async def play_source(client:discord.Client,voice_client:discord.VoiceClient):
    source = FFmpegPCMAudio("C:\\Users\\a5457\\桌面\\Programming\\Bots\\DiscordBots\\Kanata\\songs\\01 This game.opus")
    voice_client.play(source)

class MusicPlayer:
    def __init__(self):
        pass


class music(commands.Cog):
    def __init__(self, client):
        self.client:commands.Bot = client
        self.custom_channel:list = []
        self.new_channel:List[Tuple[int ,User, int]] = []
        sql_db = MySqlDataBase()
        sql = 'SELECT * FROM custom_channel'
        self.custom_channel = sql_db.get_db_data(sql_cmd=sql)
        sql = 'SELECT * FROM new_channel'
        raw_data = sql_db.get_db_data(sql_cmd=sql)
        for new_cnls in raw_data:
            self.new_channel.append((int(new_cnls[0]), self.client.get_user(int(new_cnls[1])),int(new_cnls[2])))
        self.vcs:List[Dict[discord.VoiceClient, discord.Guild]] = []

    def is_dynamic(self, channel:VoiceChannel):
        for cnl in self.custom_channel:
            if cnl[1] == str(channel.id):
                return True
        return False

    def is_new(self, channel:VoiceChannel):
        for cnl in self.new_channel:
            if cnl[0] == channel.id:
                return True
        return False


    @commands.Cog.listener()
    async def on_voice_state_update(self, member:Member, before:VoiceState, after:VoiceState):
        if member.bot:
            return 
        if before.channel == None:
            if after.channel == None:
                #no way that this happenes
                return
            else:
                #user joined a channel
                #see if it's a dynamic channel
                if self.is_dynamic(channel = after.channel):
                    #it's a dynamic channel
                    #create new voice channel and move member into it
                    new_vc:VoiceChannel = await after.channel.clone(name = f"{member.name}'s small room")
                    await new_vc.edit(user_limit = None)
                    perms = new_vc.overwrites_for(member)
                    perms.manage_channels = True
                    await new_vc.set_permissions(member, overwrite = perms)
                    sql_db = MySqlDataBase()
                    sql = 'INSERT INTO new_channel (new_channel_id, owner_id, timeout) VALUES (%s, %s, %s)'
                    val = (str(new_vc.id), member.id, 0)
                    sql_db.insert_data(sql_cmd=sql, values=val)
                    self.new_channel.append((new_vc.id, member, 0))
                    return await member.move_to(new_vc)
        else:
            #user is from another channel
            if after.channel == None:
                #user is not in any voice channel
                #see if before channel was one of the new channels
                if self.is_new(before.channel):
                    #if all members was disconnected from before channel then delete
                    if len(before.channel.members) >0:
                        return
                    else:
                        #delete the new channel
                        await before.channel.delete()
                        sql_db = MySqlDataBase()
                        sql = 'DELETE FROM new_channel WHERE new_channel_id = %s'
                        val = (str(before.channel.id),)
                        sql_db.del_data(sql_cmd=sql, values=val)
                        for idx, cnl in enumerate(self.new_channel):
                            if before.channel.id == cnl[0]:
                                self.new_channel.pop(idx)
                                break
                        return
            else:
                #user connects to another channel
                #check if after is dynamic               
                if self.is_dynamic(channel = after.channel):
                    #it's dynamic
                    #see if before channel is new channel, if yes then delete and create another one
                    if self.is_new(channel = before.channel):
                        #move back to before channel
                        await member.move_to(before.channel)
                    else:
                        #not new but its dynamic so create a new voice
                        #create new voice channel and move member into it
                        new_vc:VoiceChannel = await after.channel.clone(name = f"{member.name}'s small room")
                        await new_vc.edit(user_limit = None)
                        sql_db = MySqlDataBase()
                        sql = 'INSERT INTO new_channel (new_channel_id, owner_id, timeout) VALUES (%s, %s, %s)'
                        val = (str(new_vc.id), member.id, 0)
                        sql_db.insert_data(sql_cmd=sql, values=val)
                        self.new_channel.append((new_vc.id, member, 0))
                        return await member.move_to(new_vc)
                else:
                    #not dynamic
                    #see if before channel is new channel, if yes then delete
                    if self.is_new(channel = before.channel):
                        #see if all members was disconnected
                        if len(before.channel.members)>0:
                            return
                        else:
                            #delete the new channel
                            await before.channel.delete()
                            sql_db = MySqlDataBase()
                            sql = 'DELETE FROM new_channel WHERE new_channel_id = %s'
                            val = (str(before.channel.id),)
                            sql_db.del_data(sql_cmd=sql, values=val)
                            for idx, cnl in enumerate(self.new_channel):
                                if before.channel.id == cnl[0]:
                                    self.new_channel.pop(idx)
                                    break
                            return
                    else:
                        #not new not dynamic
                        return


    @app_commands.command(name='connect', description='Connects to voice channel')
    async def join(self, interaction:Interaction, channel:Optional[discord.VoiceChannel]):
        if channel == None and interaction.user.voice == None:
            return await interaction.response.send_message('請加入某語音頻道或指定語音頻道讓機器人加入。',ephemeral=True)
        
        vc = 0
        if channel == None:
            await interaction.response.send_message(f'已連接語音！\n頻道：{interaction.user.voice.channel.mention}\n發送訊息使用者：{interaction.user.display_name}', ephemeral=True)
            vc = await interaction.user.voice.channel.connect(timeout = 3600, reconnect=True, self_deaf=True)
            return self.vcs.append({"voice_client":vc, "guild":interaction.guild})
        else:
            await interaction.response.send_message(f'已連接語音！\n頻道：{channel.mention}\n發送訊息使用者：{interaction.user.display_name}', ephemeral=True)
            vc = await channel.connect(timeout = 3600, reconnect=True, self_deaf=True)
            return self.vcs.append({"voice_client":vc, "guild":interaction.guild})
            
    
    @app_commands.command(name = 'disconnect', description='Disconnects from a voice channel')
    async def dis(self, interaction:Interaction):
        done = False
        for vc in self.vcs:
            if vc["guild"] == interaction.guild:
                await vc["voice_client"].disconnect()
                done = True
        if not done:
            return await interaction.response.send_message('未連接至語音頻道！',ephemeral=True)
        else:
            return await interaction.response.send_message('已斷開連接！',ephemeral=True)


    @commands.command(name = 'play')
    async def tmp(self, ctx:Context):
        if ctx.guild.voice_client != None:
            await ctx.guild.voice_client.disconnect()
        vc = await ctx.author.voice.channel.connect(reconnect=True, self_deaf=True, timeout=600)
        await self.client.loop.create_task(play_source(client = self.client, voice_client=vc))


    @commands.command(name='set_channel',aliases=['set_ch'])
    async def set_channel(self, ctx, vc_id):
        Kanatadb = mysql.connector.connect(
        host='localhost',
        database='kanata',
        password='ImSingleDog1',
        user='root'
        )
        cursor = Kanatadb.cursor()
        sql = 'SELECT * FROM custom_channel'
        cursor.execute(sql)
        channel_data = cursor.fetchall()

        index = 0
        has_guild = False
        if len(channel_data)>0:
            for i,x in enumerate(channel_data):
                if x[0] == str(ctx.guild.id):
                    has_guild = True
                    index = i
                    break

        v_channel = self.client.get_channel(int(vc_id))
        if has_guild:
            if str(vc_id) == channel_data[index][1]:
                await ctx.message.channel.send(f'`{v_channel.name}`已加入動態語音頻道中!你想要更改嗎?')
            elif str(vc_id) != channel_data[index][1]:
                cursor = Kanatadb.cursor()
                sql = "DELETE FROM custom_channel WHERE guild_id = %s"
                val = (str(ctx.guild.id), )
                cursor.execute(sql, val)
                Kanatadb.commit()
                sql = 'INSERT INTO custom_channel (guild_id, guild_channel_id) VALUES (%s, %s)'
                val = (str(ctx.guild.id), vc_id)
                cursor.execute(sql, val)
                Kanatadb.commit()
                await ctx.message.channel.send(f'已將`{v_channel.name}`加入動態語音頻道中!')
        else:
            cursor = Kanatadb.cursor()
            sql = 'INSERT INTO custom_channel (guild_id, guild_channel_id) VALUES (%s, %s)'
            val = (str(ctx.guild.id), vc_id)
            cursor.execute(sql, val)
            Kanatadb.commit()
            await ctx.message.channel.send(f'已將`{v_channel.name}`加入動態語音頻道中!')

    @commands.command(name='delete_channel', aliases=['del_ch'])
    async def delete_channel(self, ctx, vc_id):
        Kanatadb = mysql.connector.connect(
            host='localhost',
            database='kanata',
            password='ImSingleDog1',
            user='root'
        )
        cursor = Kanatadb.cursor()
        sql = 'SELECT * FROM custom_channel'
        cursor.execute(sql)
        channel_data = cursor.fetchall()        
        index = 0
        has_guild = False
        if len(channel_data)>0:
            for i,x in enumerate(channel_data):
                if x[0] == str(ctx.guild.id):
                    has_guild = True
                    index = i
                    break
        
        v_channel = self.client.get_channel(int(vc_id))
        if has_guild:
            cursor = Kanatadb.cursor()
            sql = "DELETE FROM custom_channel WHERE guild_id = %s"
            val = (str(ctx.guild.id), )
            cursor.execute(sql, val)
            Kanatadb.commit()
            await ctx.message.channel.send(f'已將`{v_channel.name}`移出動態語音頻道資料庫!')        
        else:
            await ctx.message.channel.send(f'這個伺服器還未設置動態語音頻道!')


async def setup(client):
    await client.add_cog(music(client))
