import pprint
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardRemove, BotCommand, LabeledPrice, PreCheckoutQuery
from aiogram.types.message import ContentType
from config import TOKEN, PAYMENTS_TOKEN
from docxtpl import DocxTemplate
import datetime
import time
from functions import create_doc, context_cntrl, find_court, court_region, court_data_insert, ready_for_render, \
    global_users_dict, global_users_check
import zayava_abz11st23
import zayava_abz3st23
import vydacha_rishennya
from list_courts import COURTS
from list_tck import TCK
import string

bot = Bot(TOKEN)
dp = Dispatcher(bot)
bot_directory = r"E:\Програми\pythonProject1\Bot\Aiogram"

doc_list = [zayava_abz3st23, zayava_abz11st23, vydacha_rishennya]
PRICE = LabeledPrice(label='Документ', amount=20 * 100)

commands_description = """ 
<b>/start</b> - <em>початок роботи</em>
<b>/create</b> - <em>створити документи</em>
<b>/end</b> - <em>завершити</em>"""


# Розділ з допоміжними функціями обробки
def search_for_context(mess_text):
    for i in doc_list:
        if mess_text in i.doc_dict.keys():
            return i


async def doc_generate(message):
    m = doc_name.doc_dict["doc_path"]
    await create_doc(m, context=context)
    inkb = InlineKeyboardMarkup(row_width=1)
    inb1 = InlineKeyboardButton(text="Перейти до нового документу", callback_data="new_doc")
    inkb.add(inb1)
    message1 = await bot.send_message(chat_id=message.chat.id,
                                      text=""" Опрацьовую """)

    time.sleep(3)
    await message1.edit_text(text="Ось Ваш документ")
    url = str(bot_directory + "\zayava" + "_" + context["fio"].split()[0] + ".docx")
    await bot.send_document(chat_id=message.chat.id,
                            document=open(url, "rb"),
                            reply_markup=inkb)

# Розділ з функціями бота

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand("start", "Запустити бота"),
        BotCommand("restart", "Перезапустити бота"),
        BotCommand("choose", "Вибір документа"),
        BotCommand("info", "Умови використання"),
        BotCommand("buy", "Оплата"),
        BotCommand("get_document", "Отримати готовий документ")])


@dp.message_handler(commands=["start"])
async def start_command(message: Message):
    text = """Вітаю! Я допоможу підготувати  
документи швидко і правильно.
З вас інформація, а з мене написання!
Натисність <i>'продовжити'</i> аби почати!"""
    inkb = InlineKeyboardMarkup(row_width=1)
    inb1 = InlineKeyboardButton(text="Продовжити", callback_data="yes")
    inkb.add(inb1)
    await bot.send_message(chat_id=message.chat.id,
                           text=text,
                           reply_markup=inkb,
                           parse_mode="html")
    await message.delete() #видаляє команду старт з переліку повідомлень

""""
@dp.message_handler(commands=["info"])
async def start_command(message: Message):
"   text = "<i>'Запускаючи цей Бот шляхом натискання команди "start" Ви цим надаєте згоду 
на збір, обробку та використання ваших персональних даних для створення документа.
Інформація зберігається на захищеному сервері та розробник Бота не має доступу до неї</i>"
    mess = await bot.send_message(chat_id=message.chat.id,
                           text=text,
                           parse_mode="html")
    time.sleep(6)
    await mess.delete()
"""

@dp.callback_query_handler()
async def next_step(callback: CallbackQuery):
    if callback.data == "yes":
        await choose_command(message=callback.message)
    elif callback.data == "true":
        await get_document(message=callback.message)
    elif callback.data == "new_doc":
        await start_command(message=callback.message)
    elif callback.data == "payment":
        await buy_process(message=callback.message)


@dp.message_handler(commands=["choose"])
async def choose_command(message: Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True,
                             one_time_keyboard=False)
    b_doc1 = KeyboardButton(text="(1)")
    b_doc2 = KeyboardButton(text="(2)")
    b_doc3 = KeyboardButton(text="(3)")
    kb.add(b_doc1, b_doc2, b_doc3)
    await bot.send_message(chat_id=message.chat.id,
                           text=f"""Я можу скласти такі документи:

{"(1)"} {zayava_abz3st23.doc_dict["text_doc"]}

{"(2)"} {zayava_abz11st23.doc_dict["text_doc"]}

{"(3)"} {vydacha_rishennya.doc_dict["text_doc"]}

Для вибору документа натисність його номер...""",
                           reply_markup=kb)
    await message.delete() # видалено "вітаю", я допоможу скласти док....


