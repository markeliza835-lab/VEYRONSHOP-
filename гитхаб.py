import telebot
from telebot import types
import json
import os
import time
from datetime import datetime
import pytz

TOKEN = "8912929129:AAGjUK8TCZ9q9w0z2Vj6U4OEFbqKAgXA7w4"
ADMIN_ID = 8493369954


bot = telebot.TeleBot(TOKEN)


DB_FILE = "veyron.json"



# =========================
# БАЗА
# =========================


def load():

    if os.path.exists(DB_FILE):

        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


    return {

        "users": {},

        "products": {
            "brawl": [],
            "stars": []
        },

        "reviews": [],

        "orders": [],

        "promocodes": {},

        "star_balance": 0

    }



db = load()
promo_temp_target = "all"



if "promocodes" not in db:

    db["promocodes"] = {}

if "star_balance" not in db:

    db["star_balance"] = 0

def save():

    with open(DB_FILE, "w", encoding="utf-8") as f:

        json.dump(
            db,
            f,
            ensure_ascii=False,
            indent=2
        )
# =========================
# МЕНЮ
# =========================


START_PHOTO = "ТВОЙ_FILE_ID_ФОТО"



def menu(uid):

    kb = types.InlineKeyboardMarkup()


    kb.add(
        types.InlineKeyboardButton(
            "🎮 Brawl Stars | Донат",
            callback_data="brawl"
        )
    )


    kb.add(
        types.InlineKeyboardButton(
            "⭐ Telegram Stars",
            callback_data="stars"
        )
    )


    kb.add(
        types.InlineKeyboardButton(
            "💬 Отзывы",
            callback_data="reviews"
        )
    )


    kb.add(
        types.InlineKeyboardButton(
            "🆘 Поддержка",
            callback_data="support"
        )
    )
    kb.add(
        types.InlineKeyboardButton(
            "❓ Частые вопросы",
            callback_data="faq"
    )
)

    kb.add(
        types.InlineKeyboardButton(
            "🦫 VEYRON Points",
            callback_data="points"
        )
    )

    if uid == ADMIN_ID:

        kb.add(
            types.InlineKeyboardButton(
                "⚙️ Админка",
                callback_data="admin"
            )
        )


    return kb




def back_button():

    kb = types.InlineKeyboardMarkup()


    kb.add(
        types.InlineKeyboardButton(
            "🔙 Назад",
            callback_data="back"
        )
    )


    return kb
def smooth_delete(chat_id, message_id):

    try:

        bot.delete_message(

            chat_id,

            message_id

        )

        time.sleep(0.5)

    except:

        pass



def send_main_menu(chat_id, uid):

    msg = bot.send_photo(

        chat_id,

        photo="AgACAgIAAxkBAAIIG2pcoPtpUZI78NvAUg-Ej5t61fOpAAK6G2sbnhLZShiDXP63k6pfAQADAgADeQADPQQ",

        caption="""

🦫 VEYRONSHOP

Добро пожаловать!

🎮 Донат Brawl Stars
⭐ Telegram Stars

Выберите раздел ниже 👇

""",

        reply_markup=menu(uid)

    )


    return msg
# =========================
# START
# =========================


@bot.message_handler(commands=["start"])
def start(message):

    uid = str(message.from_user.id)


    if uid not in db["users"]:

        db["users"][uid] = {

            "name": message.from_user.first_name,

            "date": time.time()

        }

        save()



    msg = send_main_menu(

        message.chat.id,

        message.from_user.id

    )


    db["users"][uid]["menu_id"] = msg.message_id

    save()





# =========================
# ГЛАВНЫЕ КНОПКИ
# =========================


@bot.callback_query_handler(

    func=lambda c: c.data in [

        "brawl",

        "stars",

        "reviews",

        "support",

        "faq"

    ]

)
def buttons(call):


    bot.answer_callback_query(call.id)


    smooth_delete(

    call.message.chat.id,

    call.message.message_id

)



    if call.data == "brawl":

        shop(call, "brawl")



    elif call.data == "stars":

        shop(call, "stars")



    elif call.data == "reviews":

        reviews_menu(call.message)



    elif call.data == "support":

        bot.send_message(

            call.message.chat.id,

            "🆘 Напишите сообщение:",

            reply_markup=back_button()

        )


        bot.register_next_step_handler(

            call.message,

            support_send

        )
    
    elif call.data == "faq":

        faq_menu(call.message)
@bot.callback_query_handler(
    func=lambda c: c.data == "faq_support"
)
def faq_support(call):

    bot.answer_callback_query(call.id)

    smooth_delete(

        call.message.chat.id,

        call.message.message_id

    )

    msg = bot.send_message(

    call.message.chat.id,

    "🆘 Напишите сообщение:",

    reply_markup=back_button()

)
    

    bot.register_next_step_handler(

    msg,

    support_send

)
# =========================
# НАЗАД
# =========================


@bot.callback_query_handler(
    func=lambda c: c.data == "back"
)

def back(call):

    try:

        bot.answer_callback_query(call.id)

    except:

        pass


    bot.clear_step_handler_by_chat_id(

        call.message.chat.id

    )


    try:

        bot.delete_message(

            call.message.chat.id,

            call.message.message_id

        )

    except:

        pass



    send_main_menu(

        call.message.chat.id,

        call.from_user.id

    )





@bot.callback_query_handler(
    func=lambda c: c.data == "back_menu"
)

def back_menu(call):

    bot.answer_callback_query(call.id)


    try:

        bot.delete_message(

            call.message.chat.id,

            call.message.message_id

        )

    except:

        pass



    send_main_menu(

        call.message.chat.id,

        call.from_user.id

    )
# =========================
# МАГАЗИН
# =========================


def shop(call, category):

    message = call.message


    products = db["products"].get(category, [])


    if not products:

        bot.send_message(

            message.chat.id,

            "😔 Товаров пока нет",

            reply_markup=back_button()

        )

        return



    kb = types.InlineKeyboardMarkup()



  



    for i, item in enumerate(products):

        kb.add(

            types.InlineKeyboardButton(

                f"{item['name']} - {item['price']}₽",

                callback_data=f"buy_{category}_{i}"

            )

        )
    kb.add(

        types.InlineKeyboardButton(

            "🔙 Назад",

            callback_data="back_menu"

        )

    )



    bot.send_message(

        message.chat.id,

        "🛒 Выберите нужный товар:",

        reply_markup=kb

    )
# =========================
# ПОКУПКА
# =========================


@bot.callback_query_handler(
    func=lambda c: c.data.startswith("buy_")
)
def buy(call):

    bot.answer_callback_query(call.id)


    try:
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
    except:
        pass


    _, category, index = call.data.split("_")


    product = db["products"][category][int(index)]

    kb = types.InlineKeyboardMarkup()
    if category in ["brawl", "stars"]:

        kb.add(
            types.InlineKeyboardButton(
                "👤 Себе",
                callback_data=f"self_{category}_{index}"
            )
        )


        kb.add(
            types.InlineKeyboardButton(
                "🎁 Другу",
                callback_data=f"friend_{category}_{index}"
            )
        )


    else:

        kb.add(
            types.InlineKeyboardButton(
                "🎟 Ввести промокод",
                callback_data=f"usepromo_{category}_{index}"
            )
        )


        kb.add(
            types.InlineKeyboardButton(
                "❌ Без промокода",
                callback_data=f"nopromo_{category}_{index}"
            )
        )

 
    kb.add(
    types.InlineKeyboardButton(
        "🔙 Назад",
        callback_data="back_menu"
    )
)


    if product.get("photo"):


        msg = bot.send_photo(
            call.message.chat.id,
            product["photo"],

            caption=(

                f"📦 {product['name']}\n"

                f"💰 {product['price']}₽\n\n"

                "Есть промокод?"

            ),

            reply_markup=kb

        )
        db["last_buy_message"] = msg.message_id

        save()

    else:


        bot.send_message(

            call.message.chat.id,

            (

                f"📦 {product['name']}\n"

                f"💰 {product['price']}₽\n\n"

                "Есть промокод?"

            ),

            reply_markup=kb

        )
