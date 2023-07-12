import asyncio
from datetime import date, timedelta
import logging

import aiohttp
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK


# Забезпечимо логування у файл (рівень INFO) та всі логи у консоль
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()  # Логування в консоль
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
fh = logging.FileHandler("exchange.log")  # Логування в файл
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)


async def request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return str({
                                r["date"]: {
                                    "EUR": {
                                        "sale": r["exchangeRate"][8]["saleRate"],
                                        "purchase": r["exchangeRate"][8][
                                            "purchaseRate"
                                        ],
                                    },
                                    "USD": {
                                        "sale": r["exchangeRate"][23]["saleRate"],
                                        "purchase": r["exchangeRate"][23][
                                            "purchaseRate"
                                        ],
                                    },
                                }
                            })
                logging.debug(f'Error status {response.status} for {url}')
        except aiohttp.ClientConnectorError as e:
            logging.debug(f'Connection error {url}: {e}')
        return None


async def get_exchange():
    today_date = date.today().strftime("%d.%m.%Y")
    url_without_date = "https://api.privatbank.ua/p24api/exchange_rates?date="
    url = url_without_date + today_date
    res = await request(url)
    return res


async def get_exchange_few_days(amount_of_days):
    lst_dates = []
    today_date = date.today()  # Поточна дата
    counter = amount_of_days - 1
    while counter != 0:
        lst_dates.append((today_date - timedelta(days=counter)).strftime("%d.%m.%Y"))
        counter -= 1
    lst_dates.append(today_date.strftime("%d.%m.%Y"))
    url_without_date = "https://api.privatbank.ua/p24api/exchange_rates?date="
    urls_list = []
    for i in lst_dates:
        url = url_without_date + i
        urls_list.append(url)
    result = []
    for elem in urls_list:
        res = await request(elem)
        result.append(res)
    return result


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.debug(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.debug(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message == 'exchange':
                logging.info('Exchange command')
                r = await get_exchange()
                await self.send_to_clients(r)
            elif message.split()[0] == 'exchange' and 0 < int(message.split()[1]) <= 10:
                logging.info('Exchange command')
                r = await get_exchange_few_days(int(message.split()[1]))
                await self.send_to_clients(str(r))
            else:
                await self.send_to_clients(f"{ws.name}: {message}")



async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())