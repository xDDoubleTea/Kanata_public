import matplotlib.pyplot as plt
import discord
from io import BytesIO

def get_result_pie_chart(options:list, ratio:list, title:str, explode:tuple, startangle:int = 90):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    fig1, ax1 = plt.subplots()
    ax1.pie(
        ratio, 
        explode=explode, 
        labels=options, 
        autopct='%1.2f%%',
        shadow=True,
        startangle=startangle,
        textprops = dict(color = '#b04c51', fontsize = 20, fontweight = 400)
    )
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig1.patch.set_facecolor('#b5b2b1')
    ax1.set_title(title, fontsize=25 ,color = '#3764c4',fontweight = 600)
    with BytesIO() as image_binary:
        plt.savefig(image_binary,format='png', bbox_inches="tight")
        image_binary.seek(0)
        file = discord.File(fp = image_binary, filename = 'uwu.png')
        return file