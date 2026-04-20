import asyncio

async def fetch_weather():
    print("开始查天气")
    await asyncio.sleep(2)
    return "晴天"

async def fetch_news():
    print("开始查新闻")
    await asyncio.sleep(3)
    return "今日头条"

async def main():
    weather, news = await asyncio.gather(
        fetch_weather(),
        fetch_news()
    )
    print(weather)
    print(news)

asyncio.run(main())