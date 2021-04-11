from flask import Flask, request
import logging

import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)  # Устанавливаем уровень логирования

# Когда новый пользователь напишет нашему навыку, то мы сохраним в этот словарь запись формата - подсказки
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!" ]}
# Когда он откажется купить слона, то мы уберем одну подсказку
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():  # Функция получает тело запроса и возвращает ответ.
    # Внутри доступен request.json (отправила нам Алиса в запросе POST)
    logging.info(f'Request: {request.json!r}')
    # Начинаем формировать ответ, согласно документации
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {'end_session': False}
    }
    handle_dialog(request.json, response)  # сформирует оставшиеся поля JSON
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)  # Преобразовываем в JSON и возвращаем


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    # Если это новый пользователь.
    if req['session']['new']:  # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз
        sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!"]}
        res['response']['text'] = 'Привет! Купи слона!'  # Заполняем текст ответа
        res['response']['buttons'] = get_suggests(user_id)  # Получим подсказки
        return

    #  Если пользователь согласился.
    if req['request']['original_utterance'].lower() in \
            ['ладно', 'куплю', 'покупаю', 'хорошо']:
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return

    # Если пользователь не согласился.
    res['response']['text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [{'title': suggest, 'hide': True} for suggest in session['suggests'][:2]]
    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:  # перебираем сущности
        if entity['type'] == 'YANDEX.FIO':   # находим сущность с типом 'YANDEX.FIO'
            # Если есть сущность с ключом 'first_name', возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
