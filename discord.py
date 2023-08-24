import discord
from discord.ext import commands
import datetime
import json

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False


bot = commands.Bot(command_prefix='!', intents=intents)

exp_per_thread = 15
exp_per_level = 20


user_levels = {}  # Dicionário para armazenar os níveis e xp dos usuários

# Lista de canais excluídos onde o sistema de níveis não funcionará
#excluded_channels = [1143327353519480952, 1143347662054236322, 1143368647390277805, 1143370778767806504, 1143502875071352913]  # Substitua pelos IDs reais dos canais



# Função para salvar os dados de experiência em um arquivo JSON
def save_user_levels(filename, user_levels_data):
    user_data_to_save = {}

    for user_id, data in user_levels_data.items():
        user_data_to_save[user_id] = {
            "exp": data["exp"],
            "level": data["level"]
        }

    with open(filename, 'w') as file:
        json.dump(user_data_to_save, file, indent=4)

 # Função para carregar os dados de experiência de um arquivo JSON
def load_user_levels(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Retorna um dicionário vazio se o arquivo não existir

# Nome do arquivo JSON para armazenar os dados de experiência
json_filename = 'user_levels.json'

# Carrega os dados de experiência existentes ou cria um dicionário vazio
user_levels = load_user_levels(json_filename)       

processed_threads = set()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
processed_threads = set()

    
@bot.event
async def on_thread_create(thread):
    if thread.id not in processed_threads:  # Verifica se o tópico já foi processado
        user_id = thread.owner_id
        if user_id not in user_levels:
            user_levels[user_id] = {'exp': 0, 'level': 1}
        user_levels[user_id]['exp'] += exp_per_thread
        while user_levels[user_id]['exp'] >= exp_per_level:
            user_levels[user_id]['exp'] -= exp_per_level
            user_levels[user_id]['level'] += 1
            await thread.send(f"Parabéns, <@{user_id}>! Você alcançou o nível {user_levels[user_id]['level']}!")
            save_user_levels(json_filename, user_levels)
        processed_threads.add(thread.id)  # Adiciona o tópico ao conjunto de tópicos processados




@bot.event #exp por tempo decorrido
async def on_message(message):
    if isinstance(message.channel, discord.Thread):
        if message.author != bot.user and len(message.content) >= 10:
            user_id = message.author.id
            if user_id not in user_levels:
                user_levels[user_id] = {'exp': 0, 'level': 1}
            
            now_utc = datetime.datetime.utcnow()
            created_at_utc = message.channel.created_at.replace(tzinfo=None)
            
            time_difference = now_utc - created_at_utc
            if time_difference <= datetime.timedelta(minutes=1):
                user_levels[user_id]['exp'] += 10
            elif time_difference <= datetime.timedelta(minutes=2):
                user_levels[user_id]['exp'] += 9
            elif time_difference <= datetime.timedelta(minutes=3):
                user_levels[user_id]['exp'] += 8
            elif time_difference <= datetime.timedelta(minutes=4):
                user_levels[user_id]['exp'] += 7
            elif time_difference <= datetime.timedelta(minutes=5):
                user_levels[user_id]['exp'] += 6
            elif time_difference <= datetime.timedelta(minutes=6):
                user_levels[user_id]['exp'] += 5
            elif time_difference <= datetime.timedelta(minutes=7):
                user_levels[user_id]['exp'] += 4
            elif time_difference <= datetime.timedelta(minutes=8):
                user_levels[user_id]['exp'] += 3
            elif time_difference <= datetime.timedelta(minutes=9):
                user_levels[user_id]['exp'] += 2                            
            else:
                user_levels[user_id]['exp'] += 1
            
            while user_levels[user_id]['exp'] >= exp_per_level:
                user_levels[user_id]['exp'] -= exp_per_level
                user_levels[user_id]['level'] += 1
                await message.channel.send(f"Parabéns, {message.author.mention}! Você alcançou o nível {user_levels[user_id]['level']}!")

    await bot.process_commands(message)
    save_user_levels(json_filename, user_levels)



@bot.command()
async def level(ctx):
    user_id = ctx.author.id
    if user_id in user_levels:
        await ctx.send(f"{ctx.author.mention}, seu nível é {user_levels[user_id]['level']}.")
    else:
        await ctx.send(f"{ctx.author.mention}, você ainda não possui um nível.")

@bot.command()
@commands.has_permissions(administrator=True)
async def dar_xp(ctx, user: discord.User, xp_amount: int):
    # Verifica se o usuário tem permissões de administrador para usar o comando
    if ctx.author.guild_permissions.administrator:
        if user.id not in user_levels:
            user_levels[user.id] = {'exp': 0, 'level': 1}
        
        user_levels[user.id]['exp'] += xp_amount
        while user_levels[user.id]['exp'] >= exp_per_level:
            user_levels[user.id]['exp'] -= exp_per_level
            user_levels[user.id]['level'] += 1
            await ctx.send(f"XP atribuído a {user.mention}. {user.mention} agora está no nível {user_levels[user.id]['level']}.")
        
        # Salva os dados de experiência após a modificação
        save_user_levels(json_filename, user_levels)
    else:
        await ctx.send("Você não tem permissão para usar este comando.")

@bot.command()
async def top(ctx):
    sorted_users = sorted(user_levels.items(), key=lambda x: x[1]['level'], reverse=True)
    top_users = sorted_users[:10]  # Pega os 10 primeiros usuários da lista ordenada
    
    leaderboard_message = "Top 10 usuários com mais níveis:\n"
    
    for index, (user_id, data) in enumerate(top_users, start=1):
        try:
            user = await bot.fetch_user(user_id)  # Obtém o objeto de usuário usando o ID
        except discord.NotFound:
            user = None
        
        if user:
            leaderboard_message += f"{index}. {user.mention} - Nível {data['level']}\n"
        else:
            leaderboard_message += f"{index}. *Usuário não encontrado* - Nível {data['level']}\n"
    
    await ctx.send(leaderboard_message)


bot.run('token')

