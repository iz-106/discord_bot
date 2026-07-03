import discord
from discord.ext import commands
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 最新のトークンに更新しました
TOKEN = "MTUyMjU2NjY3MTg3OTg5NzI2Mg.GHm8n6.OpNt9yPFxvyjif1N_6gu-hwvqYaAsuZ3b6HuU8"

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
    # イベントの名前をそのままロール名にする
    role_name = event.name
    
    # サーバー内にイベント名と同じロールがあるか探す
    role = discord.utils.get(guild.roles, name=role_name)
    
    # なければイベント名でロールを自動作成
    if not role:
        role = await guild.create_role(name=role_name, mentionable=True)
        print(f"イベント専用ロール「{role_name}」を作成しました。")

    member = guild.get_member(user.id)
    if member:
        await member.add_roles(role)
        print(f"{member.display_name} にロール「{role_name}」を付与しました。")

# ユーザーが「興味あり」を取り消したとき
@bot.event
async def on_scheduled_event_user_remove(event, user):
    guild = event.guild
    role_name = event.name
    
    role = discord.utils.get(guild.roles, name=role_name)
    if role:
        member = guild.get_member(user.id)
        if member:
            await member.remove_roles(role)
            print(f"{member.display_name} からロール「{role_name}」を削除しました。")

# イベントの状態が更新されたとき（終了またはキャンセル）
@bot.event
async def on_scheduled_event_update(before, after):
    if after.status in [discord.EventStatus.completed, discord.EventStatus.canceled]:
        guild = after.guild
        role_name = after.name
        
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            print(f"イベント「{role_name}」が終了したため、ロールを全員から外してロール自体を削除します。")
            await role.delete()

# イベント自体が「削除」されたとき
@bot.event
async def on_scheduled_event_delete(event):
    guild = event.guild
    role_name = event.name
    
    role = discord.utils.get(guild.roles, name=role_name)
    if role:
        print(f"イベント「{role_name}」が削除されたため、ロールを削除します。")
        await role.delete()

# Webサーバーを裏で同時に起動する
threading.Thread(target=run_server, daemon=True).start()

bot.run(TOKEN)
