from Settings import *


def get_sl(op: str, price: list, p_size: float, acc_balance: float, ent_price: float, p_p: int, s_fact: float) -> float:
    stop_price: float = 0.0
    risk_amount_usd = inp_risk * 0.01 * acc_balance
    trade_size_usd = p_size * ent_price
    stop_percent: float = (risk_amount_usd / trade_size_usd)
    if use_trail:
        if op == "BUY":
            stop_factor: float = 1 - stop_percent
            profit: float = float(price[0].close) - ent_price
            if profit > 0:
                length = float(price[0].close) - float(price[0].close) * stop_factor
                stop_price = round(float(price[0].close) - (length - (profit * s_fact)), p_p)
            else:
                stop_price = round(ent_price * stop_factor, p_p)

        if op == "SELL":
            stop_factor: float = 1 + stop_percent
            profit = ent_price - float(price[0].close)
            if profit > 0:
                length = float(price[0].close) * stop_factor - float(price[0].close)
                stop_price = round(float(price[0].close) + (length - (profit * s_fact)), p_p)
            else:
                stop_price = round(ent_price * stop_factor, p_p)

    if not use_trail:
        if op == "BUY":
            stop_factor: float = 1 - stop_percent
            stop_price = round(ent_price * stop_factor, p_p)
        if op == "SELL":
            stop_factor: float = 1 + stop_percent
            stop_price = round(ent_price * stop_factor, p_p)
    if stop_price == 0:
        print("Error calculating stop loss")
    return stop_price


def get_tp(op: str, trade_size: float, acc_balance: float, ent_price: float, p_p: int) -> float:
    tp_price: float = 0
    risk_amount_usd = inp_risk * 0.01 * acc_balance
    trade_size_usd = trade_size * ent_price
    stop_percent: float = (risk_amount_usd / trade_size_usd)
    if op == "BUY":
        tp_factor: float = 1 + inp_tp * stop_percent
        tp_price = round(ent_price * tp_factor, p_p)
    if op == "SELL":
        tp_factor: float = 1 - inp_tp * stop_percent
        tp_price = round(ent_price * tp_factor, p_p)
    if tp_price == 0:
        print("Error calculating take profit level")
    return tp_price
