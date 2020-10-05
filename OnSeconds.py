from binance_f.model.order import *
from binance_f.model.exchangeinformation import ExchangeInformation
from binance_f.base.printobject import *
from Settings import *
from colorama import *
from Methods import get_sl, get_tp


def on_seconds(client, pos, exchange_info: ExchangeInformation, acc_balance: float):
    # TAKE PROFIT / STOP LOSS
    try:
        open_orders = client.get_open_orders()
    except ConnectionError:
        print("Can't get orders for take profit function...")
        return

    # Get symbol last candle
    try:
        price = client.get_candlestick_data(symbol=pos.symbol, interval=time_frame, startTime=None, endTime=None,
                                            limit=2)
    except ConnectionError:
        print("Can't reach server for candles...")
        return

    # Set price list object as time series
    price.reverse()

    # Get precision
    p_p, q_p = 0.0, 0.0
    for Symbol in exchange_info.symbols:
        if pos.symbol == Symbol.baseAsset + "USDT":
            p_p, q_p = Symbol.pricePrecision, Symbol.quantityPrecision

    # Check if tp and sl orders exists
    short_pos_tp_exists_already, long_pos_tp_exists_already = False, False
    short_pos_sl_exists_already, long_pos_sl_exists_already = False, False
    update_long_sl, update_short_sl = True, True

    if float(pos.positionAmt) > 0:  # Long
        long_sl = get_sl("BUY", price, pos.positionAmt, acc_balance, float(pos.entryPrice), p_p, short_factor)
        long_tp = get_tp("BUY", pos.positionAmt, acc_balance, float(pos.entryPrice), p_p)
        for order in open_orders:
            if order.symbol == pos.symbol:
                # SL
                if order.side == OrderSide.SELL and order.type == OrderType.STOP_MARKET:
                    other_sell_stop_id: str = ""
                    if use_trail:
                        if float(order.origQty) == float(pos.positionAmt):
                            if long_sl > float(order.stopPrice):
                                other_sell_stop_id = order.orderId  # Send old order to deletion
                            elif float(order.stopPrice) == long_sl:
                                long_pos_sl_exists_already = True
                            else:
                                update_long_sl = False
                        else:
                            other_sell_stop_id = order.orderId

                    if not use_trail:
                        if float(order.stopPrice) == long_sl and float(order.origQty) == float(pos.positionAmt):
                            long_pos_sl_exists_already = True
                        else:
                            other_sell_stop_id = order.orderId

                    # Remove any extra sl
                    if other_sell_stop_id != "":  # Delete old sl
                        cancel_result = Order()
                        try:
                            cancel_result = client.cancel_order(symbol=pos.symbol, orderId=other_sell_stop_id)
                        except:
                            PrintBasic.print_obj(cancel_result)
                            print("^ Can't delete short order", pos.symbol, other_sell_stop_id)

                # TP
                if use_tp and order.side == OrderSide.SELL and order.type == OrderType.LIMIT:
                    other_sell_order_id: str = ""
                    if float(order.price) == long_tp:
                        long_pos_tp_exists_already = True
                    else:
                        other_sell_order_id = order.orderId

                    # Remove any extra tp
                    cancel_result = Order()
                    if other_sell_order_id != "":  # Delete old tp
                        try:
                            cancel_result = client.cancel_order(symbol=pos.symbol, orderId=other_sell_order_id)
                        except:
                            PrintBasic.print_obj(cancel_result)

        # Add TP
        if use_tp and pos.positionAmt > 0 and not long_pos_tp_exists_already:
            result = Order()
            try:
                # random_int = randint(1, 1000)
                result = client.post_order(
                    symbol=pos.symbol, side=OrderSide.SELL, ordertype=OrderType.LIMIT,
                    # newClientOrderId=client_order_id+random_int,
                    quantity=str(round(float(pos.positionAmt), q_p)),
                    timeInForce=TimeInForce.GTC, price=str(long_tp))
                PrintBasic.print_obj(result)
            except:
                PrintBasic.print_obj(result)
                print(Fore.RED, " Failed to create limit tp for", pos.symbol, Fore.WHITE)

        # Add SL
        if ((not use_trail and pos.positionAmt > 0 and not long_pos_sl_exists_already) or
                (use_trail and pos.positionAmt > 0 and not long_pos_sl_exists_already and update_long_sl)):
            result = Order()
            try:
                # random_int = randint(1, 1000)
                result = client.post_order(
                    symbol=pos.symbol, side=OrderSide.SELL, ordertype=OrderType.STOP_MARKET,
                    # newClientOrderId=client_order_id+random_int,
                    quantity=str(round(float(pos.positionAmt), q_p)),
                    reduceOnly=True,
                    stopPrice=str(long_sl))
                PrintBasic.print_obj(result)
            except:
                PrintBasic.print_obj(result)

    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

    # Short
    if float(pos.positionAmt) < 0:
        short_sl = get_sl("SELL", price, pos.positionAmt * -1, acc_balance, float(pos.entryPrice), p_p, short_factor)
        short_tp = get_tp("SELL", pos.positionAmt * -1, acc_balance, float(pos.entryPrice), p_p)
        for order in open_orders:
            if order.symbol == pos.symbol:
                # SL
                if order.side == OrderSide.BUY and order.type == OrderType.STOP_MARKET:
                    other_buy_stop_id: str = ""
                    if use_trail:
                        #  print(Fore.RED, "Org qty:", order.origQty, " Pos amt:", pos.positionAmt)
                        if float(order.origQty) == float(pos.positionAmt)*-1:
                            if short_sl < float(order.stopPrice):
                                other_buy_stop_id = order.orderId  # Send old order to deletion
                            elif float(order.stopPrice) == short_sl:
                                short_pos_sl_exists_already = True
                            else:
                                update_short_sl = False
                        else:
                            other_buy_stop_id = order.orderId

                    if not use_trail:
                        if float(order.stopPrice) == short_sl and float(order.origQty) == float(pos.positionAmt)*-1:
                            short_pos_sl_exists_already = True
                        else:
                            other_buy_stop_id = order.orderId

                    # Remove any extra sl
                    if other_buy_stop_id != "":  # Delete old sl
                        cancel_result = Order()
                        try:
                            cancel_result = client.cancel_order(symbol=pos.symbol, orderId=other_buy_stop_id)
                        except:
                            PrintBasic.print_obj(cancel_result)
                            print("^ Can't delete long order", pos.symbol, other_buy_stop_id)

                # TP
                if use_tp and order.side == OrderSide.BUY and order.type == OrderType.LIMIT:
                    other_buy_order_id: str = ""
                    if float(order.price) == short_tp:
                        short_pos_tp_exists_already = True
                    else:
                        other_buy_order_id = order.orderId

                    # Remove any extra tp
                    cancel_result = Order()
                    if other_buy_order_id != "":  # Delete old tp
                        try:
                            cancel_result = client.cancel_order(symbol=pos.symbol, orderId=other_buy_order_id)
                        except:
                            PrintBasic.print_obj(cancel_result)
                            print("^ Can't delete long order", pos.symbol, other_buy_order_id)

        # If sell position create buy limit tp
        if use_tp and pos.positionAmt < 0 and not short_pos_tp_exists_already:
            result = Order()
            try:
                # random_int = randint(1, 1000)
                result = client.post_order(
                    symbol=pos.symbol, side=OrderSide.BUY, ordertype=OrderType.LIMIT,
                    # newClientOrderId=client_order_id+random_int,
                    quantity=str(round(float(pos.positionAmt) * -1, q_p)),
                    timeInForce=TimeInForce.GTC, price=str(short_tp))
                PrintBasic.print_obj(result)
            except:
                PrintBasic.print_obj(result)
                print(Fore.RED, "^ Failed to create limit tp for", pos.symbol, Fore.WHITE)

            #  If sell position create buy limit tp
        if ((not use_trail and pos.positionAmt < 0 and not short_pos_sl_exists_already) or
                (use_trail and pos.positionAmt < 0 and not short_pos_sl_exists_already and update_short_sl)):

            result = Order()
            try:
                # random_int = randint(1, 1000)
                result = client.post_order(
                    symbol=pos.symbol, side=OrderSide.BUY, ordertype=OrderType.STOP_MARKET,
                    # newClientOrderId=client_order_id+random_int,
                    quantity=str(round(float(pos.positionAmt) * -1, q_p)),
                    reduceOnly=True,
                    stopPrice=str(short_sl))
                PrintBasic.print_obj(result)
            except:
                PrintBasic.print_obj(result)
