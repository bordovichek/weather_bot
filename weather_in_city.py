from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from levenstein import levenstein
from time import sleep


def find_city(finded: List[str], original: str) -> tuple:
    """

    :param finded: список с городами, "выпавшими" на сайте из поисковой строки
    :param original: Искомый город
    Функция просто ищет расстояние Левенштейна для каждого города, если найдется с 100% попаданием, сразу его вернет
    :return: кортеж с названием найденного города и расстоянием Левенштейна
    """
    return_city = ''
    max_diff = 100
    for city in finded:
        difference = levenstein(city, original)
        if difference == 0:
            return city, 0
        if difference < max_diff:
            return_city = city
            max_diff = difference
    return return_city, max_diff


def weather(city: str) -> str:
    """

    :param city: город, информацию по которому хочет получить пользователь
    :return: строку с найденной информацией, либо с ошибкой
    """
    # проверка правильного ввода города, также с учетом символа "-"
    if city.isalpha() or (
            '-' in city[2:-2] and city.replace('-', '').isalpha() or ' ' in city[2:-2] and city.replace(' ',
                                                                                                        '').isalpha()):
        with webdriver.Chrome() as browser:
            to_find = tuple()
            browser.get('https://www.gismeteo.ru/')
            browser.find_element(By.XPATH, '/html/body/header/div[2]/div/div[1]/div[1]/div/input').send_keys(city)
            # ввод в поисковую строку города, который ввел пользователь
            sleep(2)  # "засыпаем" чтобы подождать, когда сайт выдаст все предлагаемые города (можно уменьшить при
            # желании, если позволяет скорость интернета)
            if browser.find_element(By.XPATH,
                                    '/html/body/header/div[2]/div/div/div[3]/div').text == "Ничего не найдено":
                # в случае если не найдено совпадений, то нужно выйти из функции с возвратом ошибки
                return "Простите, ничего не нашел по вашему запросу"
            if len(city.split()) == 2:  # пришлось отрабатывать 2 разных случая с городами в 1 слово и 2
                finded_city = browser.find_element(By.XPATH,
                                                   '/html/body/header/div[2]/div/div[1]/div[3]/div/div[2]/a[1]').text
                to_lev = " ".join(finded_city.split()[i].lower() for i in range(2))  # так как возвращается строка по
                # типу "Великий Новгород\nРоссия Новгородская область\n...", то нужно взять лишь первые 2 слова
                diff = levenstein(to_lev, city)  # получаем расстояние Левенштейна для искомого города и найденных на
                # сайте (про алгоритм погуглите, всяко лучше, чем я тут объяснять буду)
                if diff > 2:  # если есть отличие более чем в 2 знака, то выходим
                    return "Простите, ничего не нашел по вашему запросу"
                else:
                    browser.find_element(By.XPATH,
                                         '/html/body/header/div[2]/div/div[1]/div[3]/div/div[2]/a[1]').send_keys(
                        Keys.ENTER)  # если все нашлось, то нажимаем ENTER и переходим на сайт
            else:
                # В случае с городом в одно слово есть проблема, что при небольшом названии и одной ошибке при вводе,
                # может неправильно находиться город на сайте, поэтому будем искать расстояние для всех "выпадающих"
                # на сайте городов
                finded_cities = browser.find_element(By.XPATH,
                                                     '/html/body/header/div[2]/div/div[1]/div[3]/div/div[2]').text.split()  # Все "выпавшие" ujhjlf
                to_find = find_city(finded_cities, city)
                if to_find[1] > 2:
                    return "Простите, ничего не нашел по вашему запросу"
                for orig_city in browser.find_elements(By.CLASS_NAME,
                                                       'search-item '):  # Теперь среди выпавших ищем тот, у кого расстояние минимально
                    if orig_city.text.split()[0] == to_find[0]:
                        orig_city.click()
                        break
            sleep(0.5)  # опять заснули, чтобы дать сайту прогрузиться
            if to_find: # Тут будем создавать переменную с правильным названием города, чтобы вывод был без орфографических ошибок
                founded_city = to_find[0]
            else:
                founded_city = to_lev
            # в названии переменных все понятно, ищем соответствующую информацию
            date = browser.find_element(By.XPATH, '/html/body/main/div[1]/section[2]/div/div/div/div[1]/div[1]').text
            down_temp = browser.find_element(By.XPATH,
                                             '/html/body/main/div[1]/section[2]/div/div/div/div[1]/div[3]/div/div/div[1]/temperature-value').text
            top_temp = browser.find_element(By.XPATH,
                                            '/html/body/main/div[1]/section[2]/div/div/div/div[1]/div[3]/div/div/div[2]/temperature-value').text
            weather_whole_day = browser.find_element(By.XPATH,
                                                     '/html/body/main/div[1]/section[2]/div/div').get_attribute(
                'data-tooltip')
            weather_now = browser.find_element(By.XPATH,
                                               '/html/body/main/div[1]/section[2]/div/a[1]/div/div[1]/div[3]/div/div[2]').text.lower()
            # ура, все нашли
            return f'Город: {founded_city.title()}\nДата: {date[4:]}\nТемпература от {down_temp} до {top_temp}\nПогода: "{weather_whole_day}"\nСейчас {weather_now}'
    else:
        return "Ой, что-то вы не то ввели"
