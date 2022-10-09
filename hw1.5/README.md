# Обработка ответа от REST API

Консольное приложение получает на вход название телепрограммы и выдает базовую информацию о нем

Для получения информации о телепрограмме нужно использовать открытый API https://www.tvmaze.com/api#show-single-search

Ваша задача:

1. Сделать запрос по адресу API используя библиотеку **requests**
2. Достать JSON из ответа используя метод **response.json** https://www.geeksforgeeks.org/response-json-python-requests/
3. Описать объект используя модели **pydantic** https://pydantic-docs.helpmanual.io
    1. Вам будут нужны следующие поля: **name, network.name, network.country.name, summary**
    2. Если данных полей нет в JSON, выдавать ошибку ValueError
4. Полученный JSON из ответа обработать используя вышеописанную модель данных
5. Используя `print()` вывести каждое поле на новой строке с соответственным заголовком (Name, Network Name, Network
   Country Name, Summary)
6. Имя телепрограммы должно приниматься на вход как параметр скрипта (может состоять из нескольких слов), пример
   запуска: `python -m tv_program Family Guy`
7. Обработать все остальные ошибки (нет данных в ответе API, ошибки запросы к API, проблемы с сетью API и тд)
8. Итоговый проект должен проходить тест и проверки flake8, black и MyPy

запуск тестов

```
make test
make lint
```

Пример работы скрипта:

```
python -m tv_program Family Guy

Name: Family Guy
Network Name: FOX
Network Country Name: United States
Summary: <p><b>Family Guy</b> follows Peter Griffin the endearingly ignorant dad, and his hilariously offbeat family of middle-class New Englanders in Quahog, RI. Lois is Peter's wife, a stay-at-home mom with no patience for her family's antics. Then there are their kids: 18-year-old Meg is an outcast at school and the Griffin family punching bag; 13-year-old Chris is a socially awkward teen who doesn't have a clue about the opposite sex; and one-year-old Stewie is a diabolically clever baby whose burgeoning sexuality is very much a work in progress. Rounding out the Griffin household is Brian the family dog and a ladies' man who is one step away from AA.</p>
```


## Усложненный вариант 
Нужно реализовать кэширование данных, чтобы полученная информация не перезапрашивалась, если мы ее уже запрашивали за последние 5 минут. Например, если мы запросили данные по The Simpsons, то при повторном запуске через 30 секунд данные возьмутся из кэша без запроса с сервису, а при запросе через 10 минут, будут запрошены свежие данные. 


Кэширование в коде НУЖНО реализовать через написание декоратора, который кэширует результат функции. 
Пример (формат можно изменить на свое усмотрение) 
```
@cache(ttl=5 * 60) 
def search(query: str):
        ... 
```
Данные сохраняем в виде файлов. Формат файлов и названия определяем сами. Использовать файловые базы данных (sqlite, etc.) НЕЛЬЗЯ.


## Критерии оценивания 
1) Получить JSON ответ от сервиса - 1 балл 
2) Описать модель данных используя Pydantic - 1 балл
3) Провалидировать полученый JSON используя модель данных - 3 балла 
4) Пройти тест и проверку линтерами - 3 балла 
5) Покрыть тестами логику поиска - 1 балл 
6) Сделать кэширующий декоратор - 2 балла 
 
 