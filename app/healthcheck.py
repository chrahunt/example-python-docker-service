import aiohttp
import asyncio
import sys


async def main():
    async with aiohttp.ClientSession() as client:
        async with client.get('http://localhost:8080/health') as resp:
            data = await resp.json()
            if data['status'] == 'up':
                return 0
            else:
                return 1


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    sys.exit(loop.run_until_complete(main()))