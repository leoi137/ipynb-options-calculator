import numpy as np
import pandas as pd
import datetime
import math
from scipy import stats
# from fast_arrow import StockMarketdata
# from live_option_data import GatherData

def option_calculator(kind, spot_price, strike, expiration, IV, time_taken = None, expected_date=None, IR = 0.75):

    if len(expiration.split('-')) ==3:
        year, month, day = expiration.split('-')
        expiration_date = datetime.datetime(int(year), int(month), int(day))
    else:
        year, month, day, hour, minute = expiration.split('-')
        expiration_date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))

    # year, month, day = expiration.split('-')
    # expiration_date = datetime.datetime(int(year), int(month), int(day))

    if time_taken is not None:

        today = datetime.datetime.today()
        diff = expiration_date - today

        if (today + datetime.timedelta(time_taken)).weekday() == 6: # If Sunday
            time_taken += 1
        if (today + datetime.timedelta(time_taken)).weekday() == 5: # If Saturday
            time_taken += 2
        if diff.days < 1:
            time = ((diff.seconds/86400) - time_taken)/365
        if diff.days >= 1:
            time = (diff.days - time_taken)/365

    if expected_date is not None:

        if len(expected_date.split('-')) ==3:
            year, month, day = expected_date.split('-')
            expected_date = datetime.datetime(int(year), int(month), int(day))
        else:
            year, month, day, hour, minute = expected_date.split('-')
            expected_date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))

        time_diff = expiration_date - expected_date
        time = ((time_diff.seconds + time_diff.days*86400)/3600)/8760
        # time = (expiration_date - expected_date).days/365
        # print(expiration_date, expected_date, (time_diff.seconds + time_diff.days*86400)/3600, time)
        # print(expiration_date, expected_date, ((expiration_date - expected_date).seconds/3600), time)

    d1_numerator = np.log(spot_price/strike) + (IR/100 + ((IV)**2)/2)*time
    d1 = d1_numerator / (IV*np.sqrt(time))
    d2 = d1 - IV*np.sqrt(time)
    # print(time)
    # print(d1_numerator, d1, d2)

    if kind.lower() == 'call':
        value = spot_price * stats.norm.cdf(d1) - (strike/np.exp((IR/100)*time))*stats.norm.cdf(d2)

    elif kind.lower() == 'put':
        value = (strike/np.exp((IR/100)*time))*stats.norm.cdf(-d2) - spot_price * stats.norm.cdf(-d1)

    return value

def get_option_prices(kind, spot, target, strike, expiration, IV_now, IV_expected, time_taken = None, expected_date=None, IR = 0.25):

    if time_taken is not None:
        spot_price = option_calculator(kind, spot, strike, expiration, IV, time_taken=0)
        target_price = option_calculator(kind, target, strike, expiration, IV, time_taken=time_taken)

    if expected_date is not None:
        right_now = datetime.datetime.now()
        right_now = f'{right_now.year}-{right_now.month}-{right_now.day}-{right_now.hour}-{right_now.minute}'
        spot_price = option_calculator(kind, spot, strike, expiration, IV=IV_now, expected_date=right_now)
        target_price = option_calculator(kind, target, strike, expiration, IV=IV_expected, expected_date=expected_date)

    print(f'Price: ${spot_price:0.4f}')
    print(f'Target: $ {target_price:0.4f}')
    print(f'Reward/Risk: {abs((target_price-spot_price)/spot_price)*100:0.2f} %')

def get_spread_option_prices(kind, stop, spot, target, strike_buy, strike_sell, expiration, IV_buy, IV_sell, time_taken = None, expected_date=None, IR = 0.25):

    stop_buy = option_calculator(kind, stop, strike_buy, expiration, IV=IV_buy, expected_date=expected_date)
    stop_sell = option_calculator(kind, stop, strike_sell, expiration, IV=IV_sell, expected_date=expected_date)

    spot_buy = option_calculator(kind, spot, strike_buy, expiration, IV_buy, time_taken=0)
    spot_sell = option_calculator(kind, spot, strike_sell, expiration, IV_sell, time_taken=0)

    target_buy = option_calculator(kind, target, strike_buy, expiration, IV=IV_buy, expected_date=expected_date)
    target_sell = option_calculator(kind, target, strike_sell, expiration, IV=IV_sell, expected_date=expected_date)

    stop_price = stop_buy - stop_sell
    spot_price = spot_buy - spot_sell
    target_price = target_buy - target_sell

    print(f'Stop Price: $ {stop_price:0.4f}')
    print(f'Buy Price : $ {spot_price:0.4f}')
    print(f'Target Price: $ {target_price:0.4f}')
    print(f'Reward: $ {(target_price-spot_price)*100:0.4f} -- {(target_price-spot_price)/((spot_price-stop_price))*100:0.2f}%')
    print(f'Loss: $ {(spot_price-stop_price)*100:0.4f}')


def get_reward_risk(kind, stop, spot, target, strike, expiration, IV, IV_e, expected_date):
    
    cost = option_calculator(kind, spot, strike, expiration, IV, time_taken=0)
    stop_loss = option_calculator(kind, stop, strike, expiration, IV_e, expected_date=expected_date)
    target_price = option_calculator(kind, target, strike, expiration, IV_e, expected_date=expected_date)
    loss = cost-stop_loss
    profit = target_price-cost
    
    print(f'Price: $ {cost:0.4f} - Stop: $ {stop_loss:0.4f} - Target: $ {target_price:0.4f}')
    print(f'Loss: $ {loss:0.2f} - Profit: $ {profit:0.2f}')
    print('----------------------------------------------')
    print(f'Reward/Risk Ratio: {abs(profit/loss)*100:0.2f} %')