@bot.callback_query_handler(
    func=lambda c: c.data.startswith("self_")
)
def buy_self(call):

    bot.answer_callback_query(call.id)
    try:

        bot.delete_message(

            call.message.chat.id,

            call.message.message_id

        )

    except:

        pass
    db["receiver"] = "Себе"
    save()
    _, category, index = call.data.split("_")

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "🎟 Ввести промокод",
            callback_data=f"usepromo_{category}_{index}"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "❌ Без промокода",
            callback_data=f"nopromo_{category}_{index}"
        )
    )
    kb.add(
    types.InlineKeyboardButton(
        "🔙 Назад",
        callback_data=f"buy_{category}_{index}"
    )
)
    try:

        bot.edit_message_caption(

            chat_id=call.message.chat.id,

            message_id=db["last_buy_message"],

            caption="👤 Покупка для себя\n\nВыберите оформление:",

            reply_markup=kb

        )

    except:

        bot.send_message(

            call.message.chat.id,

            "👤 Покупка для себя\n\nВыберите оформление:",

            reply_markup=kb

        )
@bot.callback_query_handler(
    func=lambda c: c.data.startswith("friend_")
)
def buy_friend(call):

    bot.answer_callback_query(call.id)
    try:

        bot.delete_message(

            call.message.chat.id,

            call.message.message_id

        )

    except:

        pass

    _, category, index = call.data.split("_")


    bot.send_message(
        call.message.chat.id,
        "🎁 Введите @username друга:"
    )


    bot.register_next_step_handler(
        call.message,
        lambda m: save_friend_receiver(
            m,
            category,
            int(index)
        )
    )
def save_friend_receiver(message, category, index):

    username = message.text.strip()
    db["receiver"] = username
    save()
    

    kb = types.InlineKeyboardMarkup()


    kb.add(
        types.InlineKeyboardButton(
            "🎟 Ввести промокод",
            callback_data=f"usepromo_{category}_{index}"
        )
    )


    kb.add(
	    types.InlineKeyboardButton(
 	       "❌ Без промокода",
	        callback_data=f"nopromo_{category}_{index}"
    )
)
    kb.add(
    types.InlineKeyboardButton(
        "🔙 Назад",
        callback_data=f"buy_{category}_{index}"
    )
)

    bot.send_message(
        message.chat.id,
        f"🎁 Покупка для друга\n\n"
        f"👤 Получатель: {username}",
        reply_markup=kb
    )

# =========================
# ЗАКАЗ БЕЗ ПРОМОКОДА
# =========================


@bot.callback_query_handler(
    func=lambda c: c.data.startswith("nopromo_")
)
def no_promo(call):

    bot.answer_callback_query(call.id)

    try:

        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )

    except:

        pass


    _, category, index = call.data.split("_")


    product = db["products"][category][int(index)]


    receiver = db.pop(
        "receiver",
        "Себе"
    )


    start_payment(
        call.message.chat.id,
        call.from_user.id,
        call.from_user.username,
        category,
        int(index),
        product,
        receiver,
        product["price"],
        None
    )
# =========================
# ПРОМОКОД ПРИ ПОКУПКЕ
# =========================


@bot.callback_query_handler(
    func=lambda c: c.data.startswith("usepromo_")
)
def enter_promo(call):

    bot.answer_callback_query(call.id)

    try:

        bot.delete_message(

            call.message.chat.id,

            call.message.message_id

        )

    except:

        pass

    _, category, index = call.data.split("_")

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "🔙 Назад",
            callback_data="back_menu"
        )
    )

    msg = bot.send_message(
        call.message.chat.id,
        "🎟 Введите промокод:",
        reply_markup=kb
)

    bot.register_next_step_handler(

        call.message,

        lambda m: check_promo_after_buy(

            m,

            category,

            index,

            call.message.message_id

        )

    )


def check_promo_after_buy(message, category, index, old_message_id):
    
    if isinstance(index, str) and index.isdigit():
        index = int(index)

    code = message.text.replace(" ", "").replace("\n", "").upper()
    try:

        bot.delete_message(

            message.chat.id,

            message.message_id - 1

        )

    except:

        pass

    if code not in db["promocodes"]:

        bot.send_message(

            message.chat.id,

            "❌ Такого промокода нет"

        )

        return



    promo = db["promocodes"][code]


    if promo.get("date"):

        moscow = pytz.timezone("Europe/Moscow")

        now = datetime.now(moscow)

        end_datetime = datetime.strptime(

            promo["date"] + " " + promo["time"],

            "%d.%m.%Y %H:%M"

        )

        end_datetime = moscow.localize(end_datetime)


        if now > end_datetime:

            bot.send_message(

                message.chat.id,

                "❌ Срок действия промокода истёк"

            )

            return



    


      
    if promo.get("limit") is not None and promo["uses"] >= promo["limit"]:

        bot.send_message(

            message.chat.id,

            "❌ Промокод закончился",

            reply_markup=back_button()

        )

        return


    target = promo.get("target", "all")

    print("PROMO TARGET:", target)
    print("BUY CATEGORY:", category)
    print("BUY INDEX:", index)

    if target != "all":

        if target["type"] == "category":

            if target["value"] != category:

                bot.send_message(
                    message.chat.id,
                    "❌ Промокод действует на другую категорию",
                    reply_markup=back_button()
                )

                return


        elif target["type"] == "product":

            if (
                target["category"] != category
                or target["index"] != index
            ):

                bot.send_message(
                    message.chat.id,
                    "❌ Промокод действует на другой товар",
                    reply_markup=back_button()
                )

                return


        elif target["type"] == "products":

            found = False

            for item in target["items"]:

                if (
                    item["category"] == category
                    and item["index"] == index
                ):
                    found = True
                    break


            if not found:

                bot.send_message(
                    message.chat.id,
                    "❌ Промокод действует на другой товар",
                    reply_markup=back_button()
                )

                return
    



    product = db["products"][category][index]


    discount = promo["discount"]


    price = product["price"]


    final_price = price - (price * discount // 100)



    promo["uses"] += 1
    save()

    start_payment(
        message.chat.id,
        message.from_user.id,
        message.from_user.username,
        category,
        index,
        product,
        db.get("receiver", "Себе"),
        final_price,
        code
    )


# =========================
# ЧАСТЫЕ ВОПРОСЫ
# =========================


def faq_menu(message):

    kb = types.InlineKeyboardMarkup()


    kb.add(
        types.InlineKeyboardButton(
            "💬 Уточнить у администрации",
            callback_data="faq_support"
        )
    )


    kb.add(
        types.InlineKeyboardButton(
            "🔙 Назад",
            callback_data="back_menu"
        )
    )


    bot.send_message(

        message.chat.id,

        """
❓ Частые вопросы VEYRONSHOP


⭐ Telegram Stars

⚡ Моментальная выдача?

Да!
Telegram Stars выдаются моментально.
Обычно это занимает до 1 минуты.


💸 Почему у вас такой дешёвый донат?

Мы используем специальные регионы,
где стоимость доната ниже.

Благодаря этому можем предлагать
выгодные цены для наших клиентов.


🎮 Что нужно для покупки Brawl Stars доната?

Для покупки доната Brawl Stars необходимо,
чтобы регион аккаунта был установлен "США" 🇺🇸

Это нужно для корректного проведения покупки.


🛡 После покупки доната с моим аккаунтом что-то будет?

Нет.
Купленный ваш аккаунт в полной безопасности

⚠️ Возможен откат аккаунта.
Вероятность 2%.

Откат — это не удаление доната.
Ваш купленный донат остаётся.


💬 Как узнать, что ваши отзывы настоящие?

Вы можете прямо сейчас оставить свой отзыв.

После публикации он отобразится
для всех пользователей магазина.


↩️ Можно ли вернуть деньги после покупки?

Нет.
После выполнения заказа возврат денежных средств
не производится.

Перед покупкой внимательно проверяйте
товар и данные получателя.


🦫 Что такое VEYRON Points?

VEYRON Points — это наша внутренняя
бонусная система.

После покупки вы получаете 1% от суммы заказа
в виде VEYRON Points.

Пример:

Вы купили на 5000₽ —
получаете 50 VEYRON Points.

Их можно использовать,
чтобы сэкономить на следующей покупке.


⏳ Сгорают ли VEYRON Points?

Да.

VEYRON Points сгорают через 1 месяц
после получения.
""",

        reply_markup=kb

    )

# =========================
# ОТЗЫВЫ
# =========================



def reviews_menu(message):

    kb = types.InlineKeyboardMarkup()



    kb.add(

        types.InlineKeyboardButton(

            "✍️ Написать отзыв",

            callback_data="write_review"

        )

    )



    kb.add(

        types.InlineKeyboardButton(

            "👀 Смотреть отзывы",

            callback_data="show_reviews"

        )

    )



    kb.add(

        types.InlineKeyboardButton(

            "🔙 Назад",

            callback_data="back_menu"

        )

    )



    bot.send_message(

        message.chat.id,

        "💬 Отзывы VEYRONSHOP:",

        reply_markup=kb

    )



@bot.callback_query_handler(

    func=lambda c: c.data == "write_review"

)

def write_review(call):

    bot.answer_callback_query(call.id)



    bot.delete_message(

        call.message.chat.id,

        call.message.message_id

    )



    kb = types.InlineKeyboardMarkup()

    for i in range(5, 0, -1):

        kb.add(
            types.InlineKeyboardButton(
                f"⭐ {i}",
                callback_data=f"rating_{i}"
            )
        )


    kb.add(
        types.InlineKeyboardButton(
            "🔙 Назад",
            callback_data="back"
        )
    )


    bot.send_message(
        call.message.chat.id,
        "⭐ Оцените магазин:",
        reply_markup=kb
    )



@bot.callback_query_handler(

    func=lambda c: c.data.startswith("rating_")

)
def rating_select(call):
    if not call.data.startswith("rating_"):
        return
    bot.answer_callback_query(call.id)


    smooth_delete(

        call.message.chat.id,

        call.message.message_id

    )


    rating = int(call.data.replace("rating_", ""))


    msg = bot.send_message(

        call.message.chat.id,

        "✍️ Напишите текст отзыва:"

    )


    bot.register_next_step_handler(

        msg,

        lambda m: save_review(m, rating)

    )


def save_review(message, rating):

    


    try:

        smooth_delete(

            message.chat.id,

            message.message_id - 1

        )

    except:

        pass

    db["reviews"].append(

        {

            "user": message.from_user.first_name,

            "text": message.text,

            "rating": int(rating)

        }

    )


    save()

    try:

        bot.send_message(

            message.chat.id,

            "✅ Спасибо за отзыв!",

            reply_markup=back_button()

        )



    except Exception as e:

        print("ОШИБКА ОТПРАВКИ:", e)  
    
def show_reviews(call):

    bot.answer_callback_query(call.id)

    smooth_delete(

        call.message.chat.id,

        call.message.message_id

    )

    if not db["reviews"]:

        bot.send_message(

            call.message.chat.id,

            "💬 Отзывов пока нет",

            reply_markup=back_button()

        )

        return


    text = "\u2003💬 Отзывы:\n\n"

    ratings = [
        r["rating"]
        for r in db["reviews"]
        if "rating" in r
    ]

    if ratings:

        average = sum(ratings) / len(ratings)

        text += f"⭐ Средняя оценка: {average:.1f}/5\n\n"

    print("ПОКАЗ:", db["reviews"][-10:])

    for r in db["reviews"][-10:]:

        text += (

            f"👤 {r['user']}\n"

            f"⭐ Оценка: {'⭐' * r.get('rating', 0)} ({r.get('rating', 0)}/5)\n"

            f"💬 {r['text']}\n"

            "────────\n\n"

        )



    bot.delete_message(

        call.message.chat.id,

        call.message.message_id

    )



    bot.send_message(

        call.message.chat.id,

        text,

        reply_markup=back_button()

    )



# =========================
# ПОДДЕРЖКА
# =========================



def support_send(message):

    try:

        smooth_delete(

            message.chat.id,

            message.message_id - 1

        )

    except:

        pass

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "💬 Ответить",
            callback_data=f"reply_{message.from_user.id}"
        )
    )


    bot.send_message(

        ADMIN_ID,

        f"""
🆘 Поддержка

👤 Пользователь:
{message.from_user.id}

💬 Сообщение:
{message.text}
""",

        reply_markup=kb

    )


    bot.send_message(

        message.chat.id,

        "✅ Сообщение отправлено",

        reply_markup=back_button()

    )
