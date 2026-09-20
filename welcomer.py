import discord
from discord import app_commands
from discord.ext import commands
import json
import os

CONFIG_FILE = "welcome_config.json"


class Welcomer(commands.Cog):
    """Sistema de bienvenida simple estilo Welcomer"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_config(self) -> None:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def _format_message(self, template: str, member: discord.Member) -> str:
        """Reemplaza las variables del mensaje de bienvenida"""
        return (
            template
            .replace("{user}", member.mention)
            .replace("{member-count}", str(member.guild.member_count))
            .replace("{server}", member.guild.name)
        )

    @app_commands.command(
        name="welcome-setup",
        description="Configura el mensaje y canal de bienvenida del servidor"
    )
    @app_commands.describe(
        canal="Canal donde se enviarán los mensajes de bienvenida",
        mensaje="Mensaje de bienvenida. Variables: {user} {member-count} {server}"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_setup(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel,
        mensaje: str
    ):
        """Configura el sistema de bienvenida"""
        guild_id = str(interaction.guild.id)

        self.config[guild_id] = {
            "channel_id": canal.id,
            "message": mensaje
        }
        self._save_config()

        # Preview del mensaje
        preview = self._format_message(mensaje, interaction.user)

        embed = discord.Embed(
            title="✅ Sistema de bienvenida configurado",
            color=discord.Color.green(),
            description=(
                f"**Canal:** {canal.mention}\n"
                f"**Mensaje:**\n```{mensaje}```\n"
                f"**Vista previa:**\n{preview}"
            )
        )
        embed.set_footer(text="FuryBot • Welcome System")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @welcome_setup.error
    async def welcome_setup_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas el permiso **Gestionar Servidor** para usar este comando.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Ocurrió un error: `{error}`",
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Envía el mensaje de bienvenida cuando un usuario se une"""
        guild_id = str(member.guild.id)
        data = self.config.get(guild_id)

        if not data:
            return

        channel = member.guild.get_channel(data["channel_id"])
        if channel is None:
            return

        message = self._format_message(data["message"], member)

        try:
            await channel.send(message)
        except discord.Forbidden:
            # El bot no tiene permisos para hablar en ese canal
            pass
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcomer(bot))
