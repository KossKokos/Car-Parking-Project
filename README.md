# Застосунок Car Parking  (Team 4)


Застосунок Car Parking - це веб-додаток, який автоматизує управління паркуванням, включаючи оптичне розпізнавання номерних знаків і відстеження тривалості паркування. Він надає користувачам зручний інтерфейс для перегляду історії паркування, а адміністраторам - можливість управління обліковими записами та тарифами. Застосунок спрощує процес паркування і полегшує його управління, забезпечуючи зручність для всіх користувачів.



![Logo](https://github.com/KossKokos/Car-Parking-Project/blob/main/main.py)
![Logo](https://github.com/KossKokos/Car-Parking-Project/blob/dev/car_parking/Logo/logo.jpeg)
![Logo](https://github.com/KossKokos/Car-Parking-Project/blob/max_limit_2/car_parking/Logo/logo.jpeg)



## Зміст
- [Особливості](#особливості)
- [Залежності](#залежності)
- [Опис](#опис)
- [Налаштування та запуск API](#налаштування_та_запуск_API)
- [Документація](#документація)
- [Ліцензія](#ліцензія)
- [Учасники](#учасники)
## Contributors

## Особливості
- Управління обліковими записами користувачів.
- Ролі адміністратора та звичайного користувача.
- Функції адміністратора - додавання/видалення зареєстрованих номерних знаків, налаштування тарифів на паркування та можливість створення чорного списку транспортних засобів.
- Функції користувача - перегляд власної інформації про номерний знак та історії паркування
- Приймання зображень від користувача. Детекція номерного знаку. Виявлення та виділення області із номерним знаком зі зображень.
- Оптичне розпізнавання символів для ідентифікації тексту номерного знаку.
- Пошук номера авто у базі даних зареєстрованих транспортних засобів.
- Відстеження тривалості паркування.
- Запис часу в'їзду/виїзду кожного разу, коли визначається номерний знак.
- Розрахунок загальної тривалості паркування для кожного унікального номерного знаку.
- Зберігання даних про тривалість, пов'язаних із номерними знаками в базі даних. Розрахунок вартості паркування.
- Сповіщення користувача, якщо накопичені парковочні витрати перевищують встановлені ліміти.
- Генерація звітів про розрахунки, які можна експортувати у форматі CSV.


## Залежності
  * python==3.10
  * alembic==1.10.2
  * babel==2.13.0
  * bcrypt==4.0.1
  * cloudinary==1.32.0
  * colorama==0.4.6
  * cryptography==41.0.5
  * docutils==0.19
  * fastapi==0.95.0
  * email-validator==1.3.1
  * fastapi-limiter==0.1.5
  * fastapi-mail==1.2.7
  * httpx==0.25.2
  * jinja2==3.1.2
  * passlib==1.7.4
  * psycopg2==2.9.5
  * pydantic==1.10.7
  * pytest==7.4.3
  * pytest-mock==3.12.0
  * python-dotenv==1.0.0
  * python-jose==3.3.0
  * python-multipart==0.0.6
  * redis==4.5.4
  * requests==2.31.0
  * sniffio==1.3.0
  * sphinx==6.1.3
  * sqlalchemy==2.0.7
  * starlette==0.26.1
  * urllib3==1.26.18
  * uvicorn==0.21.1
  * pytest-asyncio==0.23.2
  * pytest-trio==0.8.0
  * qrcode["pil"]==7.4.2

## Опис

В папці src знаходиться вся робоча система:
  -  У src\database знаходиться файл db.py, де підключено базу даних Postgresql, Щоб під'єднати власну db, потрібно ввести дані з вашої db у файл .env, що знаходиться у головній директорії проекту. 
  -  У src\models знаходяться моделі таблиць, які ви створюєте і мігруєте їх в базу даних, тільки в цьому файлі.
  -  У src\repository знаходяться crud фунції, кожен файл відповідальних за операції над певним об'єктом, наприклад в users.py тільки crud функції для юзерів і т.д. Нові crud операцї для нового об'єкта - новий файл.
  -  У src\routes знаходяться файли для створення шляхів, наприклад в auth.py будуть api/auth/login, api/auth/signup, api/auth/request_email і так далі, в users.py будуть шляхи які починаються з api/users/ і так для кожних нових шляхів - новий файл.
  -  у src\schemas знаходяться файли в яких моделі для видачі інформації, прийому від користувачів. Ви можете добавляти скільки завгодно моделів та файлів. 
  -  У src\services зберегаються модулі в яких знаходяться класи для виконання операцій по аутентифікації, авторизації і надсилання емейл для підтвердження користувача або скидання паролю та інформацію що стосується паркування.  Ви можете добаляти нові сервери, наприклад для роботи з cloudinary.
  -  У src\templates знахоться темплейти для надсилання емейлів.


## Налаштування та запуск API 
- Важливо!!! Усі скоманди для запуску застосунку повинні виконуватись у теці Instagram_killer. Для цього у терміналі необхідно виконати команду "cd Instagram_killer".

- Створить віртуальне оточення використовуючи Poetry за допомогою команди "poetry install --no-root".

- Активуйте оточення командою "poetry shell"

- Файл .example.env є прикладом, які дані потрібно записувати. Для того, щоб запустити API, потрібно перейменувати його в .env та ввести свої дані.

- Файл docker-compose потрібен для запуску відразу двох баз даних: postgres та redis. Це полегшує роботу та збільшує продуктивність. Щоб запустити  його, введіть в консолі команду "docker-compose up" або "docker-compose up -d", для того, щоб не бачити логування. Щоб зупинити, введіть в консо".

- Для запуску сервера потрібно виконати команду python main.py

## Документація

http://localhost:8000/docs

## Ліцензія

Цей проект підпадає під дію MIT лицензіЇ.

## Учасники
- [Kostiantyn Pereimybida / Team lead](https://github.com/KossKokos)
- [Dmytro Kruhlov / Scrum Master](https://github.com/Dmytro-Kruhlov)
- [Michael Ivanov / Developer](https://github.com/MikeIV2007)
- [Natalia Semeniuk / Developer](https://github.com/N1a2t3a)
- [Vladyslav Kyryllov / Developer](https://github.com/Vlad96Kir7)