# =========================
# АДМИНКА
# =========================


def admin_panel(message):

    kb = types.InlineKeyboardMarkup()


    kb.add(
        types.InlineKeyboardButton(
            "👥 Пользователи",
            callback_data="admin_users"
        )
    )


    kb.add(
        types.InlineKeyboardButton(
            "➕ Добавить товар",
            callback_data="admin_add"
        )
    )

    kb.add(
    types.InlineKeyboardButton(
        "🗑 Очистить заказы",
        callback_data="clear_orders"
    )
)

    kb.add(
        types.InlineKeyboardButton(
            "📦 Заказы",
            callback_data="admin_orders"
        )
    )


    kb.add(
        types.InlineKeyboardButton(
            "🎟 Создать промокод",
            callback_data="admin_promo"
        )
    )
    kb.add(
    types.InlineKeyboardButton(
        "📋 Список промокодов",
        callback_data="admin_promos"
    )
)
    kb.add(
    types.InlineKeyboardButton(
        "📢 Рассылка",
        callback_data="admin_mailing"
    )
)
    kb.add(
        types.InlineKeyboardButton(
            "📦 Управление товарами",
            callback_data="admin_products"
        )
    )

    kb.add(
    types.InlineKeyboardButton(
        "💬 Управление отзывами",
        callback_data="admin_reviews"
    )
)
    kb.add(
        types.InlineKeyboardButton(
            "💰 Пополнить звёзды",
            callback_data="admin_topup_stars"
        )
    )
    kb.add(
        types.InlineKeyboardButton(
            "🔙 Назад",
            callback_data="back_menu"
        )
    )


    bot.send_message(

        message.chat.id,

        f"⚙️ VEYRONSHOP ADMIN\n\n💰 Баланс звёзд: {db['star_balance']}⭐",

        reply_markup=kb

    )


@bot.callback_query_handler(
    func=lambda c: c.data == "admin" 
    or c.data.startswith("admin_") 
    or c.data.startswith("promo_")
    or c.data.startswith("target_")
    or c.data.startswith("category_")
    or c.data.startswith("products_")
    or c.data.startswith("product_")
    or c.data.startswith("add_more_product")
    or c.data == "finish_products"
    or c.data == "promo_limit_products"
    or c.data == "promo_time_products"
    or c.data == "test_finish"
    or c.data == "test_limit_products"
    or c.data == "promo_limit_all"
    or c.data == "promo_time_all"
    or c.data == "test_time"

)

