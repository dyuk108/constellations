# -*- coding: utf-8 -*-
#
# Тестовый скрипт для построения карты всего неба в экваториальной проекции
# в формате SVG. Показывает, как можно исполдьзовать датасеты:
# - данные о ярчайших звёздах до 6,5m https://github.com/dyuk108/brightstar_dataset
# - данные о созвездиях (названия, границы, линии) https://github.com/dyuk108/constellations

import pandas as pd

# Читаем датасет по ярчайшим звёздам до 6,5m dataset_bright_stars.csv
# Индексы столбцов: 0 - HIP, 6 - Vmag, 11 - RAdeg, 12 - DEdeg
df_stars = pd.read_csv('dataset_bright_stars.csv', usecols=[0, 6, 9, 10])
df_stars.set_index('HIP', inplace=True) # назначаем индексом номер HIP
print(df_stars)

# Читаем датасет по названиям созведий constellations.csv
# 0 - сокращённое лат. название и 3 - номер HIP звезды, около которой рисовать название созвездия
df_cst = pd.read_csv('constellations.csv', encoding='utf-8') # там названия по-русски, поэтому utf-8
print(df_cst)

# Читаем датасет по границам созвездий constbnd_draw.csv
# 4 стоблца: координаты первой точки линии RA1,Dec1 и второй точки RA2,Dec2
df_bnd = pd.read_csv('constbnd_draw.csv')
print(df_bnd)

# Читаем датасет по линиям созведий constellations.csv
# 0 - HIP1, 1 - HIP2, 3 - созвездие
df_lines = pd.read_csv('cst_lines.csv')
print(df_lines)

# Работаем с файлом SVG.
margin = 10 # отступ от краёв
scale = 4 # масштаб для градусов, которые превращаются в "пиксели" изображения
width = 360*scale + 2*margin # развёртка 360 градусов по RA + поля
height = 120*scale + 2*margin # по Dec +- 60 градусов + поля

fw = open('examples/skymap_eq.svg', 'w')
fw.write(f'<svg version="1.1" baseProfile="full" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')

# Вверху нарисуем прямоугольник карты
fw.write(f'<rect x="{margin}" y="{margin}" width="{360*scale}" height="{120*scale}" stroke-width="0" fill="#122947"/>\n')

# Экваториальная координатная сетка в равнопромежуточной проекции.
for i in range(13): # сетка по RA
    x = i*scale*30 + margin # координата x линии на изображении, шаг - 20 градусов
    fw.write(f'<line x1="{x}" x2="{x}" y1="{margin}" y2="{height-margin}" stroke="#336699" stroke-opacity="0.8" stroke-width="0.5"/>\n')
    ra = 24 - i*2 # координата RA для надписей
    if ra == 24:
        ra = 0
    if ra == 0:
        shift = -12 # надпись левее линии
    else:
        shift = 3 # надпись правее линии

    fw.write(f'<text x="{x + shift}" y="{60*scale + margin - 5}" fill="#336699" font-size="10">{ra}h</text>\n')

for i in range(7): # сетка по Dec
    if i == 3: # линия экватора
        stroke_width = 1 # линия будет толще
    else:
        stroke_width = 0.5
    y = i*scale*20 + margin # координата y линии, шаг - 20 градусов; рисуем сверху
    fw.write(f'<line x1="{margin}" x2="{width-margin}" y1="{y}" y2="{y}" stroke="#336699" stroke-opacity="0.8" stroke-width="{stroke_width}"/>\n')
    dec = 60 - i*20
    if dec == 60: # верхняя линия
        shift = 10 # под линией надпись
    else:
        shift = -5 # под линией надпись
    fw.write(f'<text x="{margin + 3}" y="{y + shift}" fill="#336699" font-size="10">{dec}</text>\n')

# Функция рисования линий границ созвездий.
draw_line_bnd = lambda x1, x2, y1, y2: fw.write(f'<line x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" stroke="#FF5090" stroke-opacity="0.8" stroke-width="0.5" stroke-dasharray="5,1"/>\n')

