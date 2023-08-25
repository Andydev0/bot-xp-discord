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

# Nome do arquivo JSON para armazenar os dados de experiência
json_filename = 'user_levels.json'    

processed_threads = set()


# Lista de canais excluídos onde o sistema de níveis não funcionará
#excluded_channels = [1143327353519480952, 1143347662054236322, 1143368647390277805, 1143370778767806504, 1143502875071352913]  # Substitua pelos IDs reais dos canais



# Função para salvar os dados de experiência em um arquivo JSON
def save_user_levels(filename, user_levels_data):
    user_levels = {}

    for user_id, data in user_levels_data.items():
        user_levels[user_id] = {
            "exp": data["exp"],
            "level": data["level"],
            "data_xp": data.get("data_xp", [])
        }

    with open(filename, 'w') as file:
        json.dump(user_levels, file, indent=4)


 # Função para carregar os dados de experiência de um arquivo JSON
def load_user_levels(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Retorna um dicionário vazio se o arquivo não existir

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
processed_threads = set()

    
@bot.event
async def on_thread_create(thread):
    if thread.id not in processed_threads:  # Verifica se o tópico já foi processado
        user_id = thread.owner_id
        dados = load_user_levels(json_filename)

        if user_id not in dados:
            dados[user_id] = {'exp': 0, 'level': 1}
        dados[user_id]['exp'] += exp_per_thread
        while dados[user_id]['exp'] >= exp_per_level:
            dados[user_id]['exp'] -= exp_per_level
            dados[user_id]['level'] += 1
            await thread.send(f"Parabéns, <@{user_id}>! Você alcançou o nível {dados[user_id]['level']}!")
            save_user_levels(json_filename, dados)
        processed_threads.add(thread.id)  # Adiciona o tópico ao conjunto de tópicos processados




@bot.event #exp por tempo decorrido
async def on_message(message):
    if isinstance(message.channel, discord.Thread):
        if message.author != bot.user and len(message.content) >= 10:
            user_id = str(message.author.id)

            now_utc = datetime.datetime.utcnow()
            created_at_utc = message.channel.created_at.replace(tzinfo=None)

            time_difference = now_utc - created_at_utc
            if time_difference <= datetime.timedelta(minutes=1):
                await adicionar_xp(user_id, 10, message.channel, message.author)
            elif time_difference <= datetime.timedelta(minutes=2):
                await adicionar_xp(user_id, 9, message.channel, message.author)
            elif time_difference <= datetime.timedelta(minutes=3):
                await adicionar_xp(user_id, 8, message.channel, message.author) 
            elif time_difference <= datetime.timedelta(minutes=4):
                await adicionar_xp(user_id, 7, message.channel, message.author) 
            elif time_difference <= datetime.timedelta(minutes=5):
                await adicionar_xp(user_id, 6, message.channel, message.author) 
            elif time_difference <= datetime.timedelta(minutes=6):
                await adicionar_xp(user_id, 5, message.channel, message.author) 
            elif time_difference <= datetime.timedelta(minutes=7):
                await adicionar_xp(user_id, 4, message.channel, message.author) 
            elif time_difference <= datetime.timedelta(minutes=8):
                await adicionar_xp(user_id, 3, message.channel, message.author) 
            elif time_difference <= datetime.timedelta(minutes=9):
                await adicionar_xp(user_id, 2, message.channel, message.author)
            else:
                await adicionar_xp(user_id, 1, message.channel, message.author) 

    await bot.process_commands(message)



@bot.command()
async def level(ctx):
    user_id = ctx.author.id
    dados = load_user_levels(json_filename)
    if user_id in dados:
        await ctx.send(f"{ctx.author.mention}, seu nível é {dados[user_id]['level']}.")
    else:
        await ctx.send(f"{ctx.author.mention}, você ainda não possui um nível.")

@bot.command()
@commands.has_permissions(administrator=True)
async def dar_xp(ctx, user: discord.User, xp_amount: int):
    if ctx.author.guild_permissions.administrator:
        canal = ctx.message.channel
        await adicionar_xp(str(user.id), xp_amount, canal, user)
    else:
        await ctx.send("Você não tem permissão para usar este comando.")


@bot.command()
async def top(ctx):
    dados = load_user_levels(json_filename)
    sorted_users = sorted(dados.items(), key=lambda x: x[1]['level'], reverse=True)
    top_users = sorted_users[:10]

    leaderboard_message = "Top 10 usuários com mais níveis:\n"

    for index, (user_id, data) in enumerate(top_users, start=1):
        try:
            user = await bot.fetch_user(user_id)
        except discord.NotFound:
            user = None

        if user:
            data_xp = data.get('data_xp', [])
            leaderboard_message += f"{index}. {user.mention} - Nível {data['level']}, XP ganho: {sum(entry['xp_ganha'] for entry in data_xp)}\n"
        else:
            leaderboard_message += f"{index}. *Usuário não encontrado* - Nível {data['level']}\n"

    await ctx.send(leaderboard_message)



async def adicionar_xp(user_id, xp_ganha, canal, author):
    dados = load_user_levels(json_filename)
    if user_id not in dados:
        dados[user_id] = {'exp': 0, 'level': 1, 'data_xp': []}
    else:
        print("já esta no geison")
    dados[user_id]['exp'] += xp_ganha
    dados[user_id]['data_xp'].append({
        "xp_ganha": xp_ganha,
        "data_da_xp": datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    })
    save_user_levels(json_filename, dados)
    print(f"foi adicionado para o user: {user_id} XP: {xp_ganha}")
    await adicionar_lvl(user_id, canal, author)

    

async def adicionar_lvl(user_id, canal, author):
    dados = load_user_levels(json_filename)
    while dados[user_id]['exp'] >= exp_per_level:
        dados[user_id]['exp'] -= exp_per_level
        dados[user_id]['level'] += 1
        await canal.send(f"Parabéns, {author.mention}! Você alcançou o nível {dados[user_id]['level']}!")
    save_user_levels(json_filename, dados)

bot.run('---')

