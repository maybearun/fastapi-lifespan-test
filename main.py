import aiohttp
import uvicorn
from aiohttp import ClientTimeout
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request


def startup():
    # place all the startup code here like innit and cnx
    print("startup")


def shutdown():
    # place all the shutdown code here like close http sessions
    print("shutdown")


# create a new async context manager
@asynccontextmanager
async def lifespan(app:FastAPI):
    startup()
    yield
    shutdown()


# if we dont want to create a global http client
@asynccontextmanager
async def lifespan(app: FastAPI):
    startup()
    async with aiohttp.ClientSession(
        timeout=ClientTimeout(
            total=60 * 15, connect=60 * 5, sock_read=60 * 5, sock_connect=60 * 5
        )
    ) as client:
        yield {"client":client} # this passes the client to request.state
    shutdown()


app = FastAPI(lifespan=lifespan)

async def get_data(client: aiohttp.ClientSession):
    resp = await client.get("https://www.google.com") 
    print(resp)
    return await resp.text()

@app.get("/")
async def read_root():
    return {"msg": "HelloWorld"}

@app.get("/test")
async def test(req:Request):
    try:
        if hasattr(req.state, "client"): # check if the client is present in the request state
            data = await get_data(req.state.client)
            return {"data": data}
        else:
            raise Exception("Client not found")
    except Exception as e:
        return {"msg": str(e)}
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
