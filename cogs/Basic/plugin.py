from __future__ import annotations

import discord
import datetime
import random
from .. import Plugin
from typing import Optional
from discord import Member, VoiceState, User, Message
from discord.ext import commands
from core import Bot, Embed, AfkModel
from discord import Interaction, app_commands
from discord.ui import View, Select
from config import VERSION
from typing import Optional
from discord.ext import commands, tasks
from logging import getLogger
from tortoise import Tortoise
from cogs import *


class HelpSelect(Select, commands.Cog):
    def __init__(self, bot: commands.bot):
        super().__init__(
            placeholder="Choose a category",
            options=[
                discord.SelectOption(
                    label=cog_name, description=cog.__doc__
                ) for cog_name, cog in bot.cogs.items() if cog.__cog_commands__ and cog_name not in ['Jishaku']
            ]
        )

        self.bot = bot

    async def callback(
            self,
            interaction: Interaction
    ) -> None:
        cog = self.bot.get_cog(self.values[0])
        assert cog

        commands_mixer = []
        for i in cog.walk_commands():
            commands_mixer.append(i)

        for i in cog.walk_app_commands():
            commands_mixer.append(i)

        embed = discord.Embed(
            title=f"{cog.__cog_name__} Commands",
            description='\n'.join(
                f"**{command.name}**: `{command.description}`"
                for command in commands_mixer
            )
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


class Basic(Plugin):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    temporary_channels = []
    temporary_categories = []

    @Plugin.listener('on_message')
    async def on_afk(self, message: discord.message):
        if message.author.bot:
            return
        if not message.guild:
            return

        afk = await AfkModel.get_or_none(id=message.author.id, guild_id=message.guild.id)
        if afk:
            await message.reply(
                f"Welcome back {afk.mention}! You were AFK since: {afk.formated_since}"
            )
            return await afk.delete()
        for user in message.mentions:
            afk = await AfkModel.get_or_none(id=user.id, guild_id=message.guild.id)
            if afk:
                await message.reply(
                    f"{afk.mention} has been afk since {afk.formated_since} for: {afk.reason}."
                )

    @app_commands.command(
        name='membercount',
        description="Shows the amount of members in the server"
    )
    async def membercount_command(self, interaction: Interaction):
        embed = Embed(color=discord.Colour.random())
        embed.set_author(name=f"Rick",
                         icon_url=self.bot.user.avatar)
        embed.add_field(name="Current Member Count: ",
                        value=interaction.guild.member_count)
        embed.set_footer(text=interaction.guild,
                         icon_url=interaction.guild.icon)
        embed.timestamp = datetime.datetime.now()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name='afk',
        description="Set your AFK."
    )
    async def set_afk(self, interaction: Interaction, reason: Optional[str]):
        reason = reason or "I'm AFK :)"
        record = await AfkModel.get_or_none(pk=interaction.user.id)
        if not record:
            await AfkModel.create(id=interaction.user.id, guild_id=interaction.guild_id, reason=reason)
            return await self.bot.success(
                f"You're AFK status has been set to: {reason}",
                interaction
            )
        await self.bot.error(
            f"You are already AFK!", interaction
        )

    @commands.hybrid_command(
        name='help',
        description="Shows a list of Rick's commands!"
    )
    async def help_command(self, ctx: commands.context):
        embed = discord.Embed(
            title="Rick's Help Command"
        )
        view = View().add_item(HelpSelect(self.bot))
        await ctx.send(embed=embed, view=view)

    @app_commands.command(
        name='fuckyou',
        description="A random Fuck You"
    )
    @app_commands.describe(
        user="Select a user"
    )
    async def fuckyou_command(self, interaction: Interaction, user: Member = None):
        fuck_off = ["Fuck you Summer, you stupid bitch!",
                    "Fuck you Jerry!", ]

        rick_f_file = open(
            "core\\fuckyouquotes.txt", mode="r", encoding="utf8")
        rick_f_file_facts = rick_f_file.read().split("\n")
        rick_f_file.close()

        for i in rick_f_file_facts:
            if i == "":
                rick_f_file_facts.remove(i)

        fuck_off = fuck_off + rick_f_file_facts

        await interaction.response.send_message(random.choice(fuck_off) + f" And {user.mention} don't think i forgot about you.. Fuck you too :middle_finger:")

    @app_commands.command(
        name='rick',
        description="A random Rick quote"
    )
    async def quote(self, interaction: Interaction):
        # start = ""

        quotes = ["**Wubba lubba dub dub!**",
                  ]
        quote_file = open(
            "core\sanchezquotes.txt", mode="r", encoding="utf8")
        quote_file_facts = quote_file.read().split("\n")
        quote_file.close()

        for i in quote_file_facts:
            if i == "":
                quote_file_facts.remove(i)

        quotes = quotes + quote_file_facts

        # embed = Embed(color=discord.Colour.random())
        # embed.set_author(name=f"Rick",
        #                 icon_url=self.bot.user.avatar)
        # embed.set_thumbnail(url=self.bot.user.avatar.url)
        # embed.add_field(name="", value=random.choice(quotes).capitalize())
        # embed.set_footer(text=interaction.guild,
        #                 icon_url=interaction.guild.icon)
        # await interaction.response.send_message(embed=embed)
        await interaction.response.send_message(random.choice(quotes), ephemeral=True)

    @app_commands.command(
        name='msg-format',
        description="Shows Discord Message Formating!"
    )
    async def message_formating(self, interaction: Interaction):
        await interaction.response.send_message('''
# ***Discord Message Formatting***

## **Headers**

> Add # Before Text For Large Header.

> Add ## Before Text For Medium Header.

> Add ### Before Text For Small Header.

### **Examples**

> # Large Header.
> ## Medium Header.
> ### Small Header.

## Text Formatting

### *Remember Close The Asterisks*

### These Can Be Combined!

### *Italics*
> Italics: - One Asterisk [ * ] Before / After Text.

### **Bold**
> Bold: - Two Asterisks [ * ] Before / After Text.

### ***Bold italics***
> Bold Italics: - Three Asterisks [ * ] Before / After Text.

### __Underline__
> Underline: - Two Underscore Symbols [ _ ] Before / After Text.

### ~~Strikethrough~~
> Strikethrough: - Two Tilde Symbols [ ~ ] Before / After Text.

### ||BOO! Spoiler Message 👻||
> Spoiler: - Two Verticle Bars [ | ] Before / After Text.

## **Lists**

**List Option One: * **

**List Option Two: -**

### **Examples**

> Option One:
> * List Item One
> 
> Option Two:
> - List Item Two

## **Code Blocks**

> Single Line Code Block: Start And End Your Message With A Backtick Symbol [ ` ]
> 
> Multi-Line Code Block: Start And End Your Message With Three Backtick Symbols [ ` ]
> 
> Multi-Line Code Block With Language: Start Your Message With Three Backtick Symbols Then Type The Language Name Then End Your Message With Three Backtick Symbols [ ` ] ( Example: Python = Python or py )

### **Examples**

` Test Single Line Code Block `

```
Test Multi-Line Code Block

```
```python
    async def on_ready(self) -> None:
        log.info("Test Multi-Line Code Block With Language")
        self.tree.sync
```

## **Block Quotes**

**If You Want To Add A Single Block Quote, Just Add (>) Before The First Line. **
***For Example:***

> Test

**If You Want To Add Multiple Lines To A Single Block Quote, Just Add (>>>) Before The First Line. **
***For Example:***

>>> Test
Hello 
How Are Ya?
''', ephemeral=True)

    @app_commands.command(
        name='status',
        description="Server Status"
    )
    async def server_status(self, interaction: Interaction):
        guild = interaction.guild

        voice_channels = len(guild.voice_channels)
        text_channels = len(guild.text_channels)
        sevrer_categories = len(interaction.guild.categories)


        embed = Embed(color=discord.Colour.random())

        embed.set_thumbnail(
            url=interaction.user.avatar.url
        )

        embed.set_image(
            url=guild.icon
        )
        embed.add_field(
            name="Server Name",
            value=guild.name,
            inline=False
        )
        emoji_string = ""
        for e in guild.emojis:
            if e.is_usable():
                emoji_string += str(e)

        embed.add_field(
            name="Custom Emojies",
            value=emoji_string or "No custom emojies detected",
            inline=False
        )
        embed.add_field(
            name="Categories",
            value=sevrer_categories
        )
        embed.add_field(
            name="Voice Channels",
            value=voice_channels
        )
        embed.add_field(
            name="Text Channels",
            value=text_channels
        )
        embed.add_field(
            name="AFK Channel",
            value=guild.afk_channel
        )
        embed.set_author(
            name=self.bot.user.name
        )
        embed.set_footer(
            text=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Basic(bot))
