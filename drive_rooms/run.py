#!/usr/bin/env python3
from app import init_app

server = init_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(server, host="localhost", port=8000)
