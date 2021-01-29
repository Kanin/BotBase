import os

import aiohttp_jinja2
import jinja2
from aiohttp import web
from discord.ext import commands

BLACKLISTED_EVENTS = ["presence_update"]


class BuiltinAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clean_name = self.bot.user.name.replace(" ", "_")
        self.runner = None
        self.app = web.Application()
        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader("utils/assets/templates"))
        self.routes = web.RouteTableDef()
        self.routes.static("/assets", "utils/assets/", show_index=True, name="Test")
        self.host = os.getenv("API_HOST", "localhost")
        self.port = os.getenv("API_PORT", 8080)
        self.bot.loop.create_task(self.server())
        self.events = {}

    def cog_unload(self):
        self.bot.log.info("Stopping api server")
        self.bot.loop.create_task(self.runner.cleanup())

    async def server(self):

        @self.routes.get("/")
        @aiohttp_jinja2.template("home.jinja2")
        async def home(request):
            return {}

        @self.routes.get("/commands")
        async def com_list(request):
            response_object = {}
            for command in self.bot.walk_commands():
                if command.hidden:
                    continue
                if command.enabled:
                    if command.cog_name not in response_object:
                        response_object[command.cog_name] = {}
                    cmd = str(command).replace(" ", "_")
                    response_object[command.cog_name].update({cmd: {}})
                    response_object[command.cog_name][cmd]["description"] = command.help
                    if "bot_perms" in dir(command.callback):
                        response_object[command.cog_name][cmd]["bot_perms"] = \
                            [x for x, y in command.callback.bot_perms.items()]
                    if "user_perms" in dir(command.callback):
                        response_object[command.cog_name][cmd]["user_perms"] = \
                            [x for x, y in command.callback.user_perms.items()]
            return web.json_response(data=response_object)

        @self.routes.get("/metrics")
        async def metrics(request):
            lines = []

            for event, count in self.events.items():
                lines.append(f"event_counts,bot={self.clean_name},type={event} count={count}i")

            for command, count in self.bot.commands_used.items():
                lines.append(f"commands_ran,bot={self.clean_name},command={command} count={count}i")

            lines.append(f"guild_count,bot={self.clean_name} count={len(self.bot.guilds)}i")
            return web.Response(text="\n".join(lines))

        self.app.add_routes(self.routes)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        server = web.TCPSite(self.runner, self.host, self.port)
        await server.start()
        self.bot.log.info(f"API Server running on {server.name}")

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        if msg.get("op") != 0:
            # Not a dispatch (might be useful to track heartbeats, reconnects, invalid sessions etc. tho)
            return

        event = msg.get("t", "none").lower()
        if event not in BLACKLISTED_EVENTS:
            if event not in self.events.keys():
                self.events[event] = 1
            else:
                self.events[event] += 1


def setup(bot):
    bot.add_cog(BuiltinAPI(bot))