def admin_buttons(call):

    global promo_temp_target
    
    if call.from_user.id != ADMIN_ID:

        return
        print("CALLBACK:", call.data)

    bot.answer_callback_query(call.id)

    print("CALL:", call.data)

    if call.data == "admin":

        admin_panel(call.message)

        return



    elif call.data == "admin_users":


        bot.send_message(

            call.message.chat.id,

            f"👥 Пользователей: {len(db['users'])}",

            reply_markup=back_button()

        )



    elif call.data == "admin_add":


        bot.send_message(

            call.message.chat.id,

            """
➕ Добавление товара

Формат:

категория-название-цена

Пример:

brawl-170 гемов Brawl Stars-299
""",

            reply_markup=back_button()

        )


        bot.register_next_step_handler(

            call.message,

            add_product

        )



    elif call.data == "admin_orders":


        if not db["orders"]:

            bot.send_message(

                call.message.chat.id,

                "📦 Заказов пока нет",

                reply_markup=back_button()

            )

            return


        text = "📦 Заказы:\n\n"


        for order in db["orders"][-10:]:

            text += (

                f"👤 Покупатель: {order['user']}\n"
                f"🎁 Получатель: {order.get('receiver', 'Себе')}\n"

                f"📦 {order['product']}\n"

                f"💰 {order['price']}₽\n"

                "────────\n"

            )


        bot.send_message(

            call.message.chat.id,

            text,

            reply_markup=back_button()

        )
    elif call.data == "admin_mailing":

        bot.send_message(

            call.message.chat.id,

            """
📢 Рассылка

Отправьте сообщение, которое получат все пользователи.
""",

            reply_markup=back_button()

        )


        bot.register_next_step_handler(

            call.message,

            mailing

        )
    elif call.data == "admin_topup_stars":

        bot.send_message(
            call.message.chat.id,
            "💰 Введите количество звёзд для пополнения баланса бота:",
            reply_markup=back_button()
        )

        bot.register_next_step_handler(
            call.message,
            topup_stars_amount
        )
    elif call.data == "admin_promo":

        kb = types.InlineKeyboardMarkup()


        kb.add(

            types.InlineKeyboardButton(

                "🌍 Весь магазин",

                callback_data="target_all"

            )

        )


        kb.add(

            types.InlineKeyboardButton(

                "📂 Категория",

                callback_data="target_category"

            )

        )


        kb.add(

            types.InlineKeyboardButton(

                "📦 Товары",

                callback_data="target_products"

            )

        )


        bot.send_message(

            call.message.chat.id,

            """
🎟 Создание промокода

🎯 Выберите на что действует:
""",

            reply_markup=kb

        )
    elif call.data == "promo_limit":

        bot.send_message(
            call.message.chat.id,

            """
🔢 Промокод с лимитом активаций

Формат:

КОД|СКИДКА|КОЛИЧЕСТВО


Пример:

VEYRON10|10|5
""",

            reply_markup=back_button()
        )


        bot.register_next_step_handler(
            call.message,
            create_promo
        )
    elif call.data == "test_limit_products":

        bot.send_message(

            call.message.chat.id,

            """
🔢 Промокод с лимитом активаций

Формат:

КОД|СКИДКА|КОЛИЧЕСТВО


Пример:

BRAWL10|10|5
"""

        )


        bot.register_next_step_handler(

            call.message,

            lambda m: create_promo(

                m,

                promo_temp_target

            )

        )


        return

    elif call.data == "promo_limit_all":

        print("PROMO LIMIT ALL CLICK")

        bot.send_message(

            call.message.chat.id,

            """
🔢 Промокод с лимитом активаций

Формат:

КОД|СКИДКА|ЛИМИТ


Пример:

VEYRON10|10|5
"""

        )


        bot.register_next_step_handler(

            call.message,

            create_promo

        )


        return

    elif call.data == "promo_time_all":

        bot.send_message(

            call.message.chat.id,

            """
⏳ Промокод со сроком действия

Формат:

КОД|СКИДКА|ДАТА|ВРЕМЯ


Пример:

VEYRON10|10|27.05.2026|15:12
"""

        )


        bot.register_next_step_handler(

            call.message,

            lambda m: create_promo_time(

                m,

                promo_temp_target

            )

        )


        return
    elif call.data == "test_time":

        bot.send_message(

            call.message.chat.id,

            """
⏳ Промокод со сроком действия

Формат:

КОД|СКИДКА|ДАТА|ВРЕМЯ

Пример:

VEYRON10|10|27.05.2026|15:12
"""

        )



        bot.register_next_step_handler(

            call.message,

            lambda m: create_promo_time(

                m,

                promo_temp_target

            )

        )


        return

    elif call.data == "promo_time":

        bot.send_message(
            call.message.chat.id,

            """
⏳ Промокод со сроком действия

Формат:

КОД|СКИДКА|ДАТА|ВРЕМЯ

Пример:

VEYRON10|10|27.05.2026|15:12
""",

            reply_markup=back_button()
        )


        bot.register_next_step_handler(
            call.message,
            create_promo_time
        )
    elif call.data == "promo_target":

        kb = types.InlineKeyboardMarkup()

        kb.add(
            types.InlineKeyboardButton(
                "🌍 Весь магазин",
                callback_data="target_all"
            )
        )

        kb.add(
            types.InlineKeyboardButton(
                "📂 Категория",
                callback_data="target_category"
            )
        )

        kb.add(
            types.InlineKeyboardButton(
                "📦 Товары",
                callback_data="target_products"
            )
        )

        bot.send_message(
            call.message.chat.id,
            "🎯 На что действует промокод?",
            reply_markup=kb
        )

    elif call.data == "target_all":

        print("TARGET ALL CLICK")


        promo_temp_target = "all"


        kb = types.InlineKeyboardMarkup()


        kb.add(

            types.InlineKeyboardButton(

                "🔢 Лимит активаций",

                callback_data="promo_limit_all"

            )

        )


        kb.add(

            types.InlineKeyboardButton(

                "⏳ Срок действия",

                callback_data="promo_time_all"

            )

        )


        bot.send_message(

            call.message.chat.id,

            """
🌍 Промокод на весь магазин выбран.

Выберите ограничение:
""",

            reply_markup=kb

        )


        return


    elif call.data == "target_category":

        kb = types.InlineKeyboardMarkup()


        kb.add(
            types.InlineKeyboardButton(
                "🎮 Brawl Stars",
                callback_data="category_brawl"
            )
        )


        kb.add(
            types.InlineKeyboardButton(
                "⭐ Telegram Stars",
                callback_data="category_stars"
            )
        )


        bot.send_message(

            call.message.chat.id,

            "📂 Выберите категорию:",

            reply_markup=kb

        )
    elif call.data == "target_products":

        kb = types.InlineKeyboardMarkup()


        kb.add(
            types.InlineKeyboardButton(
                "🎮 Brawl Stars",
                callback_data="products_brawl"
            )
        )


        kb.add(
            types.InlineKeyboardButton(
                "⭐ Telegram Stars",
                callback_data="products_stars"
            )
        )


        bot.send_message(

            call.message.chat.id,

            "📦 Выберите категорию товара:",

            reply_markup=kb

        )
        return        



    elif call.data == "products_brawl":

        kb = types.InlineKeyboardMarkup()


        for i, product in enumerate(db["products"]["brawl"]):

            kb.add(

                types.InlineKeyboardButton(

                    product["name"],

                    callback_data=f"product_brawl_{i}"

                )

            )


        bot.send_message(

            call.message.chat.id,

            "🎮 Выберите товар Brawl Stars:",

            reply_markup=kb

        )

    elif call.data == "products_stars":

        kb = types.InlineKeyboardMarkup()


        for i, product in enumerate(db["products"]["stars"]):

            kb.add(
                types.InlineKeyboardButton(
                    product["name"],
                    callback_data=f"product_stars_{i}"
                )
            )


        bot.send_message(

            call.message.chat.id,

            "⭐ Выберите товар Telegram Stars:",

            reply_markup=kb

        )


    elif call.data == "category_brawl":

        promo_temp_target = {
            "type": "category",
            "value": "brawl"
        }

        kb = types.InlineKeyboardMarkup()

        kb.add(
            types.InlineKeyboardButton(
                "🔢 Лимит активаций",
                callback_data="test_limit_products"
            )
        )

        kb.add(
            types.InlineKeyboardButton(
                "⏳ Срок действия",
                callback_data="test_time"
            )
        )

        bot.send_message(
            call.message.chat.id,
            """
🎮 Категория Brawl Stars выбрана.

Выберите ограничение:
""",
            reply_markup=kb
        ) 

        
    elif call.data.startswith("product_brawl_"):

        index = int(call.data.replace("product_brawl_", ""))


        if not isinstance(promo_temp_target, dict) or promo_temp_target.get("type") != "products":

            promo_temp_target = {

                "type": "products",

                "items": []

            }




        kb = types.InlineKeyboardMarkup()
        if not any(

            item["category"] == "brawl"

            and item["index"] == index

            for item in promo_temp_target["items"]

        ):

            promo_temp_target["items"].append(

                {

                    "category": "brawl",

                    "index": index

                }

            )


        print("BRAWL TARGET:", promo_temp_target)

        kb.add(

            types.InlineKeyboardButton(

                "➕ Добавить ещё товар",

                callback_data="add_more_product_brawl"

            )

        )


        kb.add(

            types.InlineKeyboardButton(
                     "✅ Готово",
                    callback_data="finish_products"


            )

        )


        bot.send_message(

            call.message.chat.id,

            """
🎮 Товар Brawl Stars выбран.

Выберите действие:

➕ Добавить ещё товар
✅ Готово
""",

            reply_markup=kb

        ) 
        
    elif call.data.startswith("product_stars_"):

        index = int(call.data.replace("product_stars_", ""))

        if not isinstance(promo_temp_target, dict) or promo_temp_target.get("type") != "products":

            promo_temp_target = {

                "type": "products",

                "items": []

            }

        if not any(

            item["category"] == "stars"

            and item["index"] == index

            for item in promo_temp_target["items"]

        ):

            promo_temp_target["items"].append(

                {

                    "category": "stars",

                    "index": index

                }

            )

        kb = types.InlineKeyboardMarkup()


        kb.add(

            types.InlineKeyboardButton(

                "➕ Добавить ещё товар",

                callback_data="add_more_product_stars"

            )

        )


        kb.add(

            types.InlineKeyboardButton(

                "✅ Готово",

                callback_data="finish_products"

            )

        )

        bot.send_message(

            call.message.chat.id,

            """
⭐ Товар Telegram Stars выбран.

Выберите действие:

➕ Добавить ещё товар
✅ Готово
""",

            reply_markup=kb

        )





    elif call.data == "add_more_product_brawl":

        kb = types.InlineKeyboardMarkup()


        for i, product in enumerate(db["products"]["brawl"]):

            kb.add(

                types.InlineKeyboardButton(

                    product["name"],

                    callback_data=f"product_brawl_{i}"

                )

            )


        bot.send_message(

            call.message.chat.id,

            "➕ Выберите ещё один товар Brawl Stars:",

            reply_markup=kb

        )


    elif call.data == "add_more_product_stars":

        kb = types.InlineKeyboardMarkup()


        for i, product in enumerate(db["products"]["stars"]):

            kb.add(

                types.InlineKeyboardButton(

                    product["name"],

                    callback_data=f"product_stars_{i}"

                )

            )


        bot.send_message(

            call.message.chat.id,

            "➕ Выберите ещё один товар Telegram Stars:",

            reply_markup=kb

        )

    elif call.data == "finish_products":

        if not isinstance(promo_temp_target, dict) or promo_temp_target.get("type") != "products":

            bot.send_message(

                call.message.chat.id,

                "❌ Товары не выбраны."

            )

            return


        kb = types.InlineKeyboardMarkup()


        kb.add(

            types.InlineKeyboardButton(

                "🔢 Лимит активаций",

                callback_data="test_limit_products"

            )

        )


        kb.add(

  		  types.InlineKeyboardButton(

	        "⏳ Срок действия",

      	  callback_data="test_time"

    )

)

        for row in kb.keyboard:

            for btn in row:

                print("BUTTON:", btn.text, btn.callback_data)


        bot.send_message(

            call.message.chat.id,

            """
🎟 Товары выбраны.

Выберите ограничение:
""",

            reply_markup=kb

        )

        return



    elif call.data == "category_stars":

        promo_temp_target = {
            "type": "category",
            "value": "stars"
        }

        kb = types.InlineKeyboardMarkup()

        kb.add(
            types.InlineKeyboardButton(
                "🔢 Лимит активаций",
                callback_data="test_limit_products"
            )
        )

        kb.add(
            types.InlineKeyboardButton(
                "⏳ Срок действия",
                callback_data="test_time"
            )
        )

        bot.send_message(
            call.message.chat.id,
            """
⭐ Категория Telegram Stars выбрана.

Выберите ограничение:
""",
            reply_markup=kb
        )


