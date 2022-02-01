import logging
import ujson
import uvicorn
from typing import Optional
from tinydb import TinyDB, where
from tinydb.operations import add
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from texts import version
from getmcstatus import StatusPing

app = FastAPI(openapi_url=None)
db = TinyDB("christina-db.json", sort_keys=True,
            indent=4, separators=(",", ": "))
logging = logging.getLogger("uvicorn.error")

global config
config = ujson.load(open("config.json"))

global host
global verifyKey
global account
global mcaddrs
host = config["host"]
verifyKey = config["verifyKey"]
account = config["account"]
server_addrs = config["mcaddrs"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_init():
    print("""
    ______ __           __       __   __                   _   __       __                          __
   / ____// /___ _____ /_/_____ / /_ /_/______ ______     / | / /_____ / /_ _      __ ______ _____ / /__
  / /    / __  // ___// //  __// __// // __  // __  /    /  |/ // _  // __/| | /| / // __  // ___// //_/
 / /___ / / / // /   / //__  // /_ / // / / // /_/ /    / /|  //  __// /_  | |/ |/ // /_/ // /   /  <
/_____//_/ /_//_/   /_//____//___//_//_/ /_/ \__/_/    /_/ |_//____//___/  |__/|__//_____//_/   /_//_/
    """)
    logging.info(f"Christina Network v{version}")
    # init_start = time.time()

    # send_json = {"verifyKey": verifyKey}
    # apiresponse = requests.post(f"http://{host}/verify", json=send_json).json()

    # global sessionKey
    # sessionKey = apiresponse["session"]
    # logging.info(f"Get sessionKey: {sessionKey}")
    # send_json = {"sessionKey": sessionKey, "qq": account}
    # requests.post(f"http://{host}/bind", json=send_json)
    # init_done = time.time()
    # logging.info(
    #     f"Mirai initialization done ({round(init_done-init_start, 3)}s)!")


# @app.on_event("shutdown")
# async def shutdown_release():
#     logging.info("Releasing sessionKey...")
#     send_json = {"sessionKey": sessionKey, "qq": account}
#     requests.post(f"http://{host}/release", json=send_json)
#     logging.info("Released.")


@app.get("/")
async def root():
    return RedirectResponse("https://christina.icursors.net/v2")


@app.get("/version")
async def getVersion():
    return {"version": version}


@app.get("/mcstatus")
async def getMCStatus(server_abbr: str):
    try:
        server_addr = server_addrs[server_abbr.lower()]
    except KeyError:
        raise HTTPException(status_code=422, detail="Server does not exist")
    else:
        get_mcstatus = StatusPing(server_addrs[server_abbr])
        try:
            mcstatus_data = get_mcstatus.get_status()
        except Exception:
            raise HTTPException(status_code=502, detail={
                                "text": "Error while getting status", "addr": server_addr})
        else:
            return {
                "addr": server_addr,
                "data": mcstatus_data
            }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",
                port=config["httpapi_port"], log_level="info")
