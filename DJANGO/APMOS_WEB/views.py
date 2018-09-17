# encoding:utf-8
from datetime import datetime, timedelta
import json
import os
import sys
import logging
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
import pymysql.cursors
from sqlalchemy import create_engine
import pandas as pd

from APMOS_WEB.models import Trade, User

# 数据库
ENGINE = create_engine('mysql://apmos:APCap1101!@:3306/apmosdb')
# fee_apcode_mapping
PATH_FEEAPCODEMAPPING = '/home/WindowsShared/APMOS/Dependent_Files/Common_files/FeeDaily/fee_apcode_mapping.csv'
PATH_CONTRACTS='/home/WindowsShared/APMOS/Dependent_Files/Common_files/FeeDaily/contracts/all_contrats.csv'
PATH_UPDATE = '/home/WindowsShared/APMOS/Dependent_Files/Fee_Files/UpdateAPMOS/'
PATH_STORE_FILE = '/home/WindowsShared/APMOS/Result/APMOS_website/'

DATABASE_NAME = 'apmosdb'

# 日志
daily_time = str(datetime.now()).split(' ')[0].replace('-','')
PATH_BROKER_APMOS = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO,filename=PATH_BROKER_APMOS + '/log/book_traderid.' + daily_time + '.log',format="%(levelname)s:%(asctime)s:%(message)s")