# основна функція, яка контролює наповнення словника для рендерингу документа
@dp.message_handler(content_types="text")
async def get_info_command(message: Message):
    # вибір шаблону документа з якого будемо брати словники та всю іншу інформацію для наповнення
    global doc_name, s, context
    if message.text in ["(1)", "(2)", "(3)"]:
        doc_name = search_for_context(message.text)
        await bot.send_message(chat_id=message.chat.id,
                               text=doc_name.info,
                               parse_mode="html")
        time.sleep(6)
        await bot.delete_message(chat_id=message.chat.id, message_id=(int(message.message_id) + 1))

    # вибір конкретного словника контекст для заповнення
    context = doc_name.doc_dict["context"]
    print(context)
    time.sleep(1)

    try:
        information = message.text
        # перевірка чи не заходить в хендлер інформація яка не стосується наповнення словника контекст для рендерингу
        if information in ["(1)", "(2)", "(3)"]:
            information = ""

        quest = doc_name.doc_dict["quest"]  # вибір питань, які будуть запитуватись у користувача
        s = context_cntrl(context)  # ключ по якому визначається питання
        context[s] = information    # заповнення словника контекст

        if "reg_tck" in context.keys():
            if context['reg_tck'] != "" and context["tck"] == "":
                kbt = ReplyKeyboardMarkup(resize_keyboard=True,
                                          one_time_keyboard=False)
                tck_in_reg = court_region(information, TCK)
                for i in tck_in_reg:
                    globals()[i.split()[0]] = KeyboardButton(text=str(i))
                    kbt.add(globals()[i.split()[0]])
                await bot.send_message(chat_id=message.chat.id,
                                       text="Оберіть установу із списку", # показується вже після введення області
                                       reply_markup=kbt)

            if context["tck"] != "" and context["adress_tck"] == "":
                context["adress_tck"] = TCK[context["reg_tck"]][information][0]
                context["tel"] = TCK[context["reg_tck"]][information][1]
                time.sleep(1)

        # порядок обрання суду. Обирається через область і функцію court_region Результат - список судів в області.
        if "syd_reg" in context.keys():
            if context['syd_reg'] != "" and context["syd"] == "":

                kbs = ReplyKeyboardMarkup(resize_keyboard=True,
                                          one_time_keyboard=False)
                courts_in_reg = court_region(information, COURTS)
                for i in courts_in_reg:
                    globals()[i.split()[0]] = KeyboardButton(text=str(i))
                    kbs.add(globals()[i.split()[0]])
                await bot.send_message(chat_id=message.chat.id,
                                       text="Оберіть установу із списку",
                                       reply_markup=kbs)

            if context["syd"] != "" and context["adressa_sydy"] == "":
                court_data = find_court(context["syd"], courts=COURTS)
                court_data_insert(instance=court_data[0],
                                  name=court_data[1],
                                  adress=court_data[2],
                                  phone=court_data[3],
                                  email=court_data[4],
                                  context=context)

        if context["fio"] != "" and context["fio_s"] == "":
            pib = context["fio"].split()
            context["fio_s"] = pib[1][0] + "." + pib[2][0] + ". " + pib[0]

        s = context_cntrl(context)
        if s not in ["tck", "syd"]:
            await bot.send_message(chat_id=message.chat.id, text=quest[s]) # тутутутуту


    except BaseException as e:
        print (e)

        if not context_cntrl(context):
            inkb = InlineKeyboardMarkup(row_width=1)
            inb1 = InlineKeyboardButton(text="Продовжити", callback_data="true")
            inkb.add(inb1)
            await bot.send_message(chat_id=message.chat.id,
                                   text="Інформацію зібрав. Час створювати документ",
                                   reply_markup=inkb)

    await bot.delete_message(chat_id=message.chat.id, message_id=(int(message.message_id) - 1)) #видаляє попереднє повідомлення бота
    await message.delete()  #видаляються всі команди, що вводить користувач


# функція яка опрацьовує заповнений словник і потім його рендерить в готовий документ
@dp.message_handler(commands=["get_document"])
async def get_document(message: Message):

    if ready_for_render(context) != False and global_users_check(user_id=message.from_id,
                                                                 users_dict=global_users_dict) == True:
        await doc_generate(message=message)
        context.clear()

    elif global_users_dict[message.from_id] == "False":
        inkop = InlineKeyboardMarkup(row_width=1)
        inb2 = InlineKeyboardButton(text="Отримати реквізити для оплати", callback_data="payment")
        inkop.add(inb2)
        await bot.send_message(chat_id=message.chat.id,
                               text="Ви вже використали безкоштовний документ. Вартість цього документу складатиме 20 грн.",
                               reply_markup=inkop)

        await message.delete()
    else:
        return get_info_command()


@dp.message_handler(commands=['buy'])
async def buy_process(message: Message):
    await bot.send_invoice(message.chat.id,
                           title="Документ",
                           description="Оплата за підготовку юридичного документа",
                           provider_token=PAYMENTS_TOKEN,
                           currency='uah',
                           photo_url="https://cdn.icon-icons.com/icons2/1259/PNG/512/1495815224-jd15_84582.png",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           need_email=False,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter='one-doc-payment',
                           payload='test_some_invoice')


@dp.pre_checkout_query_handler(lambda q: True)
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    payment_info = message.successful_payment.to_python()
    #for k, v in payment_info.items():
    #    print(f"{k} : {v}")

    await bot.send_message(message.chat.id, "Платіж у розмірі '{total_amount} {currency}' успішний!".format(
        total_amount=message.successful_payment.total_amount // 100,
        currency=message.successful_payment.currency))

    if payment_info["total_amount"] == PRICE.amount:

        await doc_generate(message=message)
        context.clear()

"""
@dp.message_handler(commands=["restart"])
async def restart_command(message: Message):
    print(context)
    context.clear()
    print(context)
    text = "Вітаю! Я допоможу підготувати  
документи швидко і правильно.
З вас інформація, а з мене написання!
Натисність <i>'продовжити'</i> аби почати!"
    inkb = InlineKeyboardMarkup(row_width=1)
    inb1 = InlineKeyboardButton(text="Продовжити", callback_data="yes")
    inkb.add(inb1)
    await bot.send_message(chat_id=message.chat.id,
                           text=text,
                           reply_markup=inkb,
                           parse_mode="html")
    await message.delete() #видаляє команду старт з переліку повідомлень
"""

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=set_default_commands)
