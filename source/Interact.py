from dotenv import load_dotenv
import os
import asyncio
from prisma import Prisma

load_dotenv(dotenv_path=".env")


async def run() -> None:
    prisma = Prisma()

    await prisma.connect()

    # write your queries here
    query = '''
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public';
    '''
    result = await prisma.query_raw(query)
    tables = [row['table_name'] for row in result]
    print(tables)

    await prisma.disconnect()


def main():
    asyncio.run(run())


if __name__ == '__main__':
    main()
