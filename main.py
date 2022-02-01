import time
import ujson
import atexit
import hashlib
import aiohttp
import requests
import asyncio
import logging
from tinydb import TinyDB
from texts import version
from texts import TextFields as tF

db = TinyDB("christina-db.json", sort_keys=True,
            indent=4, separators=(",", ": "))
config = ujson.load(open("config.json"))

global host
global verifyKey
global account
global httpapi_port
global mcservers
host = config["host"]
verifyKey = config["verifyKey"]
account = config["account"]
httpapi_port = config["httpapi_port"]
mcservers = config["mcservers"]


def init():
    print("""
    ______ __           __       __   __                   _   __       __                          __
   / ____// /___ _____ /_/_____ / /_ /_/______ ______     / | / /_____ / /_ _      __ ______ _____ / /__
  / /    / __  // ___// //  __// __// // __  // __  /    /  |/ // _  // __/| | /| / // __  // ___// //_/
 / /___ / / / // /   / //__  // /_ / // / / // /_/ /    / /|  //  __// /_  | |/ |/ // /_/ // /   /  <
/_____//_/ /_//_/   /_//____//___//_//_/ /_/ \__/_/    /_/ |_//____//___/  |__/|__//_____//_/   /_//_/
    """)

    logging.info(f"Christina Network v{version}")
    init_start = time.time()

    logging.info("Verifying...")
    send_json = {"verifyKey": verifyKey}
    apiresponse = requests.post(f"http://{host}/verify", json=send_json).json()
    global sessionKey
    sessionKey = apiresponse["session"]
    logging.info(f"Get sessionKey: {sessionKey}")

    logging.info("Binding...")
    send_json = {"sessionKey": sessionKey, "qq": account}
    requests.post(f"http://{host}/bind", json=send_json)

    init_done = time.time()
    logging.info(f"Initialization done ({round(init_done-init_start, 3)}s)!")


class HttpApiConnect:
    """向 HTTP API 发送请求"""
    session_connect = aiohttp.ClientSession()

    def __init__(self, target):
        self.target = target

    # MiraiApiHttp
    async def sendGroupMessage(self, send_message_chain):
        send_json = {
            "sessionKey": sessionKey,
            "target": self.target,
            "messageChain": send_message_chain
        }
        async with self.session_connect.post(f"http://{host}/sendGroupMessage", json=send_json) as resp:
            return resp

    async def groupMemberInfo(self, memberId):
        async with self.session_connect.get(f"http://{host}/memberInfo?sessionKey={sessionKey}&target={self.target}&memberId={memberId}") as resp:
            return await resp.text()

    # Christina API
    async def getMCStatus(self, server_abbr):
        async with self.session_connect.get(f"http://127.0.0.1:{httpapi_port}/mcstatus?server_abbr={server_abbr}") as resp:
            return [resp.status, await resp.text()]

    # Gravatar
    async def getGravatar(self, email_md5):
        async with self.session_connect.get(f"https://gravatar.loli.net/avatar/{email_md5}?d=404") as resp:
            return resp.status