# =========================
# АДМИНКА — ТОВАРЫ
# =========================
    elif call.data == "promo_limit":

        bot.send_message(

            call.message.chat.id,

            """
🔢 Промокод с лимитом активаций

Формат:

КОД|СКИДКА|КОЛИЧЕСТВО


Пример:

VEYRON10|10|5
""",

            reply_markup=back_button()

        )


        bot.register_next_step_handler(

            call.message,

            create_promo

        )
    elif call.data == "promo_limit":

        bot.send_message(
            call.message.chat.id,

            """
🔢 Промокод с лимитом активаций

Формат:

КОД|СКИДКА|КОЛИЧЕСТВО


Пример:

VEYRON10|10|5
""",

            reply_markup=back_button()
        )


        bot.register_next_step_handler(
            call.message,
            create_promo
        )
    elif call.data == "admin_products":


        kb = types.InlineKeyboardMarkup()


        for category in db["products"]:

            for i, product in enumerate(
                db["products"][category]
            ):

                kb.add(

                    types.InlineKeyboardButton(

                        f"{product['name']} | {product['price']}₽",

                        callback_data=f"manage_{category}_{i}"

                    )

                )


        if not kb.keyboard:


            bot.send_message(

                call.message.chat.id,

                "📦 Товаров нет",

                reply_markup=back_button()

            )


            return



        bot.send_message(

            call.message.chat.id,

            "📦 Выберите товар для управления:",

            reply_markup=kb

        )



   

    elif call.data == "admin_promos":

        if not db["promocodes"]:

            bot.send_message(
                call.message.chat.id,
                "🎟 Промокодов пока нет",
                reply_markup=back_button()
            )

            return


        text = "📋 Список промокодов:\n\n"

        kb = types.InlineKeyboardMarkup()


        for code, promo in db["promocodes"].items():

            text += (
                f"🎟 {code}\n"
                f"🔥 Скидка: {promo['discount']}%\n"
                f"📊 Использовано: {promo['uses']}/{promo['limit']}\n"
                "────────\n"
            )


            kb.add(
                types.InlineKeyboardButton(
                    f"🗑 Удалить {code}",
                    callback_data=f"delpromo_{code}"
                )
            )


        kb.add(
            types.InlineKeyboardButton(
                "🔙 Назад",
                callback_data="back_menu"
            )
        )


        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=kb
        )
    elif call.data == "admin_reviews":

        if not db["reviews"]:

            bot.send_message(
                call.message.chat.id,
                "💬 Отзывов пока нет",
                reply_markup=back_button()
            )

            return


        kb = types.InlineKeyboardMarkup()


        for i, review in enumerate(db["reviews"]):

            kb.add(
                types.InlineKeyboardButton(
                    f"⭐ {i+1}. {review['text'][:20]}...",
                    callback_data=f"delreview_{i}"
                )
            )


        kb.add(
            types.InlineKeyboardButton(
                "🔙 Назад",
                callback_data="back_menu"
            )
        )


        bot.send_message(
            call.message.chat.id,
            "💬 Выберите отзыв для удаления:",
            reply_markup=kb
        )
# =========================
# УПРАВЛЕНИЕ ТОВАРОМ
# =========================



@bot.callback_query_handler(

    func=lambda c: c.data.startswith("manage_")

)

def manage_product(call):


    _, category, index = call.data.split("_")


    index = int(index)



    kb = types.InlineKeyboardMarkup()



    kb.add(

        types.InlineKeyboardButton(

            "✏️ Изменить",

            callback_data=f"edit_{category}_{index}"

        )

    )



    kb.add(

        types.InlineKeyboardButton(

            "🗑 Удалить",

            callback_data=f"delete_{category}_{index}"

        )

    )



    kb.add(

        types.InlineKeyboardButton(

            "🔙 Назад",

            callback_data="admin_products"

        )

    )



    bot.send_message(

        call.message.chat.id,

        "⚙️ Управление товаром:",

        reply_markup=kb

    )
# =========================
# УДАЛЕНИЕ ТОВАРА
# =========================


@bot.callback_query_handler(

    func=lambda c: c.data.startswith("delete_")

)

def delete_product(call):

    bot.answer_callback_query(call.id)


    _, category, index = call.data.split("_")


    index = int(index)

    if index >= len(db["products"][category]):

        bot.send_message(
            call.message.chat.id,
            "❌ Товар уже удалён или не найден",
            reply_markup=back_button()
        )

        return


    product = db["products"][category].pop(index)


    bot.send_message(

        call.message.chat.id,

        f"🗑 Товар удалён:\n\n"
        f"📦 {product['name']}",

        reply_markup=back_button()

    )


@bot.callback_query_handler(
    func=lambda c: c.data.startswith("delreview_")
)
def delete_review(call):

    bot.answer_callback_query(call.id)

    index = int(
        call.data.split("_")[1]
    )

    if index < len(db["reviews"]):

        review = db["reviews"].pop(index)

        save()

        bot.send_message(
            call.message.chat.id,
            f"🗑 Отзыв удалён:\n\n"
            f"👤 {review['user']}\n"
            f"⭐ {review['text']}",
            reply_markup=back_button()
        )

    else:

        bot.send_message(
            call.message.chat.id,
            "❌ Отзыв не найден",
            reply_markup=back_button()
        )