# Рисуем линии границ созвездий.
for i in range(df_bnd.shape[0]):
    x1 = (360 - df_bnd.loc[i, 'RA1'])*scale + margin
    y1 = 60*scale + margin - df_bnd.loc[i, 'Dec1']*scale
    x2 = (360 - df_bnd.loc[i, 'RA2'])*scale + margin
    y2 = 60*scale + margin - df_bnd.loc[i, 'Dec2']*scale

    # Если линия проходит через меридиан 0 часов, то её нужно рисовать слева в левую часть карты и справа в правую часть,
    # то есть дважды. Ничего страшного, если будет часть линии за пределами карты.
    if x1 < 60*scale and x2 > 300*scale:
        draw_line_bnd(x1, x2-360*scale, y1, y2)
        draw_line_bnd(x1+360*scale, x2, y1, y2)
    elif x2 < 60*scale and x1 > 300*scale:
        draw_line_bnd(x1-360*scale, x2, y1, y2)
        draw_line_bnd(x1, x2+360*scale, y1, y2)
    else:
        draw_line_bnd(x1, x2, y1, y2)

# Функция рисования линий созвездий (астеризмов).
draw_line_cst = lambda x1, x2, y1, y2: fw.write(f'<line x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" stroke="#45ad6a" stroke-opacity="0.8" stroke-width="0.5"/>\n')

# Рисуем линии созвездий (астеризмы).
for i in range(df_lines.shape[0]):
    HIP1 = df_lines.loc[i, 'HIP1']
    HIP2 = df_lines.loc[i, 'HIP2']

    x1 = (360 - df_stars.loc[HIP1, 'RAdeg'])*scale + margin
    y1 = 60*scale + margin - df_stars.loc[HIP1, 'DEdeg']*scale
    x2 = (360 - df_stars.loc[HIP2, 'RAdeg'])*scale + margin
    y2 = 60*scale + margin - df_stars.loc[HIP2, 'DEdeg']*scale

    # Если линия проходит через меридиан 0 часов, то её нужно рисовать слева в левую часть карты и справа в правую часть,
    # то есть дважды. Ничего страшного, если будет часть линии за пределами карты.
    if x1 < 60*scale and x2 > 300*scale:
        draw_line_cst(x1, x2-360*scale, y1, y2)
        draw_line_cst(x1+360*scale, x2, y1, y2)
    elif x2 < 60*scale and x1 > 300*scale:
        draw_line_cst(x1-360*scale, x2, y1, y2)
        draw_line_cst(x1, x2+360*scale, y1, y2)
    else:
        draw_line_cst(x1, x2, y1, y2)

# Рисуем звёзды.
gamma = 1.6 # гамма-коррекция: уменьшаются диаметры звёзд 3-4m, чтобы лучше были видны более яркие
smax = 4.5 #  диметр звёзд 0m
vmag_convert = lambda Vmag: ((6.6 - Vmag)/6.6)**gamma * smax
for i in range(df_stars.shape[0]):
    if -60 <= df_stars.iloc[i, 2] <= 60:
        x = (360 - df_stars.iloc[i, 1])*scale + margin
        y = 60*scale + margin - df_stars.iloc[i, 2]*scale
        # r = 2.3 - df_stars.iloc[i, 0]/3
        r = vmag_convert(df_stars.iloc[i, 0])
        fw.write(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#E0E0E0" stroke-width="0"/>\n')

# Названия созвездий.
for i in range(df_cst.shape[0]):
    HIP = df_cst.loc[i, 'HIP_center']
    cst = df_cst.loc[i, 'Cst_short']
    try:
        RA = df_stars.loc[HIP, 'RAdeg']
        Dec = df_stars.loc[HIP, 'DEdeg']
    except:
        print(f'HIP {HIP} {cst} отсутствует в датасете.')
    else:
        if -60 <= Dec <= 60:
            x = (360 - RA)*scale + margin
            y = 60*scale + margin - Dec*scale
            fw.write(f'<text x="{x}" y="{y}" fill="#a0a0a0" font-size="11" text-anchor="middle">{cst}</text>\n')

fw.write('</svg>\n')
fw.close()


