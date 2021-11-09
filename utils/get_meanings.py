import json
import asyncio
import aiohttp
import urls
import utils


def get_meanings(words):
    try:
        meanings = []

        async def get(word, session):
            try:
                async with session.get(url=urls.WORDS, params={"search": word}) as response:
                    text = await response.text()
                    data = json.loads(text)
                    if len(data):
                        meanings.append(data[0]["meanings"][0]["id"])
            except Exception:
                pass

        async def main():
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(*[get(word, session) for word in words])

        asyncio.run(main())

        return list(dict.fromkeys(meanings))

    except Exception as e:
        utils.save_to_log(f"Failed to get meanings: {e}")
