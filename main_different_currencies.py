"""
Надання інформації по курсу валют 'EUR' та 'USD' від "Приватбанка" за вказану кількість останніх днів (до 10).
Також має функцію надання інформації по курсах інших валют ("PLZ", "GBP", "CHF").
"""

import argparse
import asyncio
from datetime import date, timedelta
import logging
import platform

import aiohttp


parser = argparse.ArgumentParser()
parser.add_argument(
    "-am", dest="amount", help="Amount of days", type=int
)  # Введений аргумент поміщається в 'amount'
parser.add_argument(
    "-cur", dest="currency", help="PLZ or GBP or CHF"
)  # Додаткові варіанти валют

args = parser.parse_args()  # Збирає разом всі аргументи
print(args)


# Підготуємо список дат, для яких необхідно надати дані по курсах валют
if 0 < args.amount <= 10:
    lst_dates = []
    today_date = date.today()  # Поточна дата
    counter = args.amount - 1
    while counter != 0:
        lst_dates.append((today_date - timedelta(days=counter)).strftime("%d.%m.%Y"))
        counter -= 1
    lst_dates.append(today_date.strftime("%d.%m.%Y"))

    # Підготуємо список url для формування запитів
    url_without_date = "https://api.privatbank.ua/p24api/exchange_rates?date="
    urls_list = []
    for i in lst_dates:
        url = url_without_date + i
        urls_list.append(url)


def get_info_from_json(html, argument: args.currency):
    """Повертає список зі словниками курсів валют з тексту json"""

    result = {}
    if argument == None:
        result[html["date"]] = {
            "EUR": {
                "sale": html["exchangeRate"][8]["saleRate"],
                "purchase": html["exchangeRate"][8]["purchaseRate"],
            },
            "USD": {
                "sale": html["exchangeRate"][23]["saleRate"],
                "purchase": html["exchangeRate"][23]["purchaseRate"],
            },
        }
    if argument == "PLZ":
        result[html["date"]] = {
            "EUR": {
                "sale": html["exchangeRate"][8]["saleRate"],
                "purchase": html["exchangeRate"][8]["purchaseRate"],
            },
            "USD": {
                "sale": html["exchangeRate"][23]["saleRate"],
                "purchase": html["exchangeRate"][23]["purchaseRate"],
            },
            "PLZ": {
                "sale": html["exchangeRate"][17]["saleRate"],
                "purchase": html["exchangeRate"][17]["purchaseRate"],
            },
        }
    if argument == "GBP":
        result[html["date"]] = {
            "EUR": {
                "sale": html["exchangeRate"][8]["saleRate"],
                "purchase": html["exchangeRate"][8]["purchaseRate"],
            },
            "USD": {
                "sale": html["exchangeRate"][23]["saleRate"],
                "purchase": html["exchangeRate"][23]["purchaseRate"],
            },
            "GBP": {
                "sale": html["exchangeRate"][9]["saleRate"],
                "purchase": html["exchangeRate"][9]["purchaseRate"],
            },
        }
    if argument == "CHF":
        result[html["date"]] = {
            "EUR": {
                "sale": html["exchangeRate"][8]["saleRate"],
                "purchase": html["exchangeRate"][8]["purchaseRate"],
            },
            "USD": {
                "sale": html["exchangeRate"][23]["saleRate"],
                "purchase": html["exchangeRate"][23]["purchaseRate"],
            },
            "CHF": {
                "sale": html["exchangeRate"][4]["saleRate"],
                "purchase": html["exchangeRate"][4]["purchaseRate"],
            },
        }
    return result


async def main():
    result_total = []
    async with aiohttp.ClientSession() as session:
        for url in urls_list:
            try:
                async with session.get(url) as response:
                    if response.status == 200:  # Перевірка існування сторінки
                        html = await response.json()
                        result_total.append(get_info_from_json(html, args.currency))
                    else:
                        logging.error(f"Error status {response.status} for {url}")
            except aiohttp.ClientConnectorError as e:
                logging.error(f"Connection error {url}: {e}")
    return result_total


if __name__ == "__main__":
    if args.amount > 10 or args.amount == 0:
        print("Amount must be 1...10!")
    else:
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        result = asyncio.run(main())
        print(result)


# Приклад введення команди в термінал
# python main_different_currencies.py -am 2 -cur PLZ

# Приклад виводу в терміналі:
# [{'09.07.2023': {'EUR': {'sale': 40.85, 'purchase': 39.85}, 'USD': {'sale': 37.2, 'purchase': 36.6},
# 'PLZ': {'sale': 9.006, 'purchase': 8.8884}}}, {'10.07.2023': {'EUR': {'sale': 40.85, 'purchase': 39.85},
# 'USD': {'sale': 37.2, 'purchase': 36.6}, 'PLZ': {'sale': 9.006, 'purchase': 8.8884}}}]
