import re

import discord
from discord.ext import commands
from discord.ext.commands.converter import Greedy

from config import config


def command_signature(command: commands.Command):
    if command.usage:
        return command.usage

    params = command.clean_params
    if not params:
        return ""

    result = []
    for name, param in params.items():
        if param.kind == param.VAR_POSITIONAL:
            result.append(f"[{clean_param(param)}...]")
        elif isinstance(param.annotation, type(Greedy)):
            result.append(f"[{clean_param(param)}]...")
        elif param.default is None:
            result.append(f"[{clean_param(param)}]")
        else:
            result.append(f"<{clean_param(param)}>")

    return ' '.join(result)


def clean_param(param):
    if not param.annotation:
        return param.name

    clean = str(param).replace(" ", "")
    clean = re.sub("Union\[|]|=None", "", clean)
    if "Union" in clean:
        args = clean.split(":")[1]
        arg_names = [item.split(".")[-1] for item in args.split(",")]
        union = f"{', '.join(arg_names[:-1])}, or {arg_names[-1]}" if len(arg_names) > 2 else " or ".join(arg_names)
        clean = f"{clean.split(':')[0]}:{union}"
    if ":" in clean:
        args = clean.split(":")[1].split(".")[-1]
        clean = f"{clean.split(':')[0]}:{args}" if args else clean
    clean = re.sub(r"\bstr\b|\bActionReason\b", "Text", clean)
    clean = re.sub(r"\bint\b", "Number", clean)
    clean = re.sub(r"\bActionReason\b", "Text", clean)
    clean = re.sub(r"\bMemberID\b", "Member or ID", clean)
    return clean


class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            em = discord.Embed(description=page, color=config.colors["main"])
            em.set_author(name="Here is the help you requested!")
            await destination.send(embed=em)

    def get_opening_note(self):
        return None

    def get_command_signature(self, command):
        return f"{self.clean_prefix}{command.qualified_name} {command_signature(command)}"

    def get_ending_note(self):
        command_name = self.context.invoked_with
        return f"Type `{self.clean_prefix}{command_name} [command]` for more info on a command.\n" \
               f"You can also type `{self.clean_prefix}{command_name} [category]` for more info on a category."

    def add_bot_commands_formatting(self, command_list, heading):
        if command_list:
            joined = ", ".join(c.name for c in command_list) + "\n"
            self.paginator.add_line(f"__**{heading}**__")
            self.paginator.add_line(joined)

    def add_subcommand_formatting(self, command):
        fmt = f"{self.clean_prefix}{command.qualified_name} - `{command.description}`" \
            if command.description else \
            f"{self.clean_prefix}{command.qualified_name}"
        self.paginator.add_line(fmt)

    def add_aliases_formatting(self, aliases):
        self.paginator.add_line(self.aliases_heading + ', '.join(aliases), empty=True)

    def add_command_formatting(self, command):
        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(signature, empty=True)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand(aliases_heading="**Aliases:** ", verify_checks=False)
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))