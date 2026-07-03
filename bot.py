import discord
from discord.ext import commands

# あなたのトークン（後ろの「"」も付いています）
TOKEN = "MTUyMjU2NjY3MTg3OTg5NzI2Mg.GGTweW.46IBReqaFjyMU2CKxKbHW8fn28PiFYZQA8wO9A"

# イベント用の専用ロールの名前
ROLE_NAME = "イベント参加者"

intents = discord.Intents.default()
intents.members = True          # メンバー管理の権限
intents.guild_scheduled_events = True  # イベント管理の権限

# ★ここを正しい書き方に修正しました
bot = commands.Bot(command_prefix="!", intents=intents)

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
        print(f"ロール「{ROLE_NAME}」を作成しました。")

    member = guild.get_member(user.id)
    if member:
        await member.add_roles(role)
        print(f"{member.display_name} にロールを付与しました。")

# ユーザーが「興味あり」を取り消したとき
@bot.event
async def on_scheduled_event_user_remove(event, user):
    guild = event.guild
    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if role:
        member = guild.get_member(user.id)
        if member:
            await member.remove_roles(role)
            print(f"{member.display_name} からロールを削除しました。")

# イベントの状態が更新されたとき（終了またはキャンセル）
@bot.event
async def on_scheduled_event_update(before, after):
    if after.status in [discord.EventStatus.completed, discord.EventStatus.canceled]:
        guild = after.guild
        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        
        if role:
            print(f"イベント「{after.name}」が終了したため、ロールを全員から外します。")
            for member in role.members:
                await member.remove_roles(role)
                print(f"{member.display_name} からロールを外しました。")

bot.run(TOKEN)