class ProcessCommand:
    """处理群消息"""
    global register_dict
    register_dict = {}

    def __init__(self, message_raw):
        # self.message_type = message_raw["type"]
        self.lang = 0  # 0(默认)中文 1英文
        self.message_chain = message_raw["data"]["messageChain"]
        self.message_sender_id = message_raw["data"]["sender"]["id"]
        self.message_group_id = message_raw["data"]["sender"]["group"]["id"]
        self.message_text = ""
        for chain_item in self.message_chain:
            if chain_item["type"] == "Plain":
                self.message_text += chain_item["text"]
            elif chain_item["type"] == "At":
                self.message_text += f" {chain_item['target']} "
        self.message_item_list = self.message_text.split()
        self.httpapi = HttpApiConnect(self.message_group_id)

    def registerCommand(command_name):
        def wrapper(func):
            register_dict[command_name] = func
        return wrapper

    @registerCommand("help")
    async def chtHelp(self):
        await self.httpapi.sendGroupMessage([
            {"type": "Plain", "text": tF.command_help[self.lang]}
        ])

    @registerCommand("info")
    async def chtInfo(self):
        await self.httpapi.sendGroupMessage([
            {"type": "Plain", "text": tF.info[self.lang]}
        ])

    @registerCommand("gravatar")
    async def chtGravatar(self):
        if len(self.message_item_list) - self.lang == 2:
            await self.httpapi.sendGroupMessage([
                {"type": "Plain", "text": tF.gravatar_help[self.lang]}
            ])
        else:
            email_md5 = hashlib.md5(
                self.message_item_list[-1].encode(encoding='UTF-8')).hexdigest()
            gravatar_status = await self.httpapi.getGravatar(email_md5)
            if gravatar_status == 200:
                await self.httpapi.sendGroupMessage([
                    {"type": "Plain", "text": f"MD5: {email_md5}"},
                    {"type": "Image",
                        "url": f"https://gravatar.loli.net/avatar/{email_md5}?&s=320"}
                ])
            elif gravatar_status == 404:
                await self.httpapi.sendGroupMessage([
                    {"type": "Plain",
                        "text": f"MD5: {email_md5}\n{tF.gravatar_404[self.lang]}"},
                ])

    @registerCommand("mcstatus")
    async def chtMCStatus(self):
        if str(self.message_group_id) in mcservers:
            for server_abbr in mcservers[str(self.message_group_id)]:
                server_status = await self.httpapi.getMCStatus(server_abbr)
                if server_status[0] == 200:
                    server_status_raw = ujson.loads(server_status[1])
                    server_addr = server_status_raw["addr"]
                    server_data = server_status_raw["data"]

                    server_ping = server_data["ping"]
                    server_version = server_data["version"]["name"]
                    server_players_online = server_data["players"]["online"]
                    server_players_max = server_data["players"]["max"]

                    server_players_list = ""
                    if server_players_online > 0:
                        try:
                            server_players_sample = server_data["players"]["sample"]
                            if server_players_online <= 8:
                                for server_player in server_players_sample:
                                    server_players_list += f"\n> {server_player['name']}"
                            else:
                                for server_player in range(7):
                                    server_players_list += f"\n> {server_players_sample[server_player]['name']}"
                                server_players_list += f"\n+ {server_players_online-7} {tF.mcstatus_more[self.lang]}"
                        except KeyError:
                            pass  # 玩家数大于 0 但不显示
                        except IndexError:
                            pass  # 玩家数不匹配
                    await self.httpapi.sendGroupMessage([
                        {"type": "Plain", "text": tF.mcstatus(
                            self.lang, server_addr, server_ping, server_version, server_players_online, server_players_max, server_players_list)}
                    ])
                else:
                    await self.httpapi.sendGroupMessage([
                        {"type": "Plain", "text": tF.mcstatus_error[self.lang]}
                    ])
        else:
            await self.httpapi.sendGroupMessage([
                {"type": "Plain", "text": tF.mcstatus_not_set[self.lang]}
            ])

    async def processMessage(self):
        logging.debug(f"[Message Text] {self.message_text}")
        logging.debug(f"[Message Item List] {self.message_item_list}")
        if (len(self.message_item_list) > 0) and (self.message_item_list[0].replace("！", "!").lower() == "!!cht"):
            try:
                command_name = self.message_item_list[1].lower()
            except IndexError:
                await self.httpapi.sendGroupMessage([
                    {"type": "Plain", "text": tF.need_params[self.lang]}
                ])
            else:
                if command_name == "en":
                    self.lang = 1
                    try:
                        command_name = self.message_item_list[2]
                    except IndexError:
                        await self.httpapi.sendGroupMessage([
                            {"type": "Plain",
                                "text": tF.need_params[self.lang]}
                        ])
                    else:
                        if command_name in register_dict:
                            await register_dict[command_name](self)
                        else:
                            await self.httpapi.sendGroupMessage([
                                {"type": "Plain",
                                    "text": tF.command_not_found[self.lang]}
                            ])
                else:
                    if command_name in register_dict:
                        await register_dict[command_name](self)
                    else:
                        await self.httpapi.sendGroupMessage([
                            {"type": "Plain",
                                "text": tF.command_not_found[self.lang]}
                        ])

async def webTasks():
    logging.info("Creating WebSocket connection...")
    session_ws = aiohttp.ClientSession()

    async def wsMessage():
        async with session_ws.ws_connect(f"ws://{host}/message?verifyKey={verifyKey}&sessionKey={sessionKey}&qq={account}") as ws_message:
            logging.info("Connected to WebSocket (Message).")
            while True:
                msg_ws_message = await ws_message.receive()
                if msg_ws_message.type == aiohttp.WSMsgType.TEXT:
                    logging.info(f"[Message Raw] {msg_ws_message.data}")
                    message_raw = ujson.loads(msg_ws_message.data)
                    if ("type" in message_raw["data"]) and (message_raw["data"]["type"] == "GroupMessage"):
                        process_command = ProcessCommand(message_raw)
                        await process_command.processMessage()
                elif msg_ws_message.type == aiohttp.WSMsgType.ERROR:
                    break

    loop.create_task(wsMessage())


@atexit.register
def releaseSessionKey():
    logging.info("Releasing sessionKey...")
    json = {"sessionKey": sessionKey, "qq": account}
    requests.post(f"http://{host}/release", json=json)
    logging.info("Stopped.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="[%(asctime)s] [%(levelname)s] %(message)s")
    loop = asyncio.get_event_loop()
    try:
        init()
        loop.run_until_complete(webTasks())
        loop.run_forever()
    except Exception as ex:
        logging.error(ex)
