import subprocess

import asyncio
import discord
from decouple import config
from discord.ext import commands
from utils.embed_handler import simple_embed

from constants import system_log_channel_id

TOKEN = config("DISCORD_BOT_TOKEN")


class MyBot(commands.Bot):
    def __init__(self):
        self.build_version = None
        intents = discord.Intents.none()
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def setup_hook(self) -> None:
        await self.load_extension("cogs.status")
        await self.load_extension("cogs.games")
        await self.load_extension("cogs.health_check")
        await self.tree.sync()
        print("✅ Synced application commands")


bot = MyBot()

async def send_restart_message(client: commands.Bot):
    try:
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        commit_hash = config("BOT_BUILD_VERSION", "mystery-build")

    channel = client.get_channel(system_log_channel_id)
    client.build_version = commit_hash

    if channel is None:
        return

    try:
        embed = simple_embed(message=f"Build version: `{commit_hash}`", title="", color=discord.Color.teal())
        embed.set_footer(text=f"🔄 Bot Restarted")
        await channel.send(
            embed=embed,
        )
    except discord.Forbidden:
        pass


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await send_restart_message(bot)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.guild is None:
        try:
            await message.channel.send(
                "Want to contact staff? DM 👉 <@712323581828136971>"
            )
        except discord.Forbidden:
            pass
        return

    await bot.process_commands(message)


async def main():
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
