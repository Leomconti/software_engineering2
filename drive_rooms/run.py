#!/usr/bin/env python3
from app import init_app

server = init_app()

if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(server, host="localhost", port=8000)
    uvicorn.run(server, host="127.0.0.1", port=8000)
