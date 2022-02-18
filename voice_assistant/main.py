import speech_recognition as sr
import pyttsx3 as p3
import pywhatkit
import vk_api
import datetime
import config
import pyowm

listener = sr.Recognizer() # Присваеваем в переменную
engine = p3.init() # Инициализируем

# Изменяем озвучку голосового помощника
voices = engine.getProperty("voices")
voice = engine.setProperty("voice", voices[1].id)

# Метод говорить
def talk(text):
    engine.say(text)
    engine.runAndWait()

# Метод слушать
def listen():
    # Записываем фоновый шум для его отсечения
    with sr.Microphone() as source:
        listener.adjust_for_ambient_noise(source)
    try:
        print("Слушаю...")
        with sr.Microphone() as source:
            voice = listener.listen(source)
            command = listener.recognize_google(voice, language="ru-Ru")
            return command.lower()
    except:
        print("Не распознал...")
        return ""

# Метод даты и времени
def date_and_time():
    time = datetime.datetime.now()
    time = time.strftime("%I:%M")

    date = datetime.datetime.now()
    month = ["Января", "Февраля", "Марта","Апреля","Мая","Июня"
             "Июля","Августа","Сентября","Октября","Ноября","Декабря"]
    day = int(date.strftime("%d"))
    mon = int(date.strftime("%m"))
    return f"{day}, {month[mon - 1]}, {time}"

# Метод включения и поиска видео на ютуб
def on_video():
    talk("Скажите название видео")
    video = listen()
    talk(f"Включаю {video}")
    pywhatkit.playonyt(video)

# Метод поиска сайта
def search_website():
    talk("Скажите название сайта")
    website = listen()
    talk(f"Выполняю поиск...")
    pywhatkit.search(website)

# Инициализация Вконтакте
def vk_init():
    token = config.token_vk
    vk_session = vk_api.VkApi(token=token)
    return vk_session.get_api()

# Метод получение сообщений Вк
def get_message_vk():
    answer = []
    vk = vk_init()
    conversations = vk.messages.getConversations(offsets=0, count=20)
    for item in conversations["items"]:
        try:
            unread_count = item["conversation"]["unread_count"]
            dialog_id = item["conversation"]["peer"]["local_id"]
            conversation = vk.messages.getHistory(
                peer_id=dialog_id,
                count=unread_count,
                extended=True
            )
            profile = conversation["profiles"][0]
            user = f"{profile['first_name']} {profile['last_name']}"
            messages = conversation["items"]
            messages.reverse()
            text = ""
            for message in messages:
                text += message["text"] + "\n"

            answer.append(f"{unread_count} сообщение от пользователя {user}:\n{text}")
        except:
            pass
        return answer

# Метод озвучивание сообщений Вк
def talk_message_vk():
    messages = get_message_vk()
    if len(messages) > 0:
        talk("Сейчас скажу вам ваши сообщения")
        for message in messages:
            talk(message)
    else:
        talk(f"У вас нет новых сообщений")

# Метод написания сообщений
def write_message_vk():
    vk = vk_init()
    try:
        talk("Кому написать?")
        name = listen()
        friends = vk.friends.search(user_id="190319434", q=name)
        friend_id = friends["items"][0]["id"]
        talk("Что написать?")
        text_message = listen()
        vk.messages.send(user_id=friend_id, message=text_message, random_id=0)
        talk("Отправила")
    except:
        talk("Извините, такого пользователя нет в вашем списке друзей")

# Метод получение погоды
def get_weather():
    own = pyowm.OWM(config.token_weather)
    manager = own.weather_manager()
    data_plase = manager.weather_at_place("Saransk")
    weather = data_plase.weather
    weather_city = f"На улице {round(weather.temperature('celsius')['temp'])} " \
                   f"градусов, ветер {round(weather.wind()['speed'])} метров"
    talk(weather_city)

# Метод запуск программы
def run():
    print("Скажите ключевое слово...")
    command = listen()
    if "помощник" in command:
        talk("Привет, я твой голосовой помощник. Скажи что мне нужно сделать?")
        print("Ожидаю команду...")
        command = listen()
        if "скажи" in command:
            date_and_time()
            data = date_and_time()
            talk(data)
        if "включи" in command:
            on_video()
        if "найди" in command:
            search_website()
        if "прочитай" in command:
            talk_message_vk()
        if "напиши" in command:
            write_message_vk()
        if "погода" in command:
            get_weather()
while True:
    run()
