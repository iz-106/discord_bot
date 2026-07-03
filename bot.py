import discord
from discord.ext import commands
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# あなたのトークン
TOKEN = "MTUyMjU2NjY3MTg3OTg5NzI2Mg.Gr6YY2.i7Vji_KVfoCfWXhKTRZDNwdIXvK3AR5VS041kQ"

# イベント用の専用ロールの名前
ROLE_NAME = "イベント参加者"

intents = discord.Intents.default()
intents.members = True          # メンバー管理の権限
intents.guild_scheduled_events = True  # イベント管理の権限

bot = commands.Bot(command_prefix="!", intents=intents)

# --- 居眠り防止用（Render用のダミーWebサーバー） ---
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    server = HTTPServer(("0.0.0.0", 10000), DummyServer)
    server.serve_forever()
# --- ここまで ---

# Botが起動したとき
@bot.event
async def on_ready():
    print(f"{bot.user.name} がオンラインになりました！")

# ユーザーが「興味あり」を押したとき
@bot.event
async def on_scheduled_event_user_add(event, user):
    guild = event.guild
    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if not role:
        role = await guild.create_role(name=ROLE_NAME, mentionable=True)
    member = guild.get_member(user.id)
    if member:
        await member.add_roles(role)

# ユーザーが「興味あり」を取り消したとき
@bot.event
async def on_scheduled_event_user_remove(event, user):
    guild = event.guild
    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if role:
        member = guild.get_member(user.id)
        if member:
            await member.remove_roles(role)

# イベントの状態が更新されたとき（終了またはキャンセル）
@bot.event
async def on_scheduled_event_update(before, after):
    if after.status in [discord.EventStatus.completed, discord.EventStatus.canceled]:
        guild = after.guild
        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if role:
            for member in role.members:
                await member.remove_roles(role)

# ★新機能：イベント自体が「削除」されたとき
@bot.event
async def on_scheduled_event_delete(event):
    guild = event.guild
    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if role:
        print(f"イベント「{event.name}」が削除されたため、ロールを全員から外します。")
        for member in role.members:
            await member.remove_roles(role)

# Webサーバーを裏で同時に起動する
threading.Thread(target=run_server, daemon=True).start()

bot.run(TOKEN)
