import asyncio
from telethon import TelegramClient, events, Button
from telethon.errors import FloodWaitError

API_ID = 1234567  # вставь свои
API_HASH = 'abcdef1234567890abcdef1234567890'  # вставь свои
PHONE = '+1234567890'  # твой номер
REPORT_USER = 'sacoectasy'  # юзернейм куда шлем отчеты (без @)

client = TelegramClient('session', API_ID, API_HASH)

async def join_channel(channel_username):
    try:
        await client(JoinChannelRequest(channel_username))
        # Мутим уведомления
        await client.send(
            functions.account.UpdateNotifySettingsRequest(
                peer=channel_username,
                settings=types.InputPeerNotifySettings(mute_until=10**10)
            )
        )
        return True
    except FloodWaitError as e:
        print(f'Flood wait {e.seconds} секунд, ждем...')
        await asyncio.sleep(e.seconds + 5)
        return False
    except Exception as e:
        print(f'Ошибка при подписке на {channel_username}: {e}')
        return False

@client.on(events.NewMessage(chats='@mrkt'))
async def handler(event):
    # Когда приходит новое сообщение в @mrkt, проверяем есть ли там розыгрыш (пример)
    text = event.raw_text.lower()

    if 'розыгрыш' in text or 'подписка' in text:
        # Допустим, мы должны подписаться на канал из кнопки
        buttons = event.buttons
        if buttons:
            for row in buttons:
                for button in row:
                    if isinstance(button, Button.Url):
                        channel_url = button.url
                        # Из url получаем юзернейм канала
                        if 't.me/' in channel_url:
                            channel_username = channel_url.split('t.me/')[1].split('?')[0]
                            result = await join_channel(channel_username)
                            if result:
                                await client.send_message(REPORT_USER,
                                    f'✅ Подписался на канал: {channel_username}')
                            else:
                                await client.send_message(REPORT_USER,
                                    f'❌ Не удалось подписаться на канал: {channel_username}')

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply('Userbot запущен и готов к работе.')

async def main():
    print('Userbot стартует...')
    await client.start(phone=PHONE)
    print('Userbot запущен.')
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
