
from telethon import TelegramClient, events, Button, types
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.types import InputNotifyPeer
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
client = TelegramClient('session', api_id, api_hash)

LOG_USER = '@sacoectasy'

async def mute_channel(entity):
    await client(UpdateNotifySettingsRequest(
        peer=InputNotifyPeer(entity),
        settings=types.InputPeerNotifySettings(mute_until=2_147_483_647)
    ))

# Основная логика
async def check_mrkt():
    entity = await client.get_entity('@mrkt')
    async for message in client.iter_messages(entity, limit=10):
        if 'Розыгрыш' in message.message and 'Подпишись на канал' in message.message:
            buttons = message.buttons
            channel_username = None

            for row in buttons:
                for button in row:
                    if button.url and 't.me/' in button.url:
                        channel_username = button.url.split('/')[-1]
                        break

            if channel_username:
                try:
                    channel = await client.get_entity(channel_username)
                    await client(JoinChannelRequest(channel))
                    await mute_channel(channel)
                    await message.click(text='Проверить')
                    now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                    text = f'✅ Участие в розыгрыше!\\nКанал: @{channel_username}\\nВремя: {now}'
                    await client.send_message(LOG_USER, text)
                    with open('log.txt', 'a', encoding='utf-8') as log:
                        log.write(text + '\n')
                except Exception as e:
                    err = f'❌ Ошибка: {e}'
                    await client.send_message(LOG_USER, err)
                    with open('log.txt', 'a', encoding='utf-8') as log:
                        log.write(err + '\n')

@client.on(events.NewMessage(from_users=1667484260))
async def handler(event):
    await check_mrkt()

async def scheduler():
    while True:
        await check_mrkt()
        await asyncio.sleep(300)  # каждые 5 минут

async def main():
    await asyncio.gather(client.start(), scheduler())

with client:
    client.loop.run_until_complete(main())