# =========================
# ИЗМЕНЕНИЕ ТОВАРА
# =========================



@bot.callback_query_handler(

    func=lambda c: c.data.startswith("edit_")

)

def edit_product(call):

    bot.answer_callback_query(call.id)


    _, category, index = call.data.split("_")



    bot.send_message(

        call.message.chat.id,

        """
✏️ Изменение товара

Формат:

название|цена


Пример:

170 гемов Brawl Stars|299
""",

        reply_markup=back_button()

    )



    bot.register_next_step_handler(

        call.message,

        lambda m: save_edit(

            m,

            category,

            int(index)

        )

    )





def save_edit(message, category, index):

    try:


        name, price = message.text.split("|")



        db["products"][category][index]["name"] = name


        db["products"][category][index]["price"] = int(price)



        save()



        bot.send_message(

            message.chat.id,

            "✅ Товар изменён",

            reply_markup=back_button()

        )


    except:


        bot.send_message(

            message.chat.id,

            "❌ Неверный формат\n\nПример:\n"
            "⭐ Telegram Stars 100|150",

            reply_markup=back_button()

        )
# =========================
# ДОБАВЛЕНИЕ ТОВАРА
# =========================


def add_product(message):

    try:


        category, name, price = message.text.split("-")



        if category not in db["products"]:


            bot.send_message(

                message.chat.id,

                "❌ Такой категории нет\n\n"
                "Используйте: brawl или stars",

                reply_markup=back_button()

            )

            return




        db["products"][category].append({

  		  "name": name,

		    "price": int(price),

		    "photo": "AgACAgIAAxkBAAIblWppzEj2mU2MhaEUdxxcRT69MaQAA9sXaxv6qFFLG-JP4cFKI-gBAAMCAAN5AAM9BA"

})



        save()



        bot.send_message(

            message.chat.id,

            "✅ Товар добавлен!",

            reply_markup=back_button()

        )



    except:



        bot.send_message(

            message.chat.id,

            """
❌ Ошибка формата

Пример:

brawl-170 гемов Brawl Stars-299
""",

            reply_markup=back_button()

        )





# =========================
# СОЗДАНИЕ ПРОМОКОДА
# =========================
def create_promo(message, target="all"):

    global promo_temp_target

    try:

        data = message.text.strip().upper().split("|")

        if len(data) != 3:
            raise Exception

        code = data[0]
        discount = data[1]
        limit = data[2]


        db["promocodes"][code] = {

            "discount": int(discount),

            "limit": int(limit),

            "uses": 0,

            "date": None,

            "time": None,

            "target": target

        }


        save()

        promo_temp_target = None


        bot.send_message(

            message.chat.id,

            f"✅ Промокод создан!\n\n"

            f"🎟 {code}\n"

            f"🔢 Лимит: {limit}",

            reply_markup=back_button()

        )


    except:


        bot.send_message(

            message.chat.id,

            """
❌ Ошибка

Формат:

КОД|СКИДКА|ЛИМИТ


Пример:

VEYRON10|10|5
""",

            reply_markup=back_button()

        )

def create_promo_time(message, target="all"):

    global promo_temp_target

    try:

        code, discount, date, time = (

            message.text

            .replace(" ", "")

            .replace("\n", "")

            .upper()

            .split("|")

        )


        db["promocodes"][code] = {

            "discount": int(discount),

            "date": date,

            "time": time,

            "uses": 0,

            "limit": None,

            "target": target

        }


        save()


        moscow = pytz.timezone("Europe/Moscow")

        check_date = datetime.strptime(

            date + " " + time,

            "%d.%m.%Y %H:%M"

        )

        check_date = moscow.localize(check_date)

        now = datetime.now(moscow)


        if now > check_date:

            status = "⚠️ Внимание: срок уже истёк"

        else:

            status = "✅ Срок активен"



        promo_temp_target = None


        bot.send_message(

            message.chat.id,

            f"✅ Промокод создан!\n\n"

            f"🎟 {code}\n"

            f"⏳ До: {date} {time}\n\n"

            f"{status}",

            reply_markup=back_button()

        )


    except:


        bot.send_message(

            message.chat.id,

            """
❌ Ошибка

Формат:

КОД|СКИДКА|ДАТА|ВРЕМЯ


Пример:

VEYRON10|10|25.07.2026|15:12
""",

            reply_markup=back_button()

        )
def finish_target_all(message):

    global promo_temp_target


    promo_temp_target = "all"


    kb = types.InlineKeyboardMarkup()


    kb.add(

        types.InlineKeyboardButton(

            "🔢 Лимит активаций",

            callback_data="promo_limit_all"

        )

    )


    kb.add(

        types.InlineKeyboardButton(

            "⏳ Срок действия",

            callback_data="promo_time_all"

        )

    )


    bot.send_message(

        message.chat.id,

        """
🎟 Промокод на весь магазин выбран.

Выберите ограничение:
""",

        reply_markup=kb

    )
# =========================
# РАССЫЛКА
# =========================


def mailing(message):

    count = 0


    for user in db["users"]:


        try:


            if message.photo:

                bot.send_photo(

                    int(user),

                    message.photo[-1].file_id,

                    caption=message.caption

                )


            else:

                bot.send_message(

                    int(user),

                    message.text

                )


            count += 1


        except:


            pass



    bot.send_message(

        message.chat.id,

        f"✅ Рассылка завершена\n\n"
        f"👥 Отправлено: {count}",

        reply_markup=back_button()

    )





# =========================
# АКТИВАЦИЯ ПРОМОКОДА
# =========================


def check_promo(message):


    code = message.text.upper()



    if code not in db["promocodes"]:


        bot.send_message(

            message.chat.id,

            "❌ Такого промокода нет",

            reply_markup=back_button()

        )

        return




    promo = db["promocodes"][code]



    if promo.get("limit") is not None and promo["uses"] >= promo["limit"]:

        bot.send_message(

            message.chat.id,

            "❌ Промокод закончился",

            reply_markup=back_button()

        )

        return




    db["users"][str(message.from_user.id)]["promo"] = code



    save()



    bot.send_message(

        message.chat.id,

        f"✅ Промокод активирован!\n\n"
        f"💸 Скидка: {promo['discount']}%",

        reply_markup=back_button()

    )





# =========================
# СОХРАНЕНИЕ ID ФОТО
# =========================


@bot.message_handler(content_types=["photo"])

def get_photo(message):

    print(

        "FILE_ID:",

        message.photo[-1].file_id

    )
# =========================
# ДОБАВЛЕНИЕ ФОТО К ТОВАРУ
# =========================


def add_product_photo(message, category, name, price):

    if not message.photo:


        bot.send_message(

            message.chat.id,

            "❌ Нужно отправить фото",

            reply_markup=back_button()

        )

        return



    photo_id = message.photo[-1].file_id




    db["products"][category].append({

        "name": name,

        "price": int(price),

        "photo": photo_id

    })



    save()



    bot.send_message(

        message.chat.id,

        "✅ Товар с фото добавлен!",

        reply_markup=back_button()

    )





# =========================
# ПРОСМОТР ЗАКАЗОВ АДМИНОМ
# =========================


def show_orders(message):


    if not db["orders"]:


        bot.send_message(

            message.chat.id,

            "📦 Заказов пока нет",

            reply_markup=back_button()

        )

        return




    text = "📦 Последние заказы:\n\n"



    for order in db["orders"][-10:]:


        text += (

            f"👤 ID: {order['user']}\n"

            f"📦 {order['product']}\n"

            f"💰 {order['price']}₽\n"

            "────────\n"

        )



    bot.send_message(

        message.chat.id,

        text,

        reply_markup=back_button()

    )
# =========================
# УДАЛЕНИЕ СООБЩЕНИЙ МЕНЮ
# =========================


def delete_message_safe(chat_id, message_id):

    try:

        bot.delete_message(

            chat_id,

            message_id

        )


    except:

        pass





# =========================
# НАЗАД ИЗ ЛЮБОГО РАЗДЕЛА
# =========================


@bot.callback_query_handler(
    func=lambda c: c.data == "back_menu"
)

