"""
Надання інформації по курсу валют 'EUR' та 'USD' від "Приватбанку" за вказану кількість останніх днів (до 10)
"""

import argparse
import asyncio
from datetime import date, timedelta
import logging
import platform

import aiohttp


parser = argparse.ArgumentParser(description="Amount of days")
parser.add_argument(
    dest="amount", help="Source folder"
)  # Введений аргумент поміщається в 'amount'
arg = parser.parse_args()  # Збирає разом всі аргументи
amount_of_days = int(
    arg.amount
)  # Призначаємо переданий аргумент amount змінній amount_of_days


# Підготуємо список дат, для яких необхідно надати дані по курсах валют
lst_dates = []
today_date = date.today()  # Поточна дата
counter = amount_of_days - 1
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

result = []


async def main():
    async with aiohttp.ClientSession() as session:
        for url in urls_list:
            try:
                async with session.get(url) as response:
                    if response.status == 200:  # Перевірка існування сторінки
                        html = await response.json()
                        result.append(
                            {
                                html["date"]: {
                                    "EUR": {
                                        "sale": html["exchangeRate"][8]["saleRate"],
                                        "purchase": html["exchangeRate"][8][
                                            "purchaseRate"
                                        ],
                                    },
                                    "USD": {
                                        "sale": html["exchangeRate"][23]["saleRate"],
                                        "purchase": html["exchangeRate"][23][
                                            "purchaseRate"
                                        ],
                                    },
                                }
                            }
                        )
                    else:
                        logging.error(f"Error status {response.status} for {url}")
            except aiohttp.ClientConnectorError as e:
                logging.error(f"Connection error {url}: {e}")
    return result


if __name__ == "__main__":
    if amount_of_days > 10:
        print("Amount must be <10!")
    else:
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        result = asyncio.run(main())
        print(result)


# Приклад введення команди в термінал
# python main.py 2

# Приклад виводу в терміналі:
# [{'08.07.2023': {'EUR': {'sale': 40.85, 'purchase': 39.85}, 'USD': {'sale': 37.2, 'purchase': 36.6}}},
# {'09.07.2023': {'EUR': {'sale': 40.85, 'purchase': 39.85}, 'USD': {'sale': 37.2, 'purchase': 36.6}}}]
