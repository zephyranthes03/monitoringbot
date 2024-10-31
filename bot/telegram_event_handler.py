import asyncio
import httpx
import redis.asyncio as aioredis
import os
import threading
import prettytable as pt

import tracemalloc
from datetime import datetime, timedelta
from socket_test import service_check, alive_check
from database.database import Database
from model.service_model import ServiceModel, ServiceDataModel
from telegram import ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, Updater

# 텔레그램 봇 API 토큰과 채팅 ID 설정
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
INTERVAL = 5 * 60

async def send_telegram_message(message):
    """
    텔레그램으로 메시지를 전송하는 비동기 함수
    """
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()  # 요청 오류가 있는 경우 예외 발생
            print(f"Message sent: {message}")
        except httpx.HTTPStatusError as e:
            print(f"Failed to send message: {e}")



async def greet_every_interval():

    event_occurred = True  # 실제 이벤트 조건에 따라 설정
    database = Database()
    # 예시 이벤트 로직
    while True:
        if event_occurred:
            datetime_now = datetime.now()
            services_list = await database.get_services_by_time(datetime_now)
            datetime_now_isoformat = datetime_now.isoformat()
            if services_list is not None:
                for service_item in services_list:
                    # print(service_item['host'], service_item['port'], flush=True)
                    service_check(service_item['host'], service_item['port'])
                    datetime_add_timedelta = datetime_now + timedelta(seconds=service_item['interval'])
                    datetime_add_timedelta_isoformat = datetime_add_timedelta.isoformat()

                    service_model = ServiceDataModel(chat_id=service_item['chat_id'],
                                                host=service_item['host'], port=service_item['port'], 
                                                alias=service_item['alias'],
                                                next_check_time=datetime_now_isoformat,
                                                last_check_time=datetime_add_timedelta_isoformat,
                                                interval=service_item['interval'], status="init" )

                    ### Redis Key?를 시간 tick으로 갈것인지 chat_id로 갈것인지... 고민중...
                    await database.update_service_data(service_model.chat_id, service_model)

        #     # 이벤트 발생 시 텔레그램으로 메시지 전송
        #     await send_telegram_message("An event has occurred!")
        #     event_occurred = False
        # else:
        #     await send_telegram_message("An event has not occurred!")
        await asyncio.sleep(INTERVAL)

async def run_async_tasks():
    """비동기 작업 실행"""
    # 비동기 작업 시작 (greet_every_interval)


    # Get the singleton instance of the AsyncDatabase class
    database = Database()


    # # Initialize connections asynchronously
    await database.initialize_connections()
    await database.inintialzie_service_data()

    asyncio.create_task(greet_every_interval())

    # 다른 비동기 작업도 추가 가능
    # await asyncio.sleep(60)  # 예시로 60초 후 종료

async def main_async(application):
    # 비동기 작업 실행
    await asyncio.create_task(run_async_tasks())

