
import re
import requests
import datetime

# Функция для расчёта полной купонной доходности
def xirr(transactions):
    years = [(ta[0] - transactions[0][0]).days / 365.0 for ta in transactions]
    residual = 1
    step = 0.05
    guess = 0.05
    epsilon = 0.0001
    limit = 10000
    while abs(residual) > epsilon and limit > 0:
        limit -= 1
        residual = 0.0
        for i, ta in enumerate(transactions):
            residual += ta[1] / pow(guess, years[i])
        if abs(residual) > epsilon:
            if residual > 0:
                guess += step
            else:
                guess -= step
                step /= 2.0
    return guess-1

# Вводим ISIN
while True:
    try:
        ISIN = input('Введите ISIN облигации по которой требуется произвести расчёт купонной доходности: ').upper().strip()
        URL_ISIN = 'http://bonds.finam.ru/issue/search/default.asp?emitterCustomName=' + ISIN
        Res_URL_ISIN = requests.get(URL_ISIN)
        Code_Finam = re.search(r'details(\w{5})\/default.asp', Res_URL_ISIN.text).group(1)
        break
    except:
        print('Вы неверно ввели ISIN')

# Парсим страницу платежей.
URL_Pays = 'http://bonds.finam.ru/issue/details' + Code_Finam + '00002/default.asp'

Res_URL_Pays = requests.get(URL_Pays)
try:
    Bonds_Pays = [(datetime.datetime.strptime(re.search(r'(\d{2}\.\d{2}\.\d{4})', Res_URL_Pays.text).group(0),
                                              '%d.%m.%Y').date(), '', '', '', 0, 0)]
    Bonds_Pays += re.findall(r'(\d{2}\.\d{2}\.\d{4})&nbsp;<\/font><\/td><td align=right>'
                            r'([^&]*)&nbsp;<\/td><td align=right>([^&]*)&nbsp;&nbsp;<\/td><td align=right>'
                            r'([^&]*)&nbsp;[^>]*><td align=right>'
                            r'([^&]*)[^<]*<\/td><td align=right style="vertical-align:middle; ">'
                            r'([^&]*)', Res_URL_Pays.text)
except:
    print('Не удалось распасить страницу платежей')

Res_URL_Pays.encoding = 'cp1251'
Bond_Nominal = int(re.findall('Номинал:&nbsp;<span>(\d{0,3}\s\d*)</span>&nbsp;',
                              Res_URL_Pays.text)[0].replace('\xa0', '').replace(' ', ''))

# Парсим страницу оферт, если она есть. В противном случае будет одна дата оферты = дате погашения.
URL_Offers = 'http://bonds.finam.ru/issue/details' + Code_Finam + '00003/default.asp'
Res_URL_Offers = requests.get(URL_Offers)

try:
    Bonds_Offers = re.findall(r'(\d{2}\.\d{2}\.\d{4})[^100]*100%', Res_URL_Offers.text)
    Bonds_Offers.append(Bonds_Pays[-1][0])
except:
    print('Не удалось распарсить страницу оферт')

# Меняем формат ячеек в сформированной таблице платежей и списке оферт.
# В случае если купоны будущих платежей ещё не определены задаём по последнему известному.
if not Bonds_Pays[-1][1]:
    print('Облигация с переменным купоном, часть из которых ещё неизвестна и будет проставлена по последнему известному')

for i in range(1, len(Bonds_Pays)):
    Bonds_Pays[i] = [datetime.datetime.strptime(Bonds_Pays[i][0], '%d.%m.%Y').date(),
                     Bonds_Pays[i][1], Bonds_Pays[i][2], Bonds_Pays[i][3],
                     Bonds_Pays[i][4], Bonds_Pays[i][5]]
    if Bonds_Pays[i][1]:
        Bonds_Pays[i][1] = float(Bonds_Pays[i][1].replace(',', '.').replace('%', ''))
    else:
        Bonds_Pays[i][1] = Bonds_Pays[i - 1][1]
    if Bonds_Pays[i][4]:
        Bonds_Pays[i][4] = float(Bonds_Pays[i][4])
        Bonds_Pays[i][5] = float(Bonds_Pays[i][5])
    else:
        Bonds_Pays[i][4] = 0
        Bonds_Pays[i][5] = 0
print('Список платежей')
for i in Bonds_Pays:
    print(i)

for i in range(len(Bonds_Offers)):
    Bonds_Offers[i] = datetime.datetime.strptime(Bonds_Offers[i], '%d.%m.%Y').date()
print('Список дат оферт/погашений:\n', Bonds_Offers)

# Задаём дату покупки облигации
while True:
    try:
        Day_Input = input('Введите дату покупки в формате DD.MM.YYYY. Или нажмите Enter,'
                          ' если покупка будет осуществлена сегодня: ')
        if not Day_Input:
            Day_Bay = datetime.date.today()
            break
        else:
            Day_Bay = datetime.datetime.strptime(Day_Input, '%d.%m.%Y').date()
            if Bonds_Pays[0][0]<= Day_Bay <= Bonds_Pays[-1][0]:
                break
    except:
        print('Вы неверно ввели дату')

