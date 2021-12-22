  [![leon'studio](https://img.shields.io/badge/made%20by-leon'%20studio-inactive)](https://kwork.ru/user/LeoM97)
  ![python](https://img.shields.io/badge/Language-Python-red)
  ![Django](https://img.shields.io/badge/Framework-Django-brightgreen)
  ![Bootstrap](https://img.shields.io/badge/Client%20framework-Bootstrap-blueviolet)
  ![postgreSQL](https://img.shields.io/badge/Data%20Base-postgreSQL-%232f5b8b)
  ![channels](https://img.shields.io/badge/ASGI%20Framework-channels-%23f0b37e)
  ![celery](https://img.shields.io/badge/ASGI%20Tasks-celery-%23a0c250)
  ![redis](https://img.shields.io/badge/NoSQL-redis-%23d1352b)
  ![RabbitMQ](https://img.shields.io/badge/Message%20broker-RabbitMQ-%23f76300)
  ![API](https://img.shields.io/badge/API-Django%20Rest%20Frameowrk-%23a30000)
  ![Parser](https://img.shields.io/badge/Parser-Beautiful%20Soup-%239b9b9d)
  ![HTML](https://img.shields.io/badge/Markup-HTML-important)
  ![CSS](https://img.shields.io/badge/Stylesheets-CSS-9cf)
  ![JavaScript](https://img.shields.io/badge/interaction-Java%20Script-%23ead41c)
  <h1 align="center">Mianto Love - анонимный сайт знакомств</h1>

 <h2 align="center">Разворачивание проекта</h2>
 <p>Когда проект будет загружен на сервер требуется перейти в корневую папку проекта и выполнить следующие команды: </p>


* Устанавливаем виртуальное окружение
```
sudo apt install python3-venv
```
* Активируем виртуальное окружение
```
python3 -m venv env
source env/bin/activate
```
* Устанавливаем библиотеки, которые требуются для запуска проекта
```
pip install -r requeriments.txt
```

* Делаем миграцию базы данных
```
python manage.py makemigrations
python manage.py migrate
```
* Создаем суперпользователя
```
python manage.py createsuperuser
```


<h2 align="center">Работа с базой данных на сервере</h2>

<h3 align="center">Подключение базы PostgreSQL</h2>

<p>Для подключение базы данных PostgreSQL к проекту требуется выполнить несколько шагов</p>

* Для начала надо перейти в настройки проекта
```
cd mianto
nano settings.py
```
* При открытии документа требуется опуститься вниз до переменной DATABASE
* После чего удаляем все ``` # ``` которые относятся к ``` db_confg ``` 
* Как только ввели верные данные базы теперь можно делать миграцию базы данных.

<h3 align="center">Подключение базы Redis</h2>

<p>Redis здесь будет использоваться в виде резервного хранилища которое нам потребуется для работы библиотеки Channels</p>

* Переходим в файл ``` settings.py```, в нем буду настройки канала Redis которые указаны в переменной ```CHANNEL_LAYERS```

<h2 align="center">Внедрение очередь задач</h2>
<h3 align="center">Подключение брокера задач RabbitMQ</h2>
<p>Брокер сообщений предназначен для обработку сообщений путем приема и отдачи. В данном проекте будет использоваться для работы с задачами</p>
* Для работы брокера требуется его установить путем следующей команды

```
sudo apt install rabbitmq-server
```

* Настраиваем виртуальный хостинг

```
sudo rabbitmqctl add_user [myuser] [mypassword]
sudo rabbitmqctl add_vhost [myvhost]
sudo rabbitmqctl set_user_tags [myuser] [mytag]
sudo rabbitmqctl set_permissions -p [myvhost] [myuser] ".*" ".*" ".*"
```

* Запускаем сервер брокера

```
sudo rabbitmq-server
```

* В корневой папке проекте в файле ```celery.py``` для настройки своего виртуального хоста требуется указать данные в переменной ```app```

<h3 align="center">Запуск очереди задачи</h2>

* Для запуска задачи (в данном случае удаление объявлений через 30 дней) которая будет проверять объявления каждый день выполнив команду
```
celery -A mianto worker -B
```

<h2 align="center">Настройки проекта</h2>
<h3 align="center">Конфигурация почтового сервера</h2>
В корневой папке проекта ```mianto``` в файле ```settings.py``` требуется найти соответствующий комментарий где требуется указать настройки своего почтового сервера
```
EMAIL_HOST - хостинг почтового сервера
EMAIL_HOST_USER - почта сервера
EMAIL_HOST_PASSWORD - пароль почты сервера
EMAIL_PORT - порт smpt указан в настройках почтового домена
```

<h3 align="center">Конфигурация ReCaptcha v2</h3>
В корневой папке проекта  ```mianto```  в файле ```settings.py``` требуется найти соответствующий комментарий где требуется найти две следующий переменных и передать соответствующие ключ
```
RECAPTCHA_PUBLIC_KEY - публичный ключ
RECAPTCHA_PRIVATE_KEY - приватный ключ
```
Не забыть в админ панели ReCaptcha V2 указать домен сайт в настройках
<h3 align="center">Загрузка городов и стран</h3>
Для того что бы работала автоподсказки по городам требуется запустить скрипт путем перехода по ссылке ```areas/parsing/city/``` как только города будут успешно загружены в базу, вам вернет ответ ```Ок```
<h3 align="center">Логи и статика</h3>
Все логи чатов пользователей постоянно перезаписываются при их обновлении и поэтому загрузка больших количествах логов не будет, все логи хранятся в корневой папке ```media/log``` в виде .json файла, в остальных папках хранятся фотографии пользователей. Вся статика проекта находится в корневой папке ```static```.
<h3 align="center">Шаблоны сайта</h3>
Данный сайт был сверстан использовав Jinja2. Все макеты находятся в корневой папке ```templates```. 
<h3 align="center">Robots.txt</h3>
Перейдя по ссылке ```/robots.txt``` 




<h2 align="center">Работа с API</h2>
<h3 align="center">Документация</h2>
Все методы для работы с данным проектом можно увидеть только администратору перейдя по следующим ссылкам после ввода домена```swagger/ или redoc/```
<h3 align="center">API на сайте</h2>
Для работы с объявлениями
 
* Вывод всех объявлений перейти по ``` api/announce/ ``` так же там можно использовать фильтрацию
* Для вывода конкретного объявления стоит перейти по ``` api/announce/[id объявления]/```

Для работы с профилями

* Авторизация профиля ``` api/login/ ```
* Выйти за профиля ``` api/logout/ ```
* Регистрация профиля ```api/register/```
* Вывести конкретный профиль ```api/[id профиля]/```
* Вывести объявления конкретного пользователя ```api/[id профиля]/feed/```
* Вывести все созданные каналы чата пользователя ```api/[id профиля]/messages/```













    