def back_menu(call):


    bot.answer_callback_query(call.id)



    delete_message_safe(

        call.message.chat.id,

        call.message.message_id

    )



    bot.send_photo(

        call.message.chat.id,

        photo="AgACAgIAAxkBAAIIG2pcoPtpUZI78NvAUg-Ej5t61fOpAAK6G2sbnhLZShiDXP63k6pfAQADAgADeQADPQQ",

        caption="""

🦫 VEYRONSHOP

Добро пожаловать!

🎮 Донат Brawl Stars
⭐ Telegram Stars

Выберите раздел ниже 👇

""",

        reply_markup=menu(

            call.from_user.id

        )

    )





# =========================
# ОЧИСТКА STEP HANDLER
# =========================


def clear_user_state(chat_id):

    try:

        bot.clear_step_handler_by_chat_id(

            chat_id

        )

    except:

        pass
# =========================
# ОБРАБОТКА ОТЗЫВОВ (УЛУЧШЕННАЯ)
# =========================


def reviews_menu(message):

    kb = types.InlineKeyboardMarkup()



    kb.add(

        types.InlineKeyboardButton(

            "✍️ Написать отзыв",

            callback_data="write_review"

        )

    )



    kb.add(

        types.InlineKeyboardButton(

            "👀 Смотреть отзывы",

            callback_data="show_reviews"

        )

    )



    kb.add(

        types.InlineKeyboardButton(

            "🔙 Назад",

            callback_data="back_menu"

        )

    )



    bot.send_message(

        message.chat.id,

        "💬 Отзывы VEYRONSHOP:",

        reply_markup=kb

    )





@bot.callback_query_handler(
    func=lambda c: c.data == "write_review"
)
def write_review(call):


    bot.answer_callback_query(call.id)



    delete_message_safe(

        call.message.chat.id,

        call.message.message_id

    )

    kb = types.InlineKeyboardMarkup()

    for i in range(1, 6):

        kb.add(
            types.InlineKeyboardButton(
                "⭐" * i,
                callback_data=f"rating_{i}"
            )
        )


    msg = bot.send_message(

    call.message.chat.id,

    "⭐ Оцените магазин:",

    reply_markup=kb

)










    bot.send_message(

        message.chat.id,

        "✅ Спасибо за отзыв!",

        reply_markup=back_button()

    )
# =========================
# ПОКАЗ ОТЗЫВОВ
# =========================


@bot.callback_query_handler(

    func=lambda c: c.data == "show_reviews"

)

def show_reviews(call):


    bot.answer_callback_query(call.id)



    if not db["reviews"]:


        bot.send_message(

            call.message.chat.id,

            "💬 Отзывов пока нет",

            reply_markup=back_button()

        )

        return




    text = "💬 Последние отзывы:\n\n"
    ratings = [
        r.get("rating", 0)
        for r in db["reviews"]
    ]

    average = sum(ratings) / len(ratings)

    text += f"⭐ Средняя оценка: {average:.1f}/5\n\n"


    for review in db["reviews"][-10:]:

        text += (

            f"👤 {review['user']}\n"

            f"⭐ Оценка: {'⭐' * review.get('rating', 0)} ({review.get('rating', 0)}/5)\n"

            f"💬 {review['text']}\n"

            "────────────\n\n"

        )



    delete_message_safe(

        call.message.chat.id,

        call.message.message_id

    )



    bot.send_message(

        call.message.chat.id,

        text,

        reply_markup=back_button()

    )


@bot.callback_query_handler(
    func=lambda c: c.data.startswith("reply_")
)
def reply_support(call):

    user_id = int(
        call.data.split("_")[1]
    )

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "💬 Напишите ответ пользователю:"
    )

    bot.register_next_step_handler(
        call.message,
        lambda m: send_reply_to_user(m, user_id)
    )


def send_reply_to_user(message, user_id):

    bot.send_message(
        user_id,
        f"""
🆘 Ответ поддержки:

{message.text}
"""
    )

    bot.send_message(
        message.chat.id,
        "✅ Ответ отправлен"
    )

@bot.callback_query_handler(
    func=lambda c: c.data.startswith("delpromo_")
)
def delete_promo(call):

    bot.answer_callback_query(call.id)


    code = call.data.replace(
        "delpromo_",
        ""
    )


    if code in db["promocodes"]:

        del db["promocodes"][code]

        save()


        bot.send_message(
            call.message.chat.id,
            f"🗑 Промокод удалён:\n\n🎟 {code}",
            reply_markup=back_button()
        )

    else:

        bot.send_message(
            call.message.chat.id,
            "❌ Промокод не найден",
            reply_markup=back_button()
        )

@bot.callback_query_handler(
    func=lambda c: c.data == "clear_orders"
)
def clear_orders_button(call):

    if call.from_user.id != ADMIN_ID:
        return

    bot.answer_callback_query(call.id)

    db["orders"] = []

    save()

    bot.send_message(
        call.message.chat.id,
        "🗑 Все заказы очищены",
        reply_markup=back_button()
    )
# =========================
# ОПЛАТА ПО НОМЕРУ
# =========================

REQUISITES_NUMBER = "79130081416"
REQUISITES_BANK = "Сбербанк"

if "pending_orders" not in db:
    db["pending_orders"] = {}

if "order_counter" not in db:
    db["order_counter"] = 0


def start_payment(chat_id, buyer_id, buyer_username, category, index, product, receiver, price, promo_code):

    db["order_counter"] += 1
    order_id = str(db["order_counter"])

    db["pending_orders"][order_id] = {
        "buyer_id": buyer_id,
        "buyer_username": buyer_username,
        "category": category,
        "index": index,
        "product": product["name"],
        "receiver": receiver,
        "price": price,
        "promo_code": promo_code
    }

    save()

    available_points = get_active_points(buyer_id)

    if available_points > 0:

        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton(
                f"✅ Списать поинты ({available_points})",
                callback_data=f"usepoints_{order_id}"
            )
        )
        kb.add(
            types.InlineKeyboardButton(
                "❌ Не использовать",
                callback_data=f"nopoints_{order_id}"
            )
        )

        bot.send_message(
            chat_id,
            f"🦫 У вас {available_points} VEYRON Points\n\n"
            f"1 Point = 1₽. Хотите списать их для скидки на этот заказ?",
            reply_markup=kb
        )

    else:

        send_payment_details(chat_id, order_id)


def send_payment_details(chat_id, order_id):

    order = db["pending_orders"][order_id]

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "🔙 Назад",
            callback_data=f"cancelorder_{order_id}"
        )
    )

    msg = bot.send_message(
        chat_id,
        f"💳 Оплата заказа\n\n"
        f"📦 {order['product']}\n"
        f"💰 Сумма: {order['price']}₽\n\n"
        f"Переведите на номер:\n"
        f"📱 {REQUISITES_NUMBER}\n"
        f"🏦 Банк: {REQUISITES_BANK}\n\n"
        f"После оплаты отправьте сюда скриншот перевода.",
        reply_markup=kb
    )

    bot.register_next_step_handler(
        msg,
        lambda m: payment_screenshot_received(m, order_id)
    )


def payment_screenshot_received(message, order_id):

    if order_id not in db["pending_orders"]:
        bot.send_message(message.chat.id, "❌ Заказ не найден или уже обработан")
        return

    if not message.photo:
        msg = bot.send_message(
            message.chat.id,
            "❌ Нужно отправить именно скриншот (фото) оплаты"
        )
        bot.register_next_step_handler(
            msg,
            lambda m: payment_screenshot_received(m, order_id)
        )
        return

    db["pending_orders"][order_id]["screenshot"] = message.photo[-1].file_id
    save()

    msg = bot.send_message(
        message.chat.id,
        "👤 Введите имя отправителя (от кого перевод, например: Данил К.):"
    )

    bot.register_next_step_handler(
        msg,
        lambda m: payment_phone_received(m, order_id)
    )


