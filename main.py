import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

# ==================== FLASK (UptimeRobot) ====================
app = Flask(__name__)


@app.route("/")
def home():
    return "FuryBot is online ✅", 200


@app.route("/health")
def health():
    return {"status": "ok", "bot": "FuryBot"}, 200


def run_flask():
    # Puerto por defecto 8080 (compatible con la mayoría de hosts)
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()


# ==================== BOT ====================
intents = discord.Intents.default()
intents.members = True          # Necesario para on_member_join y member_count
intents.message_content = True  # Por si más adelante agregas comandos de texto

bot = commands.Bot(
    command_prefix="!",          # Prefijo por si quieres comandos de texto después
    intents=intents,
    help_command=None
)


@bot.event
async def on_ready():
    print(f"✅ {bot.user} está online!")
    print(f"📊 Servidores: {len(bot.guilds)}")
    print(f"👤 Usuarios: {len(bot.users)}")

    # Sincronizar slash commands
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}")


@bot.event
async def on_guild_join(guild: discord.Guild):
    print(f"➕ Me uní a: {guild.name} ({guild.id})")


async def load_cogs():
    """Carga todos los cogs"""
    await bot.load_extension("welcomer")
    print("📦 Cog 'welcomer' cargado")


async def main():
    keep_alive()  # Arranca Flask en un hilo separado
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ ERROR: No se encontró DISCORD_TOKEN en las variables de entorno.")
        print("   Crea un archivo .env con: DISCORD_TOKEN=tu_token_aqui")
    else:
        asyncio.run(main())
