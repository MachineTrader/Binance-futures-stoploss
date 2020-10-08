from binance_f import RequestClient
from OnSeconds import on_seconds
import time
from binance_f.base.printobject import *
from colorama import *
from Settings import *

client = RequestClient(api_key=g_api_key, secret_key=g_secret_key, url="https://fapi.binance.com")

human_response = ""
while human_response != "y" and human_response != "n":
    human_response: str = input("Update leverage and leverage mode?[y/n]")


ExchangeInfo = client.get_exchange_information()
# Set starting time
last_time = 0

# Set margin to Isolated or Crossed
if human_response == "y" or human_response == "Y":
    for Symbol in ExchangeInfo.symbols:
        pair = Symbol.baseAsset + "USDT"
        try:
            result = client.change_margin_type(symbol=pair, marginType=margin_type)
        except:
            print(Fore.RED+"Failed set margin type on " + pair + Fore.WHITE)

        leverage_result: any = None
        try:
            leverage_result = client.change_initial_leverage(symbol=pair, leverage=inp_lev)
        except:
            PrintBasic.print_obj(leverage_result)


while True:
    try:
        positions = client.get_position()
    except ConnectionError:
        print("Can't get positions for further processing...")
        continue

    # Get balance
    try:
        balance_list: list = client.get_balance()
    except ConnectionError:
        print("Can't reach server for balance...")
        time.sleep(5)
        continue

    my_balance = float(balance_list[0].balance)

    for pos in positions:
        if pos.entryPrice != 0:
            on_seconds(client, pos, ExchangeInfo, my_balance)

    time.sleep(sleep_seconds)
