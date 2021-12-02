# import aioredis
import asyncio

class Redis:
    _redis = None

    async def get_redis_pool(self, *args, **kwargs):
        if not self._redis:
            self._redis = await aioredis.create_redis_pool(*args, **kwargs)
        return self._redis

    async def close(self):
        if self._redis:
            self._redis.close()
            await self._redis.wait_closed()


async def get_value(key):
    redis = Redis()
    r = await redis.get_redis_pool(('127.0.0.1', 6379), db=7, encoding='utf-8')
    value = await r.get(key)
    print(f'{key!r}: {value!r}')
    await redis.close()



import asyncio
from aredis import StrictRedis

async def example():
    client = StrictRedis(host='127.0.0.1', port=6379, db=0)
    await client.flushdb()
    await client.set('foo', 1)
    assert await client.exists('foo') is True
    await client.incr('foo', 100)

    assert int(await client.get('foo')) == 101
    await client.expire('foo', 1)
    await asyncio.sleep(0.1)
    await client.ttl('foo')
    await asyncio.sleep(1)
    assert not await client.exists('foo')

loop = asyncio.get_event_loop()
loop.run_until_complete(example())

if __name__ == '__main__':
    # asyncio.run(get_value('key'))  # need python3.7
    pass