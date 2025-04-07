# -*- coding: utf-8 -*-
#
# Скрипт для копирования данных о границах созвездий
# с сайта https://iau.org/public/themes/constellations/
# Дмитрий Клыков, 2025. dyuk108.ru

import requests
import wget  # удобно скачивать файлы

urlStartPage = 'https://iau.org/public/themes/constellations/'
r = requests.get(urlStartPage)
rt = r.text # получаем текст страницы

# Нужно выбрать url каждой гиперссылки для текста 'TXT'
iEnd = 0 # позиция конца фрагмента
urls = [] # ссылки на файлы
while True:
    iStart = rt.find('<a href="/static/public/constellations/txt', iEnd)
    if iStart == -1: # если больше не найдено
        break
    iStart += 9 # смещение до url
    iEnd = rt.find('">TXT</a>', iStart)
    urls.append('https://iau.org' + rt[iStart:iEnd]) # вырезаем нужный кусок

# Скачиваем файлы по списку ссылок.
for url in urls:
    print(url)
    wget.download(url) # скачиваем файл
print(len(urls), ' файлов')