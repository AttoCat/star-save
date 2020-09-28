import discord
from discord.ext import commands
import dotenv
import os
import pathlib
import traceback

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")


class StarSave(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        os.chdir('./star-save')
        path = pathlib.Path("./cogs")

        for cog in path.glob("*.py"):
            try:
                self.load_extension(f"cogs.{cog.stem}")
                print(f"Loaded {cog.stem}")
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        print(f"Bot is ready! \nlibrary version:{discord.__version__}")
        channel = bot.get_channel(706779308211044352)
        await channel.send(f"{self.user}: 起動完了")


if __name__ == "__main__":
    bot = StarSave(command_prefix=["st!", "st."])
    bot.run(TOKEN)
