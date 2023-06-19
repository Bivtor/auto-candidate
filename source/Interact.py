from dotenv import load_dotenv
from auto_candidate import ENV_PATH
import os
import asyncio
from prisma import Prisma


load_dotenv(dotenv_path=ENV_PATH)



async def main() -> None:
    prisma = Prisma()
    await prisma.connect()

    # write your queries here
    user = await prisma.user.create(
        data={
            'name': 'Robert',
            'email': 'robert@craigie.dev'
        },
    )

    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
