
# Застосунок Car Parking  (Team 4)


Застосунок Car Parking - це веб-додаток, який автоматизує управління паркуванням, включаючи оптичне розпізнавання номерних знаків і відстеження тривалості паркування. Він надає користувачам зручний інтерфейс для перегляду історії паркування, а адміністраторам - можливість управління обліковими записами та тарифами. Застосунок спрощує процес паркування і полегшує його управління, забезпечуючи зручність для всіх користувачів.



![Logo](https://github.com/KossKokos/Car-Parking-Project/blob/main/car_parking/Logo/logo.jpeg)



## Зміст
- [Особливості](#особливості)
- [Залежності](#залежності)
- [Опис](#опис)
- [Налаштування та запуск API](#налаштування_та_запуск_API)
- [Створення docker image](#створення-docker-image)
- [Документація](#документація)
- [Ліцензія](#ліцензія)
- [Учасники](#учасники)

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
  * absl-py==2.1.0
  * aiosmtplib==2.0.2
  * alabaster==0.7.16
  * alembic==1.10.2
  * anyio==4.3.0
  * astunparse==1.6.3
  * async-timeout==4.0.3
  * attrs==23.2.0
  * babel==2.13.0
  * bcrypt==4.0.1
  * blinker==1.7.0
  * cachetools==5.3.3
  * certifi==2024.2.2
  * cffi==1.16.0
  * charset-normalizer==3.3.2
  * click==8.1.7
  * cloudinary==1.32.0
  * colorama==0.4.6
  * cryptography==41.0.5
  * dnspython==2.6.1
  * docutils==0.19
  * ecdsa==0.19.0
  * email-validator==1.3.1
  * exceptiongroup==1.2.0
  * fastapi-limiter==0.1.5
  * fastapi-mail==1.2.7
  * fastapi==0.95.0
  * flatbuffers==24.3.25
  * gast==0.5.4
  * google-auth-oauthlib==0.4.6
  * google-auth==2.29.0
  * google-pasta==0.2.0
  * greenlet==3.0.3
  * grpcio==1.62.1
  * h11==0.14.0
  * h5py==3.11.0
  * httpcore==1.0.5
  * httpx==0.25.2
  * idna==3.7
  * imagesize==1.4.1
  * iniconfig==2.0.0
  * jinja2==3.1.2
  * keras-preprocessing==1.1.2
  * keras==2.8.
  * libclang==18.1.1
  * mako==1.3.3
  * markdown==3.6
  * markupsafe==2.1.5
  * numpy==1.26.4
  * oauthlib==3.2.2
  * opencv-python==4.9.0.80
  * opt-einsum==3.3.0
  * outcome==1.3.0.post0
  * packaging==24.0
  * passlib==1.7.4
  * pillow==10.3.0
  * pluggy==1.4.0
  * protobuf==3.20.0
  * psycopg2-binary==2.9.9
  * psycopg2==2.9.5
  * pyasn1-modules==0.4.0
  * pyasn1==0.6.0
  * pycparser==2.22
  * pydantic==1.10.7
  * pygments==2.17.2
  * pypng==0.20220715.0
  * pytest-asyncio==0.23.2
  * pytest-mock==3.12.0
  * pytest==7.4.3
  * python-dotenv==1.0.0
  * python-jose==3.3.0
  * python-multipart==0.0.6
  * pytz==2024.1
  * qrcode[pil]==7.4.2
  * redis==4.5.4
  * requests-oauthlib==2.0.0
  * requests==2.31.0
  * rsa==4.9
  * setuptools==69.5.1
  * six==1.16.0
  * sniffio==1.3.0
  * snowballstemmer==2.2.0
  * sortedcontainers==2.4.0
  * sphinx==6.1.3
  * sphinxcontrib-applehelp==1.0.8
  * sphinxcontrib-devhelp==1.0.6
  * sphinxcontrib-htmlhelp==2.0.5
  * sphinxcontrib-jsmath==1.0.1
  * sphinxcontrib-qthelp==1.0.7
  * sphinxcontrib-serializinghtml==1.1.10
  * sqlalchemy==2.0.7
  * starlette==0.26.1
  * tensorboard-data-server==0.6.1
  * tensorboard-plugin-wit==1.8.1
  * tensorboard==2.8.0
  * tensorflow-io-gcs-filesystem==0.23.1
  * tensorflow==2.8.0
  * termcolor==2.4.0
  * tf-estimator-nightly==2.8.0.dev2021122109
  * tomli==2.0.1
  * trio==0.25.0
  * typing-extensions==4.11.0
  * urllib3==1.26.18
  * uvicorn==0.21.1
  * werkzeug==3.0.2
  * wheel==0.43.0
  * wrapt==1.16.0

## Опис

В папці src знаходиться вся робоча система:
  -  У src\database знаходиться файл db.py, де підключено базу даних Postgresql, Щоб під'єднати власну db, потрібно ввести дані з вашої db у файл .env, що знаходиться у головній директорії проекту. 
  -  У src\database\models знаходяться моделі таблиць, які ви створюєте і мігруєте їх в базу даних, тільки в цьому файлі.
  -  У src\repository знаходяться crud фунції, кожен файл відповідальних за операції над певним об'єктом, наприклад в users.py тільки crud функції для юзерів і т.д.
  -  У src\routes знаходяться файли для створення шляхів, наприклад в auth.py будуть api/auth/login, api/auth/signup, api/auth/request_email і так далі, в users.py будуть шляхи які починаються з api/users/.
  -  у src\schemas знаходяться файли в яких моделі для видачі інформації, прийому від користувачів.
  -  У src\services зберегаються модулі в яких знаходяться класи для виконання операцій по аутентифікації, авторизації і надсилання емейл для підтвердження користувача або скидання паролю та інформацію що стосується паркування.
  -  У src\templates знаходяться темплейти для надсилання емейлів.


## Налаштування та запуск API 

- Створить віртуальне оточення використовуючи Poetry за допомогою команди "poetry install --no-root".

- Активуйте оточення командою "poetry shell"

- Файл .example.env є прикладом, які дані потрібно записувати. Для того, щоб запустити API, потрібно перейменувати його в .env та ввести свої дані.

- Файл docker-compose потрібен для запуску відразу двох баз даних: postgres та redis. Це полегшує роботу та збільшує продуктивність. Щоб запустити  його, введіть в консолі команду "docker-compose up" або "docker-compose up -d", для того, щоб не бачити логування. Щоб зупинити, введіть в консо".

- Для запуску сервера потрібно виконати команду python main.py

## Створення docker image

 - Для того, щоб створити docker image, потрібно змінити назву файлу `.example.env` на `.env` та ввести свої дані.

 - Потрібно знаходитись в головній директорії: `Car-Parking-Project` в консолі.

 - Останній етап - це запуск команди `docker build -t car-parking-project-image .`. Назву image, який буде створений можете вибрати самостійно.

 - Коли image створиться, запуск контейнера відбувається командою: `docker run --name car-parking-project-container -p 80:80 car-parking-project-image`. Після цього, перейдіть за посиланням http://localhost:80/docs, де буде документація swagger з якою, ви вже можете працювати. 

## Документація

http://localhost:80/docs

## Ліцензія

Цей проект підпадає під дію MIT лицензіЇ.

## Учасники
- [Kostiantyn Pereimybida / Team lead](https://github.com/KossKokos)
- [Dmytro Kruhlov / Scrum Master](https://github.com/Dmytro-Kruhlov)
- [Michael Ivanov / Developer](https://github.com/MikeIV2007)
- [Natalia Semeniuk / Developer](https://github.com/N1a2t3a)
- [Vladyslav Kyryllov / Developer](https://github.com/Vlad96Kir7)