# 定义用户名密码
class UserFrom(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


# 定义登陆
def Login(request):
    if request.method == 'POST':
        uf = UserFrom(request.POST)
        # 如果uf是有效的
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            # 对比输入的用户名和密码和数据库中是否一致
            userPassJudge = User.objects.filter(username__exact=username, password__exact=password)
            # 如果正确则登陆成功，否则跳转为index页面
            if userPassJudge:
                response = HttpResponseRedirect('/index/')
                response.set_cookie('cookie_username', username, 36000)
                response.set_cookie('cookie_password', password, 36000)
                return response
            # 否则跳转到登陆页
            else:
                return render(request, 'login.html', {'uf': uf})
    else:
        uf = UserFrom()
    return render(request, 'login.html', {'uf': uf})


# About Website
def AboutWebsite(request):
    username = request.COOKIES.get('cookie_username')
    password = request.COOKIES.get('cookie_password')
    if (username == 'apmos') and (password == 'APMOS'):
        return render(request,'about_website.html')
    else:
        response = HttpResponseRedirect('/login/')
        return response

# 默认页面为昨天的数据
def Index(request):
    username = request.COOKIES.get('cookie_username')
    password = request.COOKIES.get('cookie_password')
    if (username == 'apmos') and (password == 'APMOS'):
        return render(request, 'index.html')
    else:
        response = HttpResponseRedirect('/login/')
        return response

#bbticker查询
def BBticker2Apcode(request):
    username = request.COOKIES.get('cookie_username')
    password = request.COOKIES.get('cookie_password')
    if (username == 'apmos') and (password == 'APMOS'):
        df=pd.read_csv(PATH_CONTRACTS,error_bad_lines=False)
        feed_mapping=pd.read_csv(PATH_FEEAPCODEMAPPING,error_bad_lines=False)
        feed_mapping=feed_mapping[['ap_code','feedcode']]
        df=pd.merge(df,feed_mapping,how='left')
        df=df[['ap_code','bb_ticker','feedcode']]
        df = df.to_dict(orient='records')
    return render(request, 'bb_ticker2apcode.html', {'df': df})


# ap_code
def ApmosApcode(q):
        try:
            q_list = q.split(',')
            q = q_list[0]
            # 查询
            cache = pd.read_sql_query("SELECT * FROM Trade WHERE ap_code ='" + q + "'", con=ENGINE)
            # cache = pd.merge(cache, mapping, how='left')
            cache.sort_values(by=['trade_datetime'], inplace=True, ascending=False)
            cache['trade_datetime'] = cache['trade_datetime'].astype('str')
            cache.reset_index(drop=True, inplace=True)
            cache.reset_index(inplace=True)
            df = cache.to_dict(orient='records')
            # 按时间统计
            cache['volume'] = cache['volume'].astype('int')
            cache['trade_datetime'] = cache['trade_datetime'].astype('str')
            cache['trade_datetime'] = cache['trade_datetime'].str.split(' ', expand=True)[0]
            cache_2 = pd.DataFrame()
            cache_2 = cache_2.append(
                pd.DataFrame(cache['volume'].groupby([cache['trade_datetime'], cache['account'], cache['side']]).sum()))
            cache_2.reset_index(inplace=True)
            cache_2['ap_code'] = q
            cache_2.sort_values(by='trade_datetime', inplace=True, ascending=False)
            if len(cache_2) >= 5:
                cache_2 = cache_2[0:5]  # 只保留前三行
            total_sum = cache_2.to_dict(orient='records')
            # 如果没有index求和查询
            if len(q_list) == 1:
                total_volume=0
                return (df, total_sum,total_volume,q_list)
            # 如果有index求和查询
            elif len(q_list) == 3:
                q_start = q_list[1]
                q_end = q_list[2]
                df_index = cache[int(q_start):int(q_end) + 1]
                a = df_index[df_index['side'] == 'Sell'].index
                df_index['volume'] = df_index['volume'].astype('float')
                if len(a) != 0:
                    df_index.loc[a, 'volume'] = (-1) * df_index.loc[a, 'volume']
                total_volume = '[total index volume]: ' + str(int(df_index['volume'].sum()))
                return (df,total_sum,total_volume,q_list)

        except Exception as e:
            print('[Error] apcode is wrong. ', e)

#exch_trade_id
def ApmosExch_trade_id(q):
        cache = pd.read_sql_query("SELECT * FROM Trade WHERE exch_trade_id LIKE'%%" + q + "%%'",con=ENGINE)
        # cache = pd.merge(cache, mapping, how='left')
        cache['trade_datetime'] = cache['trade_datetime'].astype('str')
        cache.sort_values(by=['trade_datetime'], inplace=True, ascending=False)
        cache.reset_index(inplace=True)
        df = cache.to_dict(orient='records')
        return (df)

#trade date
def ApmosTradedate(q):
        cache = pd.read_sql_query("SELECT * FROM Trade WHERE date_format(trade_datetime,'%%Y-%%m-%%d') ='" + q + "'",con=ENGINE)
        # cache = pd.merge(cache, mapping, how='left')
        cache['trade_datetime'] = cache['trade_datetime'].astype('str')
        cache.reset_index(inplace=True)
        df = cache.to_dict(orient='records')
        return (df)

def ApmosSearch(request):
    search_type=request.GET.get('search_type')
    search_value=request.GET.get('search_value')
    username = request.COOKIES.get('cookie_username')
    password = request.COOKIES.get('cookie_password')
    if (username == 'apmos') and (password == 'APMOS') :
        # apcode搜索 长度大于5个字节
        if search_type == 'ap_code' and len(search_value) >= 5:
            try:
                ap_code_data=ApmosApcode(search_value)
                df=ap_code_data[0]
                total_sum=ap_code_data[1]
                total_volume=ap_code_data[2]
                q_list=ap_code_data[3]
                if len(q_list)==1:
                    return render(request, 'index.html', {'df': df, 'total_sum': total_sum})
                elif len(q_list)==3:
                    return render(request, 'index.html', {'df': df, 'total_sum': total_sum, 'total_volume': total_volume})
                else:
                    return render(request, 'index.html')
            except Exception as e:
                print('[Error]',e)
                return render(request, 'index.html')
        #exch trade id搜索 长度大于5个字节
        elif search_type == 'exch_trade_id' and len(search_value) >= 5:
            try:
                df=ApmosExch_trade_id(search_value)
                return render(request, 'index.html', {'df': df})
            except Exception as e:
                print('[Error]',e)
                return render(request, 'index.html')

        #trade date 搜索 长度大于5个字节
        elif search_type == 'trade_datetime' and len(search_value) >= 5:
            try:
                df=ApmosTradedate(search_value)
                return render(request, 'index.html', {'df': df})

            except Exception as e:
                print('[Error]',e)
                return render(request, 'index.html')
        else:
            return render(request, 'index.html')

    else:
        response = HttpResponseRedirect('/login/')
        return response


# 查询T+1时间和feedcode
def FindFeedcode(request):
    q = request.GET.get('FindFeedcode')
    username = request.COOKIES.get('cookie_username')
    password = request.COOKIES.get('cookie_password')
    if q and (username == 'apmos') and (password == 'APMOS'):
        try:
            df = pd.read_csv(PATH_FEEAPCODEMAPPING)
            a = df[df['ap_code'] == q].index
            if len(a) != 0:
                df = df[df['product_class'] == df.loc[a, 'product_class'].values[0]]
                cache = df.to_dict(orient='records')
            else:
                cache = pd.DataFrame()

            return render(request, 'feedcode.html', {'cache': cache})
        except Exception as e:
            print('[Error] feedcode is wrong.', e)
            return render(request, 'index.html')
    else:
        response = HttpResponseRedirect('/login/')
        return response


# 根据apcode查询平均价
def FindAVGPrice(request):
    code_type = request.GET.get('code_type')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    ap_code = request.GET.get('code_value')
    username = request.COOKIES.get('cookie_username')
    password = request.COOKIES.get('cookie_password')
    #如果code_type是bbticker,则需要进行查找ap_code
    if code_type=='bb_ticker':
        bb_ticker=ap_code
        cache = pd.read_csv(PATH_CONTRACTS)
        cache=cache[['ap_code','bb_ticker']]
        a=cache[cache['bb_ticker']==ap_code].index
        if len(a)!=0:
            ap_code=cache.loc[a,'ap_code'].values[0]
        else:
            return render(request, 'avg_price.html')


    if code_type and (username == 'apmos') and (password == 'APMOS'):
        if len(end_time) < 10:
            end_time = str(datetime.now()).split(' ')[0]
        cache_str = "SELECT * FROM Trade WHERE (ap_code='" + ap_code + "') and (date_format(trade_datetime,'%%Y-%%m-%%d')<='" + end_time + "') and (date_format(trade_datetime,'%%Y-%%m-%%d')>='" + start_time + "')"
        cache = pd.read_sql_query(cache_str, con=ENGINE)
        cache['volume'] = cache['volume'].astype('int')
        cache['price'] = cache['price'].astype('float')
        cache['trade_amount'] = cache['volume'] * cache['price']
        df = pd.DataFrame()
        df = df.append(pd.DataFrame(cache[['volume', 'trade_amount']].groupby([cache['trader_id'], cache['book'],cache['account'],cache['side']]).sum()))
        df.reset_index(inplace=True)
        df.fillna(method='ffill', inplace=True)
        df['AVG_price'] = round(df['trade_amount'] / df['volume'], 5)
        df.sort_values(by='trader_id', inplace=True)
        df['trade_amount'] =round(df['trade_amount'],2)
        df = df.to_dict(orient='records')
        if code_type=='ap_code':
            return render(request, 'avg_price.html',{'df': df, 'start_time': start_time, 'end_time': end_time, 'ap_code': ap_code})
        else:
            return render(request, 'avg_price.html',{'df': df, 'start_time': start_time, 'end_time': end_time, 'ap_code': bb_ticker})

    else:
        return render(request, 'avg_price.html')

#根据apcode和时间查询价格分布
def FindPriceVolume(request):
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    #分解code_value
    code_value = request.GET.get('code_value')
    q_list = code_value.split(',')
    ap_code = q_list[0]

    username = request.COOKIES.get('cookie_username')
    password = request.COOKIES.get('cookie_password')
    if ap_code and (username == 'apmos') and (password == 'APMOS') and (len(start_time)==10):
        if len(end_time) < 10:
            end_time = start_time
        cache_str = "SELECT * FROM Trade WHERE (ap_code='" + ap_code + "') and (date_format(trade_datetime,'%%Y-%%m-%%d')<='" + end_time + "') and (date_format(trade_datetime,'%%Y-%%m-%%d')>='" + start_time + "')"
        cache = pd.read_sql_query(cache_str, con=ENGINE)

        cache['volume'] = cache['volume'].astype('int')
        cache['price'] = cache['price'].astype('float')
        #create datetime
        cache['trade_datetime'] = pd.to_datetime(cache['trade_datetime'])
        cache['hour'] = cache['trade_datetime'].dt.hour
        cache['hour'] = cache['hour'].astype('str')
        cache['trade_datetime'] = cache['trade_datetime'].astype('str')
        try:
            cache['trade_datetime'] =cache['trade_datetime'].str.split(' ',expand=True)[0]+ ' '+cache['hour']
        except:
            pass
        # out
        df = pd.DataFrame()
        df = df.append(pd.DataFrame(cache['volume'].groupby([cache['ap_code'],cache['account'],cache['trade_datetime'],cache['side'],cache['price']]).sum()))
        df.reset_index(inplace=True)
        # 排序
        df.sort_values(by=['trade_datetime','price'],inplace=True,ascending= False)
        df['rec_mark'] = round(df['volume']* df['price'],3)
        df.reset_index(inplace=True,drop=True)
        df.reset_index(inplace=True)

        #code value中是否有index查询需求
        if len(q_list) ==1:
            #求rec mark
            rec_mark = (df['volume']* df['price']).sum()
            df = df.to_dict(orient='records')
            return render(request, 'price_volume.html',{'df': df, 'start_time': start_time, 'end_time': end_time, 'ap_code': ap_code,'rec_mark': rec_mark})
        elif len(q_list) ==3:
            q_start = q_list[1]
            q_end = q_list[2]
            df= df[int(q_start):int(q_end) + 1]

            #求rec mark
            rec_mark = (df['volume']* df['price']).sum()

            df = df.to_dict(orient='records')
            return render(request, 'price_volume.html',{'df': df, 'start_time': start_time, 'end_time': end_time, 'ap_code': ap_code,'rec_mark': rec_mark})
    else:
        return render(request, 'index.html')

# 更新book trade
def UpdateResult(request):
    username = request.COOKIES.get('cookie_username')
    password = request.COOKIES.get('cookie_password')
    if (username == 'apmos') and (password == 'APMOS'):
        # 获取参数
        FILE_NAME = request.GET.get('cache_file_name')
        FILE_NAME = FILE_NAME.replace('$', ' ')
        logging.info('file_name:{{{}}}'.format(FILE_NAME))

        # 文件名字长度大于3
        try:
            if len(FILE_NAME) < 3:
                return render(request, 'index.html')
        except:
            return render(request, 'index.html')

        CHANGE_TRADER_NAME = request.GET.get('CHANGE_TRADER_NAME')
        logging.info('CHANGE_TRADER_NAME:{{{}}}'.format(CHANGE_TRADER_NAME))
        trader_mark = request.GET.get('trader_mark')
        logging.info('trader_mark:{{{}}}'.format(trader_mark))

        CHANGE_BOOK_NAME = request.GET.get('CHANGE_BOOK_NAME')
        logging.info('CHANGE_BOOK_NAME:{{{}}}'.format(CHANGE_BOOK_NAME))
        book_mark = request.GET.get('book_mark')
        logging.info('book_mark:{{{}}}'.format(book_mark))

        ACCOUNT = request.GET.get('ACCOUNT')
        logging.info('ACCOUNT:{{{}}}'.format(ACCOUNT))
        account_mark = request.GET.get('account_mark')
        logging.info('account_mark:{{{}}}'.format(account_mark))

        COUNTERPARTY = request.GET.get('COUNTERPARTY')
        COUNTERPARTY =COUNTERPARTY.replace('$', ' ')
        logging.info('COUNTERPARTY:{{{}}}'.format(COUNTERPARTY))
        counterparty_mark = request.GET.get('counterparty_mark')
        logging.info('counterparty_mark:{{{}}}'.format(counterparty_mark))

        db = pymysql.connect(user='apmos', passwd='APCap1101!', db=DATABASE_NAME)
        cursor_sql = db.cursor()
        df_update = pd.read_csv(PATH_UPDATE + FILE_NAME)
        df_update['exch_trade_id'] = df_update['exch_trade_id'].astype('str')
        df_list = list(df_update['exch_trade_id'])
        show_data_list = []

        for n in df_list:
            # 打印
            cache = 'SELECT * FROM Trade WHERE exch_trade_id="' + n + '"'
            cursor_sql.execute(cache)
            show_data = cursor_sql.fetchone()
            show_data_list.append(n)
            logging.info(show_data)

            if trader_mark != '0':
                cache = 'UPDATE Trade SET trader_id="' + CHANGE_TRADER_NAME + '" WHERE exch_trade_id="' + n + '"'
                cursor_sql.execute(cache)

            if book_mark != '0':
                cache = 'UPDATE Trade SET book="' + CHANGE_BOOK_NAME + '" WHERE exch_trade_id="' + n + '"'
                cursor_sql.execute(cache)

            if account_mark != '0':
                cache = 'UPDATE Trade SET account="' + ACCOUNT + '" WHERE exch_trade_id="' + n + '"'
                cursor_sql.execute(cache)

            if counterparty_mark != '0':
                cache = 'UPDATE Trade SET counterparty="' + COUNTERPARTY + '" WHERE exch_trade_id="' + n + '"'
                cursor_sql.execute(cache)
        db.commit()

        #返回查询结果
        sql_str_list = []
        for n in show_data_list:
            sql_str = "(exch_trade_id = '"+n +"')"
            sql_str_list.append(sql_str)
        sql_str = " OR ".join(sql_str_list)
        #print(sql_str)
        update_result = pd.read_sql_query("SELECT * FROM Trade WHERE " + sql_str + "",con=ENGINE)
        update_result = update_result.to_dict(orient='records')

        return render(request, 'update_result.html', {'update_result': update_result})
    else:
        response = HttpResponseRedirect('/login/')
        return response


# 根据修改trader book 等数据
def UpdateAPMOS(request):
    username = request.COOKIES.get('cookie_username')
    password = request.COOKIES.get('cookie_password')

    if (username == 'apmos') and (password == 'APMOS'):
        # 获取数据
        FILE_NAME = request.GET.get('FILE_NAME')
        CHANGE_TRADER_NAME = request.GET.get('CHANGE_TRADER_NAME')
        CHANGE_BOOK_NAME = request.GET.get('CHANGE_BOOK_NAME')
        ACCOUNT = request.GET.get('ACCOUNT')
        COUNTERPARTY = request.GET.get('COUNTERPARTY')
        # 判定空值情况
        try:
            if len(CHANGE_TRADER_NAME) == 5:
                trader_mark = 1
            else:
                trader_mark = 0
        except:
            trader_mark = 0

        try:
            if len(CHANGE_BOOK_NAME) == 5:
                book_mark = 1
            else:
                book_mark = 0
        except:
            book_mark = 0

        try:
            if len(ACCOUNT) >= 4:
                account_mark = 1
            else:
                account_mark = 0
        except:
            account_mark = 0

        try:
            if len(COUNTERPARTY) >= 2:
                counterparty_mark = 1
            else:
                counterparty_mark = 0
        except:
            counterparty_mark = 0

        # print(FILE_NAME, CHANGE_TRADER_NAME, CHANGE_BOOK_NAME, ACCOUNT, COUNTERPARTY)
        if trader_mark + book_mark + account_mark + counterparty_mark != 0:
            # 将空格替换为$
            cache_file_name = FILE_NAME.replace(' ', '$')
            COUNTERPARTY=COUNTERPARTY.replace(' ', '$')
            # 扫描文件名
            files_list = []
            for root, dirs, files in os.walk(PATH_UPDATE):
                for f in files:
                    files_list.append(f)
            # 读取文件
            try:
                df_update = pd.read_csv(PATH_UPDATE + FILE_NAME)
            except Exception as e:
                print('[Error]', e)
                return render(request, 'updateAPMOS.html', {'files_list': files_list})
            return render(request, 'updateAPMOS.html', {'FILE_NAME': FILE_NAME,
                                                        'cache_file_name': cache_file_name,
                                                        'HOW_MUCH': len(df_update),
                                                        'CHANGE_TRADER_NAME': CHANGE_TRADER_NAME,
                                                        'trader_mark': trader_mark,
                                                        'CHANGE_BOOK_NAME': CHANGE_BOOK_NAME,
                                                        'book_mark': book_mark,
                                                        'ACCOUNT': ACCOUNT,
                                                        'account_mark': account_mark,
                                                        'COUNTERPARTY': COUNTERPARTY,
                                                        'counterparty_mark': counterparty_mark,
                                                        'files_list': files_list})
        else:
            # 扫描文件名
            files_list = []
            for root, dirs, files in os.walk(PATH_UPDATE):
                for f in files:
                    files_list.append(f)
            return render(request, 'updateAPMOS.html', {'files_list': files_list})
    else:
        response = HttpResponseRedirect('/login/')
        return response
