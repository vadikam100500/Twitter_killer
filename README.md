# **Twitter killer**
- **Social network of bloggers**
***
#### *A social network that allows you to create an account, publish posts, subscribe to your favorite authors and tag your favorite posts.*
***
## Stack

- Python 3
- Django 2.2
- sqlite3
- Bootstrap
- JavaScript
- CSS
***
## Local deploy
- Install and activate the virtual environment
- Install dependencies from requirements.txt
   ```
   $ pip install -r requirements.txt
   ``` 
- In the folder with manage.py, run the command:
   ```
   $ python3 manage.py runserver
   ```
- If you want to use debug-toolbar, uncomment correct lines in congfig and TwiKi urls, before runserver
***
## Task:

Необходимо разработать социальную сеть для публикации личных дневников.
Это будет сайт, на котором можно создать свою страницу. 
Если на нее зайти, то можно посмотреть все записи автора.
Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи.
Автор может выбрать для своей страницы имя и уникальный адрес. Дизайн можно взять самый обычный, но красивый.
Тексты без особой разметки. Не обязательно добавлять картинки и прочее. Но должно выглядеть нормально, поиграйте со шрифтами.
Еще надо иметь возможность модерировать записи и блокировать пользователей, если начнут присылать спам.
Записи можно отправить в сообщество и посмотреть там записи разных авторов.
