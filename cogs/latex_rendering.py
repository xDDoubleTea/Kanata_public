import discord
from discord import Interaction, app_commands
from discord.ui import button, select, View, Button
from discord.ext import commands

from IPython.display import Latex, display_latex
from IPython.lib import latextools
import matplotlib.pyplot as plt
import io
from view.Latex_handling import Latex_render_for_dc, latex_msg_options



class latex_rendering(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'latex')
    async def latex(self, interaction:Interaction, data:str):
        renderer = Latex_render_for_dc()
        new = '$'
        new += data
        new += '$'
        img = await renderer.Latex_dvipng(string = new)
        if img != None:
            await interaction.response.send_message(file = img)
            msg = await interaction.original_response()
            return await msg.edit(view = latex_msg_options(attached_msg = msg, latex_data=data))
        else:
            await interaction.response.send_message(content = 'Falied to render! Please check if the input has any possible error!')
            msg = await interaction.original_response()
            await msg.edit(view = await renderer.fail_rendering(msg = msg))
            return await msg.add_reaction('❗')

async def setup(client):
    await client.add_cog(latex_rendering(client))