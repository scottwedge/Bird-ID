import asyncio

import pytest

import discord_mock as mock
from bot.cogs import get_birds
from bot.data import database
from bot.functions import channel_setup, user_setup


class TestBirds:
    @pytest.yield_fixture(autouse=True)
    def test_suite_cleanup_thing(self):
        yield
        database.delete(f"channel:{self.ctx.channel.id}")
        database.zrem("score:global", str(self.ctx.channel.id))

        database.zrem("users:global", str(self.ctx.author.id))
        database.zrem("streak:global", str(self.ctx.author.id))
        database.zrem("streak.max:global", str(self.ctx.author.id))
        database.delete(f"incorrect.user:{self.ctx.author.id}")

        if self.ctx.guild is not None:
            database.delete(f"users.server:{self.ctx.guild.id}")
            database.delete(f"incorrect.server:{self.ctx.guild.id}")

    def setup(self, guild=False):
        self.bot = mock.Bot()
        self.cog = get_birds.Birds(self.bot)
        self.ctx = mock.Context(self.bot)

        if guild:
            self.ctx.set_guild()

        database.delete(f"channel:{self.ctx.channel.id}")
        database.zrem("score:global", str(self.ctx.channel.id))

        database.zrem("users:global", str(self.ctx.author.id))
        database.zrem("streak:global", str(self.ctx.author.id))
        database.zrem("streak.max:global", str(self.ctx.author.id))

        if self.ctx.guild is not None:
            database.delete(f"users.server:{self.ctx.guild.id}")

        asyncio.run(channel_setup(self.ctx))
        asyncio.run(user_setup(self.ctx))


    ### Bird Command Tests
    def test_bird_dm_1(self):
        self.setup(guild=True)

        coroutine = self.cog.bird.callback(self.cog, self.ctx) # pylint: disable=no-member
        assert asyncio.run(coroutine) is None
        assert self.ctx.messages[
            2
        ].content == "**Recognized arguments:** *Black & White*: `False`, *Female/Juvenile*: `None`, *Taxons*: `None`, *Detected State*: `None`"
        assert self.ctx.messages[
            4
        ].content == "*Here you go!* \n**Use `b!bird` again to get a new image of the same bird, or `b!skip` to get a new bird. Use `b!check guess` to check your answer. Use `b!hint` for a hint.**\n*This is an image.*"

    def test_bird_dm_2(self):
        self.setup(guild=True)

        coroutine = self.cog.bird.callback(self.cog, self.ctx, args_str="bw female") # pylint: disable=no-member
        assert asyncio.run(coroutine) is None
        assert self.ctx.messages[
            2
        ].content == "**Recognized arguments:** *Black & White*: `True`, *Female/Juvenile*: `female`, *Taxons*: `None`, *Detected State*: `None`"
        assert self.ctx.messages[
            4
        ].content == "*Here you go!* \n**Use `b!bird` again to get a new image of the same bird, or `b!skip` to get a new bird. Use `b!check guess` to check your answer. Use `b!hint` for a hint.**\n*This is a female.*"

    def test_bird_dm_3(self):
        self.setup(guild=True)

        coroutine = self.cog.bird.callback(self.cog, self.ctx, args_str="passeriformes yolo bw juvenile") # pylint: disable=no-member
        assert asyncio.run(coroutine) is None
        assert self.ctx.messages[
            2
        ].content == "**Recognized arguments:** *Black & White*: `True`, *Female/Juvenile*: `juvenile`, *Taxons*: `passeriformes`, *Detected State*: `None`"
        assert self.ctx.messages[
            4
        ].content == "*Here you go!* \n**Use `b!bird` again to get a new image of the same bird, or `b!skip` to get a new bird. Use `b!check guess` to check your answer. Use `b!hint` for a hint.**\n*This is a juvenile.*"

    def test_bird_dm_4(self):
        self.setup(guild=True)

        coroutine = self.cog.bird.callback(self.cog, self.ctx, args_str="13435 troglodytidae f")  # pylint: disable=no-member
        assert asyncio.run(coroutine) is None
        assert self.ctx.messages[
            2
        ].content == "**Recognized arguments:** *Black & White*: `False`, *Female/Juvenile*: `female`, *Taxons*: `troglodytidae`, *Detected State*: `None`"
        assert self.ctx.messages[
            4
        ].content == "*Here you go!* \n**Use `b!bird` again to get a new image of the same bird, or `b!skip` to get a new bird. Use `b!check guess` to check your answer. Use `b!hint` for a hint.**\n*This is a female.*"
