from pandas import DataFrame, Series
import pandas as pd; import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
import mpl_finance as mpf
#from matplotlib.finance import candlestick_ohlc
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY,YEARLY
from matplotlib.dates import MonthLocator,MONTHLY
import datetime as dt
import pylab
import tushare as ts
import talib

daylinefilespath = 'D:\\dayline\\'
stock_code = '603697.SH' #平安银行
MA1 = 7
MA2 = 15
startdate = '20190201'
enddate = '20190823'


def readstkData(rootpath, stockcode, sday, eday):

    # returndata = pd.DataFrame()
    # for yearnum in range(0,int((eday - sday).days / 365.25)+1):
    #     theyear = sday + dt.timedelta(days = yearnum * 365)
    #     # build file name
    #     filename = rootpath  + theyear.strftime('%Y') + '\\' + str(stockcode).zfill(6) + '.csv'

    #     try:
    #         pro = ts.pro_api("17b8e59d919b5cbf9ef3be5427d91ba7afda6803464776103fa8b0bd")
    #         rawdata = pro.daily(ts_code='000001.SZ', start_date='20190801')
    #         #rawdata = pd.read_csv(filename, parse_dates = True, index_col = 0, encoding = 'gbk')
    #     except IOError:
    #        raise Exception('IoError when reading dayline data file: ' + filename)

    #     returndata = pd.concat([rawdata, returndata])

    pro = ts.pro_api("17b8e59d919b5cbf9ef3be5427d91ba7afda6803464776103fa8b0bd")
    returndata = pro.daily(ts_code=stock_code, start_date=sday,end_date=eday)

    # Wash data
    # print(help(returndata.sort_index))
    returndata = returndata.sort_index(ascending=False)
    returndata.index.name = 'trade_date'
    returndata.drop('amount', axis=1, inplace = True)
    returndata.drop('ts_code', axis=1, inplace = True)
    returndata.drop('change', axis=1, inplace = True)
    returndata.drop('pct_chg', axis=1, inplace = True)
    returndata.drop('pre_close', axis=1, inplace = True)

    returndata['trade_date'] = pd.to_datetime(returndata['trade_date'],format='%Y%m%d')

    # print(returndata)
    return returndata

def main():

    # drop the date index from the dateframe & make a copy
    daysreshape = readstkData(daylinefilespath, stock_code, startdate, enddate)
    avg = daysreshape
    avg['Label1'] =  talib.SMA(daysreshape.close, 7)
    avg['Label2'] =  talib.SMA(daysreshape.close, 15)
    avg['60'] =  talib.SMA(daysreshape.close, 60)
    emaslow, emafast, macd = talib.MACD(daysreshape.close.values)
    ema9 = talib.MA(macd, 9)

    avg['emaslow'] = emaslow
    avg['emafast'] = emafast
    avg['macd'] = macd
    # avg['eamd'] = ema9 = talib.MA(macd, 9)
    print(avg)
    # convert the trade_date64 column in the dataframe to 'float days'
    daysreshape['trade_date'] = mdates.date2num(daysreshape['trade_date'].astype(dt.date))
    # print(daysreshape)
    # clean day data for candle view
    daysreshape.drop('vol', axis=1, inplace = True)
    daysreshape = daysreshape.reindex(columns=['trade_date', 'open', 'high', 'low', 'close', 'vol'])

    fig = plt.figure(facecolor='#07000d',figsize=(15,10))
    ax1 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, facecolor='#07000d')#
    #plotCandlestick(daysreshape,ax1)
    #plt.show()

def plotCandlestick(daysreshape,ax1):
    Av1 = talib.SMA(daysreshape.close, MA1)
    Av2 = talib.SMA(daysreshape.close, MA2)


    SP = len(daysreshape.trade_date.values[MA2-1:])
    # SP=len(daysreshape.trade_date.values[3-1:])

    mpf.candlestick_ohlc(ax1, daysreshape.values[-SP:], width=.8, colorup='#ff1717', colordown='#53c156')
    # mpf.candlestick2_ohlc(ax1,daysreshape.trade_date ,daysreshape['open'], daysreshape['high'],
        # daysreshape['low'], daysreshape['close'], width=.8, colorup='#ff1717', colordown='#53c156')

    Label1 = str(MA1)+' SMA'
    Label2 = str(MA2)+' SMA'

    ax1.plot(daysreshape.trade_date.values[-SP:],Av1[-SP:],'#e1edf9',label=Label1, linewidth=1.5)
    ax1.plot(daysreshape.trade_date.values[-SP:],Av2[-SP:],'#4ee6fd',label=Label2, linewidth=1.5)
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(15))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.yaxis.label.set_color("w")
    ax1.spines['bottom'].set_color("#5998ff")
    ax1.spines['top'].set_color("#5998ff")
    ax1.spines['left'].set_color("#5998ff")
    ax1.spines['right'].set_color("#5998ff")
    ax1.tick_params(axis='y', colors='w')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x', colors='w')
    plt.ylabel(stock_code)
    # plt.title('subplot 2',loc='right',fontstyle='italic')
    ax1.legend()
    plt.grid(True, linestyle='--')