async def start(update: Update, context: CallbackContext) -> None:
    """
    /start 명령어를 처리하는 함수
    """

        # 인사말 메시지
    welcome_message = "안녕하세요! 텔레그램 봇에 오신 것을 환영합니다. 아래에서 옵션을 선택해 주세요:"
    
    # 선택 박스(키보드)
    reply_keyboard = [ ['/start', '/stop'], ['/chat_id', '/list'], ['/add', '/remove']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    # 인사말과 선택 박스를 전송
    await update.message.reply_text(welcome_message, reply_markup=markup)

    # await update.message.reply_text('안녕하세요! 이 봇은 당신의 chat_id를 응답합니다. 아무 메시지나 보내보세요!')

async def chat_id(update: Update, context: CallbackContext) -> None:
    """
    사용자가 메시지를 보낼 때 chat_id를 응답하는 함수
    """
    chat_id = update.message.chat_id
    await update.message.reply_text(f'당신의 chat_id는: {chat_id} 입니다.')

async def stop_bot(update: Update, context: CallbackContext):
    global stop_flag
    stop_flag = True  # 플래그를 True로 설정하여 루프를 종료
    await context.bot.send_message(chat_id=update.effective_chat.id, text="봇을 중지합니다.")


def send_table(table_content:list, update: Updater, context: CallbackContext):
    table = pt.PrettyTable(['Host', 'Port', 'Alias', 'Status', 'Interval'])
    table.align['Host'] = 'c'
    table.align['Port'] = 'r'
    table.align['Alias'] = 'l'
    table.align['Status'] = 'r'
    table.align['Interval'] = 'l'

    for table_dict in table_content:
        table.add_row([table_dict['host'], f'{str(table_dict['port'])}', table_dict['alias'], table_dict['status'], f'{str(table_dict['interval'])}'])
    return table

# 파라미터를 처리하는 명령어 함수
async def list_service(update: Update, context: CallbackContext) -> None:
    # 명령어의 파라미터(인수) 가져오기
    database = Database()

    chat_id = update.message.chat_id
    print(context.args)
    time = INTERVAL

    input_list = await database.get_services_by_chat_id(chat_id)
    output_list = []
    for source in input_list:
        output = source 
        output_list.append(output)

    table_text = send_table(input_list, update, context)
    await update.message.reply_text(f'<pre>{table_text}</pre>', parse_mode=ParseMode.HTML)

    # await update.message.reply_text(f"{str(output_list)}")


# 파라미터를 처리하는 명령어 함수
async def add_service(update: Update, context: CallbackContext) -> None:
    database = Database()
    # 명령어의 파라미터(인수) 가져오기
    chat_id = update.message.chat_id
    print(context.args)
    interval = INTERVAL
    if len(context.args) == 2:
        #name = ' '.join(context.args)  # 여러 파라미터를 하나의 문자열로 연결
        host, port = context.args[0], context.args[1]
        alias = f"{host}/{port}"
    elif len(context.args) == 4:
        host, port, interval, alias = context.args[0], context.args[1], context.args[2], context.args[3]
    elif len(context.args) == 3:
        host, port, interval = context.args[0], context.args[1], context.args[2]
        alias = f"{host}/{port}"
    else:
        await update.message.reply_text("Please provide IP and port after the command, e.g., /add IP [Domain] [port] [interval] (alias).")

    ### check alias
    if await database.get_service_by_chat_id_and_alias(chat_id, alias) is None:
        await update.message.reply_text(f"Added IP={host}, Port={str(port)}, Interval(default=300)={interval}, Alias={alias}")
        service_model = ServiceDataModel(chat_id=chat_id, host=host, port=int(port), interval=int(interval), alias=alias, status='init', next_check_time=datetime.now(), last_check_time=datetime.now())
        await database.insert_service_data(chat_id, service_model)
    else:
        await update.message.reply_text(f"Alias({alias}) already exist. ")



# 파라미터를 처리하는 명령어 함수
async def remove_service(update: Update, context: CallbackContext) -> None:
    # 명령어의 파라미터(인수) 가져오기
    database = Database()

    chat_id = update.message.chat_id
    print(context.args)
    if len(context.args) == 1:
        #name = ' '.join(context.args)  # 여러 파라미터를 하나의 문자열로 연결
        alias = context.args[0]
        await update.message.reply_text(f"Removed, {alias}!")
    if len(context.args) == 2:
        #name = ' '.join(context.args)  # 여러 파라미터를 하나의 문자열로 연결
        host, port = context.args[0], context.args[1]
        await update.message.reply_text(f"Removed, {host} / {port}!")
    else:
        await update.message.reply_text("Please provide host and port after the command, e.g., /remove [Host] [port] or /remove [alias].")

    if len(context.args) >= 2:
        service_model = ServiceDataModel(host=host, port=port, alias=alias)
        await database.remove_service_data(chat_id, service_model)



def database_example():
    # Connect to MongoDB and Redis
    db, collection = connect_to_mongodb()
    redis_client = connect_to_redis()

    # Ensure both connections were successful
    if db and collection and redis_client:
        print("Successfully connected to both MongoDB and Redis.")

        # Example: Insert a sample document into MongoDB
        collection.insert_one({'name': 'John Doe', 'age': 30})
        print("Sample document inserted into MongoDB.")

        # Example: Set a value in Redis
        redis_client.set('sample_key', 'sample_value')
        print("Sample key-value pair set in Redis.")

        # Example: Fetch and print all documents from MongoDB collection
        print("Documents in MongoDB collection:")
        for document in collection.find():
            print(document)

        # Example: Get and print a value from Redis
        value = redis_client.get('sample_key')
        print(f"Value for 'sample_key' in Redis: {value.decode('utf-8')}")


def main():

    tracemalloc.start()

    # # Use the shared MongoDB collection and Redis client
    # collection = database.get_collection
    # redis_client = database.get_redis


    # 애플리케이션 빌더를 사용해 봇 생성
    # print(TELEGRAM_BOT_TOKEN, flush=True)
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # /start 명령어 처리기 등록
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('chat_id', chat_id))
    application.add_handler(CommandHandler('add', add_service))  # /stop 명령어 처리기 추가
    application.add_handler(CommandHandler('remove', remove_service))  # /stop 명령어 처리기 추가
    application.add_handler(CommandHandler('list', list_service))  # /stop 명령어 처리기 추가

    # 모든 텍스트 메시지에 대한 핸들러 등록
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_id))

    # 봇 시작
    # 봇과 비동기 함수 동시 실행

    # # Create and get an adequate asyncio event loop

    # 기본적으로 run_polling은 동기 메서드이므로, 별도의 쓰레드에서 실행
    loop = asyncio.new_event_loop()  # 새 이벤트 루프 생성
    asyncio.set_event_loop(loop)  # 새로운 이벤트 루프 설정

    loop.create_task(main_async(application))  # 비동기 작업을 루프에 추가

    application.run_polling()

    tracemalloc.stop()

    

# 메인 로직
if __name__ == "__main__":
    main()

