import discord
from discord.ext import commands
import textwrap
import contextlib
import traceback
import io


class Owner(commands.Cog):
    __slots__ = ('client', 'name', '_last_result')

    def __init__(self, bot, name=None):
        self.bot = bot
        self.name = name if name is not None else type(self).__name__
        self._last_result = None

    async def cog_check(self, ctx):
        # シンプルにBOTのオーナーであるか
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True)
    async def said(self, ctx, *, arg):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.send(arg)

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}'
        f'{"^":>{e.offset}}\n'
        f'{e.__class__.__name__}: {e}```'

    @commands.command(pass_context=True, hidden=True, name='eval')  # 以下コピペ
    async def _eval(self, ctx):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())
        await ctx.send('コマンドを入力してください')
        message = await self.bot.wait_for(
            'message', check=lambda m: m.author == ctx.author
            and m.channel == ctx.channel)
        body = self.cleanup_code(message.content)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with contextlib.redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except Exception:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(Owner(bot))
