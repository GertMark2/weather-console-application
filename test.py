import sqlite3
from uuid import UUID, uuid4
import hashlib
import requests


def hash_password(password: str) -> str:
    binary_password = password.encode()
    hashed_password = hashlib.sha512(binary_password)
    return hashed_password.hexdigest()


class User:
    def __init__(self, user_id: UUID, phone: str, username: str, password: str):
        self.__user_id = user_id
        self.__phone = phone
        self.__username = username
        self.__password = hash_password(password)

    def __repr__(self) -> str:
        return f"User(id: {self.__user_id}, username: {self.__username}, phone: {self.__phone})"

    @property
    def username(self) -> str:
        return self.__username

    @property
    def password(self) -> str:
        return self.__password

    @property
    def user_id(self) -> UUID:
        return self.__user_id

    @property
    def phone(self) -> str:
        return self.__phone


class Controller:
    def __init__(self, db_file: str):
        self.__current_user = None
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                                id TEXT PRIMARY KEY,
                                username TEXT UNIQUE,
                                password TEXT,
                                phone TEXT
                              )"""
        )
        self.conn.commit()

    def signup(self) -> None:
        user_id = str(uuid4())
        username = input("Введите ваш ник для регистрации: ")
        password = input("Введите ваш пароль для регистрации: ")
        hashed_password = hash_password(password)
        phone = input("Введите ваш номер телефона для регистрации: ")

        self.conn.execute(
            "INSERT INTO users (id, username, password, phone) VALUES (?, ?, ?, ?)",
            (user_id, username, hashed_password, phone),
        )
        self.conn.commit()
        print("Вы успешно зарегистрировались!")

    def auth_user(self) -> None:
        while True:
            username = input("Введите ваш ник для входа: ")
            password = input("Введите ваш пароль для входа: ")
            hashed_password = hash_password(password)

            cursor = self.conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, hashed_password),
            )
            user = cursor.fetchone()
            if user:
                print("Вы успешно вошли в аккаунт!")
                self.__current_user = User(UUID(user[0]), user[3], user[1], user[2])
                return
            print("Неверно введены данные, пожалуйста, повторите")

    def logout(self) -> None:
        self.__current_user = None
        print("Вы успешно вышли из аккаунта!")


class Weather:
    API_KEY = "2616edff0099a3fc02337636ce31f2d0"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather_by_city(self, city_name: str) -> dict:
        params = {"q": city_name, "appid": self.API_KEY, "units": "metric"}
        response = requests.get(self.BASE_URL, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(
                f"Не удалось получить данные о погоде. Ошибка {response.status_code}"
            )

    def print_weather(self, data: dict) -> None:
        if "name" in data:
            city_name = data["name"]
            max_temp = data["main"]["temp_max"]
            min_temp = data["main"]["temp_min"]
            wind_speed = data["wind"]["speed"]

            print(f"Город: {city_name}")
            print(f"Максимальная температура: {max_temp} градусов")
            print(f"Минимальная температура: {min_temp} градусов")
            print(f"Скорость ветра: {wind_speed} м\с")
        else:
            print("Ошибка: Не удалось получить данные о погоде.")


db_file = "weather.db"
controller = Controller(db_file)
controller.signup()
controller.auth_user()

weather = Weather()
city_name = input("Введите название города: ")
weather_data = weather.get_weather_by_city(city_name)
weather.print_weather(weather_data)