# def noPlot():
     # plot an RSI indicator on top
    maLeg = plt.legend(loc=9, ncol=2, prop={'size':7},
                       fancybox=True, borderaxespad=0.)
    maLeg.get_frame().set_alpha(0.4)
    textEd = pylab.gca().get_legend().get_texts()
    pylab.setp(textEd[0:5], color = 'w')

    ax0 = plt.subplot2grid((6,4), (0,0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')
    rsi = talib.RSI(daysreshape.close)
    rsiCol = '#c1f9f7'
    posCol = '#386d13'
    negCol = '#8f2020'
    SP = len(daysreshape.trade_date.values[MA2-1:])
    ax0.plot(daysreshape.trade_date.values[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
    ax0.axhline(70, color=negCol)
    ax0.axhline(30, color=posCol)
    ax0.fill_between(daysreshape.trade_date.values[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=negCol, edgecolor=negCol, alpha=0.5)
    ax0.fill_between(daysreshape.trade_date.values[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=posCol, edgecolor=posCol, alpha=0.5)
    ax0.set_yticks([30,70])
    ax0.yaxis.label.set_color("w")
    ax0.spines['bottom'].set_color("#5998ff")
    ax0.spines['top'].set_color("#5998ff")
    ax0.spines['left'].set_color("#5998ff")
    ax0.spines['right'].set_color("#5998ff")
    ax0.tick_params(axis='y', colors='w')
    ax0.tick_params(axis='x', colors='w')
    plt.ylabel('RSI')
    ax2 = plt.subplot2grid((6,4), (5,0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')
    fillcolor = '#00ffe8'
    nslow = 26
    nfast = 12
    nema = 9
    emaslow, emafast, macd = talib.MACD(daysreshape.close.values)
    ema9 = talib.MA(macd, nema)
    ax2.plot(daysreshape.trade_date.values[-SP:], macd[-SP:], color='#4ee6fd', lw=2)
    ax2.plot(daysreshape.trade_date.values[-SP:], ema9[-SP:], color='#e1edf9', lw=1)
    ax2.fill_between(daysreshape.trade_date.values[-SP:], macd[-SP:]-ema9[-SP:], 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax2.spines['bottom'].set_color("#5998ff")
    ax2.spines['top'].set_color("#5998ff")
    ax2.spines['left'].set_color("#5998ff")
    ax2.spines['right'].set_color("#5998ff")
    ax2.tick_params(axis='x', colors='w')
    ax2.tick_params(axis='y', colors='w')
    plt.ylabel('MACD', color='w')
    ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))
    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(45)
    # 美化
    plt.suptitle(stock_code,color='w')
    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.setp(ax1.get_xticklabels(), visible=False)

    # Mark big event
    # TODO: Make a real case here
    idx = SP
    x = (daysreshape.trade_date.values[idx] -  daysreshape.trade_date.values.min())/ (daysreshape.trade_date.values.max() - daysreshape.trade_date.values.min())
    y = (daysreshape.high.values[idx] - daysreshape.high.values.min())/ (daysreshape.high.values.max()-daysreshape.close.values.min())
    print(daysreshape.trade_date.values[idx])
    print(daysreshape.trade_date.values.max())
    print(daysreshape.trade_date.values.min())
    print(x)
    print(y)
    ax1.annotate('BreakNews!',(daysreshape.trade_date.values[idx],daysreshape.high.values[idx]),
        xytext=(x - 0.02, y + 0.1), textcoords='axes fraction',
        arrowprops=dict(facecolor='white', shrink=0.05),
        fontsize=10, color = 'w',
        horizontalalignment='right', verticalalignment='bottom')

    plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)
def plotVol():
    # vol
    volumeMin = 0
    ax1v = ax1.twinx()
    ax1v.fill_between(daysreshape.trade_date.values[-SP:],volumeMin, daysreshape.vol.values[-SP:], facecolor='#00ffe8', alpha=.4)
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.grid(False)
    ###Edit this to 3, so it's a bit larger
    ax1v.set_ylim(0, 3*daysreshape.vol.values.max())
    ax1v.spines['bottom'].set_color("#5998ff")
    ax1v.spines['top'].set_color("#5998ff")
    ax1v.spines['left'].set_color("#5998ff")
    ax1v.spines['right'].set_color("#5998ff")
    ax1v.tick_params(axis='x', colors='w')
    ax1v.tick_params(axis='y', colors='w')

def plotMacd(daysreshape,ax1,SP):
    # plot an MACD indicator on bottom
    ax2 = plt.subplot2grid((6,4), (5,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
    fillcolor = '#00ffe8'
    nslow = 26
    nfast = 12
    nema = 9
    emaslow, emafast, macd = talib.MACD(daysreshape.close.values)
    ema9 = talib.MA(macd, nema)
    ax2.plot(daysreshape.trade_date.values[-SP:], macd[-SP:], color='#4ee6fd', lw=2)
    ax2.plot(daysreshape.trade_date.values[-SP:], ema9[-SP:], color='#e1edf9', lw=1)
    ax2.fill_between(daysreshape.trade_date.values[-SP:], macd[-SP:]-ema9[-SP:], 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax2.spines['bottom'].set_color("#5998ff")
    ax2.spines['top'].set_color("#5998ff")
    ax2.spines['left'].set_color("#5998ff")
    ax2.spines['right'].set_color("#5998ff")
    ax2.tick_params(axis='x', colors='w')
    ax2.tick_params(axis='y', colors='w')
    plt.ylabel('MACD', color='w')
    ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))
    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(45)
    # 美化
    plt.suptitle(stock_b_code,color='w')
    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.setp(ax1.get_xticklabels(), visible=False)

    # Mark big event
    # TODO: Make a real case here
    ax1.annotate('BreakNews!',(daysreshape.trade_date.values[155],Av1[155]),
        xytext=(0.8, 0.9), textcoords='axes fraction',
        arrowprops=dict(facecolor='white', shrink=0.05),
        fontsize=10, color = 'w',
        horizontalalignment='right', verticalalignment='bottom')

    plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)
    plt.show()
if __name__ == "__main__":
    main()