def payment_phone_received(message, order_id):

    if order_id not in db["pending_orders"]:
        bot.send_message(message.chat.id, "❌ Заказ не найден или уже обработан")
        return

    order = db["pending_orders"][order_id]
    order["sender_name"] = message.text.strip()
    save()

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Принять", callback_data=f"accept_order_{order_id}"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_order_{order_id}")
    )

    caption = (
        f"🧾 Заказ #{order_id}\n\n"
        f"👤 Покупатель: @{order['buyer_username']}\n"
        f"🆔 ID: {order['buyer_id']}\n"
        f"🎁 Получатель: {order['receiver']}\n"
        f"📦 Товар: {order['product']}\n"
        f"💰 Сумма: {order['price']}₽\n"
        f"👤 Отправитель: {order['sender_name']}\n"
    )

    if order.get("promo_code"):
        caption += f"🎟 Промокод: {order['promo_code']}\n"

    bot.send_photo(
        ADMIN_ID,
        order["screenshot"],
        caption=caption,
        reply_markup=kb
    )

    bot.send_message(
        message.chat.id,
        "✅ Данные отправлены администратору, ожидайте подтверждения."
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("accept_order_"))
def accept_order(call):

    if call.from_user.id != ADMIN_ID:
        return

    bot.answer_callback_query(call.id)

    order_id = call.data.replace("accept_order_", "")

    if order_id not in db["pending_orders"]:
        bot.send_message(call.message.chat.id, "❌ Заказ не найден или уже обработан")
        return

    order = db["pending_orders"].pop(order_id)

    db["orders"].append({
        "user": order["buyer_id"],
        "receiver": order["receiver"],
        "product": order["product"],
        "price": order["price"],
        "date": time.time()
    })

    save()

    award_points(order["buyer_id"], order["price"])

    if order["category"] == "brawl":

        msg = bot.send_message(
            order["buyer_id"],
            f"✅ Оплата подтверждена!\n\n"
            f"📦 {order['product']}\n"
            f"💰 {order['price']}₽\n\n"
            f"Скоро с вами свяжутся, пока что напишите вашу почту и айди аккаунта:"
        )

        bot.register_next_step_handler(
            msg,
            lambda m: send_account_info(m, order_id, order)
        )

        bot.send_message(
            call.message.chat.id,
            f"✅ Заказ #{order_id} принят. Ожидаю от клиента почту и ID аккаунта."
        )

    else:

        bot.send_message(
            order["buyer_id"],
            f"✅ Оплата подтверждена!\n\n"
            f"📦 {order['product']}\n"
            f"💰 {order['price']}₽\n\n"
            f"Заказ оформлен."
        )

        extra = ""
        if order["category"] == "stars":
            extra = "\n\n⭐ Не забудь выдать звёзды получателю вручную."

        bot.send_message(
            call.message.chat.id,
            f"✅ Заказ #{order_id} принят и подтверждён клиенту.{extra}"
        )


def send_account_info(message, order_id, order):

    bot.send_message(
        ADMIN_ID,
        f"📧 Данные для заказа #{order_id}\n\n"
        f"👤 Покупатель: @{order['buyer_username']}\n"
        f"🆔 ID: {order['buyer_id']}\n"
        f"📦 Товар: {order['product']}\n\n"
        f"✉️ Данные аккаунта:\n{message.text}"
    )

    bot.send_message(
        message.chat.id,
        "✅ Данные отправлены администратору, ожидайте связи."
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_order_"))
def reject_order(call):

    if call.from_user.id != ADMIN_ID:
        return

    bot.answer_callback_query(call.id)

    order_id = call.data.replace("reject_order_", "")

    if order_id not in db["pending_orders"]:
        bot.send_message(call.message.chat.id, "❌ Заказ не найден или уже обработан")
        return

    order = db["pending_orders"].pop(order_id)
    save()

    bot.send_message(
        order["buyer_id"],
        "❌ Оплата не подтверждена.\n\nЕсли вы уверены, что оплатили — напишите в поддержку."
    )

    bot.send_message(
        call.message.chat.id,
        f"❌ Заказ #{order_id} отклонён."
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("cancelorder_"))
def cancel_order(call):

    bot.answer_callback_query(call.id)

    order_id = call.data.replace("cancelorder_", "")

    if order_id in db["pending_orders"]:
        db["pending_orders"].pop(order_id)
        save()

    bot.clear_step_handler_by_chat_id(call.message.chat.id)

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    send_main_menu(call.message.chat.id, call.from_user.id)


# =========================
# VEYRON POINTS
# =========================


def award_points(buyer_id, price):

    uid = str(buyer_id)

    if uid not in db["users"]:
        db["users"][uid] = {"name": "", "date": time.time()}

    if "points" not in db["users"][uid]:
        db["users"][uid]["points"] = []

    points = int(price * 0.01)

    if points <= 0:
        return

    db["users"][uid]["points"].append({
        "amount": points,
        "date": time.time()
    })

    save()


def get_active_points(uid):

    uid = str(uid)

    if uid not in db["users"] or "points" not in db["users"][uid]:
        return 0

    now = time.time()
    valid = []
    total = 0

    for p in db["users"][uid]["points"]:

        if now - p["date"] < 30 * 24 * 3600:
            total += p["amount"]
            valid.append(p)

    db["users"][uid]["points"] = valid
    save()

    return total


@bot.callback_query_handler(func=lambda c: c.data == "points")
def show_points(call):

    bot.answer_callback_query(call.id)

    smooth_delete(call.message.chat.id, call.message.message_id)

    total = get_active_points(call.from_user.id)

    bot.send_message(
        call.message.chat.id,
        f"🦫 VEYRON Points\n\n"
        f"💰 Ваш баланс: {total} points\n\n"
        f"За каждую покупку вы получаете 1% от суммы\n"
        f"заказа в виде VEYRON Points.\n"
        f"1 Point = 1₽\n\n"
        f"⏳ Points сгорают через 1 месяц после получения.",
        reply_markup=back_button()
    )


def spend_points(uid, amount):

    uid = str(uid)

    if uid not in db["users"] or "points" not in db["users"][uid]:
        return

    remaining = amount
    new_list = []

    for p in db["users"][uid]["points"]:

        if remaining <= 0:
            new_list.append(p)
            continue

        if p["amount"] <= remaining:
            remaining -= p["amount"]
        else:
            p["amount"] -= remaining
            remaining = 0
            new_list.append(p)

    db["users"][uid]["points"] = new_list
    save()


@bot.callback_query_handler(func=lambda c: c.data.startswith("usepoints_"))
def use_points(call):

    bot.answer_callback_query(call.id)

    order_id = call.data.replace("usepoints_", "")

    if order_id not in db["pending_orders"]:
        return

    order = db["pending_orders"][order_id]

    available = get_active_points(order["buyer_id"])

    spend = min(available, order["price"] - 1) if order["price"] > 1 else 0

    if spend > 0:
        spend_points(order["buyer_id"], spend)
        order["price"] -= spend
        save()

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    bot.send_message(
        call.message.chat.id,
        f"✅ Списано {spend} поинтов. Новая цена: {order['price']}₽"
    )

    send_payment_details(call.message.chat.id, order_id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("nopoints_"))
def no_points(call):

    bot.answer_callback_query(call.id)

    order_id = call.data.replace("nopoints_", "")

    if order_id not in db["pending_orders"]:
        return

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    send_payment_details(call.message.chat.id, order_id)
# =========================
# ПОПОЛНЕНИЕ ЗВЁЗД БОТА
# =========================


def topup_stars_amount(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        amount = int(message.text.strip())

        if amount <= 0:
            raise Exception

    except:

        bot.send_message(
            message.chat.id,
            "❌ Введите целое число больше 0",
            reply_markup=back_button()
        )
        return

    bot.send_invoice(
        chat_id=message.chat.id,
        title=f"Пополнение на {amount}⭐",
        description=f"Пополнение баланса бота на {amount} звёзд",
        invoice_payload=f"topup_{amount}",
        provider_token="",
        currency="XTR",
        prices=[
            types.LabeledPrice(
                label="Звёзды",
                amount=amount
            )
        ]
    )


@bot.pre_checkout_query_handler(func=lambda q: True)
def process_pre_checkout(pre_checkout_query):

    bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )


@bot.message_handler(content_types=["successful_payment"])
def process_successful_payment(message):

    amount = message.successful_payment.total_amount

    db["star_balance"] += amount

    save()

    bot.send_message(
        message.chat.id,
        f"✅ Баланс бота пополнен на {amount}⭐\n"
        f"💰 Текущий баланс: {db['star_balance']}⭐"
    )
# =========================
# ЗАПУСК БОТА
# =========================


print("🦫 VEYRONSHOP ONLINE")



while True:


    try:


        bot.infinity_polling(

            skip_pending=True

        )



    except Exception as e:


        print(

            "ERROR:",

            e

        )


        time.sleep(5)