print('Day_Bay =', Day_Bay)

# Задаём цену покупки в %
while True:
    try:
        Bond_Bay_Percent = float((input('Задайте цену покупки в %')).replace(',', '.')) / 100
        break
    except:
        print('Вы неверно задали цену')

# Задаём комиссию брокера
while True:
    try:
        Commission_Broker = input('Если ваша комиссия 0,0513%(Инвестор стандарт на ВТБ - 0,0413% + 0,01% МосБиржа) '
                                  'нажмите Enter или задайте свою:')
        print(Commission_Broker)
        if Commission_Broker:
            Commission_Broker = float(Commission_Broker.replace(',', '.'))/100
        else:
            Commission_Broker = 0.000513
        break
    except:
        print('Вы неверно задали комиссию. Попробуйте ещё раз.')


# Расчёт НКД к уплате:
Bond_Nominal_Current = Bond_Nominal
for i in range(len(Bonds_Pays) - 1):
    Bond_Nominal_Current -= Bonds_Pays[i][-1]
    if Bonds_Pays[i][0] <= Day_Bay < Bonds_Pays[i + 1][0]:
        NKD = Bond_Nominal_Current * Bonds_Pays[i + 1][1] / 100 * ((Day_Bay - Bonds_Pays[i][0]).days / 365)
        break

# Определяем полную цену покупки
print('При покупке облигации мы заплатим:' + str(Bond_Nominal_Current * Bond_Bay_Percent) + ' + НКД: ' + str(NKD), end='')
print('+ комиссия брокера' + str((Bond_Nominal_Current * Bond_Bay_Percent) * Commission_Broker))
Bond_Bay = Bond_Nominal_Current * Bond_Bay_Percent + NKD + (Bond_Nominal_Current * Bond_Bay_Percent) * Commission_Broker
print('Итого без комиссии:', Bond_Nominal_Current * Bond_Bay_Percent + NKD)
print('Итого с комиссией:', Bond_Bay)

# Цена продажи. Будет выщитана, как остаток номинала к оферте, если гасить будем в день оферты.
Bond_Say = 0.0

# Задаём дату продажи облигации
while True:
    try:
        print('Даты оферт и погашения: ', Bonds_Offers)
        Day_Say = datetime.datetime.strptime(input('Введите дату продажи в формате DD.MM.YYYY:'), '%d.%m.%Y').date()
        if Bonds_Pays[0][0] <= Day_Say <= Bonds_Pays[-1][0] and Day_Say >= Day_Bay:
            if Day_Say not in Bonds_Offers:
                while True:
                    try:
                        Bond_Say = float(input('Т.к. цена продажи не совпадает с датой оферты/'
                                         'погашения введите планируемую цену продажи в % без НКД: ').replace(',', '.'))\
                                   * Bond_Nominal_Current
                        break
                    except:
                        print('Вы неверно задали цену')
            break
    except:
        print('Вы неверно ввели дату')

print('Day_Say =', Day_Say)

# Список данных денежного потока
Money_Back = [(Day_Bay, round(-Bond_Bay, 2))]

# Кол-во дней владения облигацией
Bond_Days = (Day_Say - Day_Bay).days

# Расчёт денежного потока
for i in range(len(Bonds_Pays) - 1):
    Bond_Nominal -= Bonds_Pays[i][-1]
    if Bonds_Pays[i][0] <= Day_Bay < Bonds_Pays[i + 1][0] and Bonds_Pays[i][0] < Day_Say:
        print('Bond_Nominal', Bond_Nominal)
        NKD = Bond_Nominal * Bonds_Pays[i + 1][1] / 100 * (
                    (Bonds_Pays[i + 1][0] - Bonds_Pays[i][0]).days / 365)
        print('NKD', NKD)
        Money_Back.append((Bonds_Pays[i + 1][0], round(NKD + Bonds_Pays[i + 1][-1], 2)))
        Day_Bay = Bonds_Pays[i + 1][0]
    elif Day_Bay >= Day_Say:
        NKD = Bond_Nominal * Bonds_Pays[i + 1][1] / 100 * (
                (Day_Say - Bonds_Pays[i][0]).days / 365)
        Money_Back[-1] = (Day_Say, round(NKD + Money_Back[-1][1] + Bond_Nominal_Current, 2))
        break


print('Денежный поток:')
for money in Money_Back:
    print(money)

print('Доходность к погашению простая = ' + str(round(sum([money[1] for money in Money_Back]) /
                                                      Bond_Bay / (Bond_Days / 365) * 100, 2)) + '%')

print ('Доходность к погашению полная = ' + str(round(xirr(Money_Back) * 100, 2)) + '%')



