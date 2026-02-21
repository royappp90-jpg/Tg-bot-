import telebot
import requests as rq
import random, secrets, threading, time
from user_agent import generate_user_agent

# ---------------- CONFIG ----------------

BOT_TOKEN = "8066634772:AAGV9uAUAx6Yz_LmYQff0itxdwLzat9SEmo"
bot = telebot.TeleBot(BOT_TOKEN)

running = False
threads = []

work = 0
not_insta = 0
not_email = 0
yes_email = 0

# ---------------- CORE FUNCTIONS ----------------

def recaptcha():
    try:
        url = "https://www.google.com/recaptcha/api2/anchor?k=6LfEUPkgAAAAAKTgbMoewQkWBEQhO2VPL4QviKct"
        r = rq.get(url, timeout=30).text
        token = r.split('recaptcha-token" value="')[1].split('"')[0]
        return token
    except:
        return None


def hi2(prefix):
    url = "https://hi2.in/api/custom"
    data = {
        "domain": "@hi2.in",
        "prefix": prefix,
        "recaptcha": recaptcha()
    }
    r = rq.post(url, data=data).text
    return "address already taken" not in r


def telegmail(prefix):
    url = "https://hi2.in/api/custom"
    data = {
        "domain": "@telegmail.com",
        "prefix": prefix,
        "recaptcha": recaptcha()
    }
    r = rq.post(url, data=data).text
    return "address already taken" not in r


def insta_check(mail):
    url = "https://www.instagram.com/api/v1/web/accounts/check_email/"
    headers = {
        "User-Agent": generate_user_agent(),
        "X-Csrftoken": secrets.token_hex(16),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"email": mail}
    try:
        r = rq.post(url, headers=headers, data=data).text
        return "email_is_taken" in r
    except:
        return False


def genprefix():
    return ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(6,7)))

# ---------------- WORKER ----------------

def worker(domain, chat_id):
    global work, not_email, not_insta, yes_email, running

    while running:
        prefix = genprefix()

        if domain == "hi2":
            ok = hi2(prefix)
            email = f"{prefix}@hi2.in"
        else:
            ok = telegmail(prefix)
            email = f"{prefix}@telegmail.com"

        if ok:
            yes_email += 1
            if insta_check(email):
                work += 1
                bot.send_message(chat_id, f"✅ HIT FOUND\n{email}")
            else:
                not_insta += 1
        else:
            not_email += 1


# ---------------- BOT COMMANDS ----------------

@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id,
    "/run 1  → Hi2 domain\n"
    "/run 2  → Telegmail domain\n"
    "/stop → Stop workers\n"
    "/stats → Show stats"
    )


@bot.message_handler(commands=["run"])
def run(msg):
    global running, threads
    if running:
        bot.send_message(msg.chat.id, "Already running.")
        return

    try:
        choice = msg.text.split()[1]
    except:
        bot.send_message(msg.chat.id, "Use: /run 1 or /run 2")
        return

    domain = "hi2" if choice == "1" else "telegmail"

    running = True
    threads = []

    for i in range(20):
        t = threading.Thread(target=worker, args=(domain, msg.chat.id))
        t.start()
        threads.append(t)

    bot.send_message(msg.chat.id, "Started checking...")


@bot.message_handler(commands=["stop"])
def stop(msg):
    global running
    running = False
    bot.send_message(msg.chat.id, "Stopped.")


@bot.message_handler(commands=["stats"])
def stats(msg):
    bot.send_message(msg.chat.id,
    f"✅ HITS: {work}\n"
    f"📧 VALID EMAIL: {yes_email}\n"
    f"❌ BAD EMAIL: {not_email}\n"
    f"❌ NOT INSTA: {not_insta}"
    )


# ---------------- START BOT ----------------

print("Bot running...")
bot.infinity_polling()
