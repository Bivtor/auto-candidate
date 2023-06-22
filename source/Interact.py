from dotenv import load_dotenv
import os
import asyncio
from prisma import Prisma
from datetime import datetime


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


async def insert_working_table_item(name: str, parent_id: str, resume_link: str, status: int):
    prisma = Prisma()

    await prisma.connect()

    time = str(datetime.now())
    new_item = await prisma.working_table.create(
        data={
            "name": name,
            "parent_id": parent_id,
            "resume_link": resume_link,
            "date": time,
            "status": status
        }
    )

    return new_item


async def update_status_by_name(name: str, new_status: int):
    prisma = Prisma()

    await prisma.connect()

    item = await prisma.working_table.find_first(where={"name": name})
    if item:
        updated_item = await prisma.working_table.update(
            where={"id": item.id},
            data={"status": new_status}
        )
        return updated_item
    else:
        return None


async def move_working_table_to_history():

    prisma = Prisma()

    await prisma.connect()

    # Retrieve all items from the working_table
    items = await prisma.working_table.find_many()

    if items:
        # Move items to history table
        for item in items:
            await prisma.history.create(
                data={
                    "add_request_id": item.id,
                    "job_destination": item.name,
                    "date": item.date
                }
            )

        # Clear the working_table
        await prisma.working_table.delete_many()

        return True
    else:
        return False


async def getFirstWorking():
    prisma = Prisma()

    await prisma.connect()

    data = await prisma.working_table.find_first()

    await prisma.disconnect()

    return data


async def moveFirstToHistory(status: int):
    prisma = Prisma()

    await prisma.connect()

    # TODO Get info from find_first ( or pass in the info we parsed)
    # data = await prisma.working_table.find_first()

    # TODO Add to History
    # data = await prisma.working_table.find_first()

    # TODO Delete First in Working
    # data = await prisma.working_table.find_first()

    await prisma.disconnect()


def main():
    asyncio.run(run())


if __name__ == '__main__':
    main()