# def get_reward_risk2(symbol, kind, stop, spot, target, strike, expiration, IV_e, expected_date, risk, IV_jump=0, show_iv_jumps=False):
    
#     expiration_base = '-'.join(expiration.split('-')[0:3])
#     GD = GatherData()
#     option_chain = GD.main(symbol, expiration_base, kind, strike)

#     today = datetime.datetime.now()
#     data_loc_df = GD.get_day_starts(GD.date_loc_Dict)
#     try:
#         start_index = data_loc_df.loc[f'{today.year}-{today.month}-{today.day}'][0]
#     except KeyError:
#         pass
#     else:
#         iv_difference = option_chain['implied_volatility'][start_index] - option_chain['implied_volatility'][start_index-1]
#         print(f'IV Jump: {iv_difference:0.3f}')

#     if show_iv_jumps:
#         iv_jumps = get_IV_openings(option_chain)
#         stats_IV_opening_jumps(iv_jumps)

#     right_now = datetime.datetime.now()
#     if right_now < datetime.datetime(right_now.year, right_now.month, right_now.day, 6, 30, 30):
#         print("Before Opening")
#         IV = option_chain['implied_volatility'][-1]+IV_jump
#     else:
#         IV = option_chain['implied_volatility'][-1]
    
#     IV_e = IV + (IV_e/100)
    
#     cost = option_calculator(kind, spot, strike, expiration, IV, time_taken=0)
#     stop_loss = option_calculator(kind, stop, strike, expiration, IV_e, expected_date=expected_date)*100//1/100
#     target_price = option_calculator(kind, target, strike, expiration, IV_e, expected_date=expected_date)*100//1/100
#     loss = round(cost,2)-stop_loss
#     profit = target_price-round(cost,2)
    
#     print(f'IV: {IV:0.4f} - Exected IV: {IV_e:0.4f}')
#     print(f'Price: $ {round(cost,2):0.3f} - Stop: $ {stop_loss:0.3f} - Target: $ {target_price:0.3f}')
#     print(f'Loss: $ {loss:0.3f} - Profit: $ {profit:0.3f}')
#     print('----------------------------------------------')
#     print(f'Reward/Risk Ratio: {abs(profit/loss)*100:0.2f} %')
#     print(f"Shares to Buy: {math.floor(risk/(loss*100))}")

def get_stats(stock_data):

    """
    This returns the mean and stdv or the high and low spread ohlc prices
    """
    mean_oc = np.mean(np.log(stock_data['close'][-30:]/stock_data['open'][-30:]))*100
    stdv_oc = np.std(np.log(stock_data['close'][-30:]/stock_data['open'][-30:]))*100
    print(f'Close/Open  -  Mean: {mean_oc:0.2f}% - Stdv: {stdv_oc:0.2f}%')

    mean_hl = np.mean(np.log(stock_data['high'][-30:]/stock_data['low'][-30:]))*100
    stdv_hl = np.std(np.log(stock_data['high'][-30:]/stock_data['low'][-30:]))*100
    print(f'High/Low  -  Mean: {mean_hl:0.2f}% - Stdv: {stdv_hl:0.2f}%')

    print('\n')

def stats_IV_opening_jumps(iv_jumps):
    
    differences = []
    
    for x, y in iv_jumps:
        differences.append(y-x)
    
    print(f"Opening IV Gaps -> Average: {np.mean(differences):0.4f} - STDV: {np.std(differences):0.4f}")


#################### DATA RELATED ####################

# def gather_rh_prices(client, symbol, span='5year', bounds='regular'):
#     # Gather Stock data and the closing deviation.
#     data = StockMarketdata.historical_quote_by_symbol(client, symbol, span, bounds)
#     data = pd.DataFrame(data['historicals'])[
#         ['begins_at', 'open_price', 'high_price', 'low_price', 'close_price']]
#     data['begins_at'] = data['begins_at'].astype('datetime64[ns]')
#     data.columns = ['date', 'open', 'high', 'low', 'close']
#     for col in data.columns[-4:]:
#         data[col] = data[col].astype('float64')
#     data['close pct'] = np.log(data['close']/data['close'].shift(1))
#     data.set_index('date', inplace = True)

#     return data.dropna()

def get_correlations(data1, data2):

    pearson = stats.pearsonr(data1, data2)
    spear = stats.spearmanr(data1, data2)
    kendall = stats.kendalltau(data1, data2)

    print(f'Pearson R: {pearson[0]:0.2f}')
    print(f'Spearman R: {spear.correlation:0.2f}')
    print(f'Kendalltau: {kendall.correlation:0.2f}')

def get_IV_openings(chain):
    
    started_day = False
    iv_openings = []

    for i in range(len(chain)):

        if chain.index[i].hour==6 and started_day==False:
#             print('Started Day')
            iv_openings.append([chain['implied_volatility'][i-1],chain['implied_volatility'][i]])
            started_day = True

        if chain.index[i].hour>6 and started_day==True:
            started_day = False
            
    return iv_openings