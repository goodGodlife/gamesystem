import hashlib
import time

from flask import Flask, Blueprint, request, jsonify
from modules.config import SessionLocal
from modules.ratio import Ratio
from modules.sys_bet_number import Sys_bet_number
from modules.user import User
from modules.plan_config import Plan_config
from modules.rounds import Rounds
from modules.sys_config import Sys_config

gameapi = Blueprint('gameapi', __name__, url_prefix='/game')


@gameapi.route('/getsysprize', methods=["POST"])
def getsysprize():  # 获取系统开奖号码
    jdata = request.get_json()
    print(jdata)
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).first()
    if res != None:
        res = session.query(Sys_bet_number).order_by(Sys_bet_number.period.desc()).limit(10)
        print(type(res))
        data = {k: {'period': v.period, 'prize_number': v.prize_number} for k, v in enumerate(res)}
        session.close()
        return jsonify({'msg': '获取开奖历史记录成功', 'code': 200, 'data': data})

    session.close()
    return jsonify({'msg': '获取开奖历史记录异常', 'code': 201})


@gameapi.route("/getplan", methods=["POST"])
def getplan():  # 获取方案
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).first()
    if res != None:
        res = session.query(Plan_config).first()
        data = {'one': res.one, 'two': res.two, 'three': res.three, 'four': res.four, 'five': res.five, 'six': res.six
            , 'seven': res.seven, 'eight': res.eight, 'nine': res.nine}
        session.close()
        return jsonify({'msg': '获取方案成功', 'data': data, 'code': 200})
    session.close()
    return jsonify({'msg': '获取方案数据失败', 'code': 201})


@gameapi.route('/hangup', methods=['POST'])
def hangup():  # 提交挂机 ,提交时，此前该用户的记录删除掉。将分析记录写进临时表.  一次只能挂一次机
    jdata = request.get_json()
    print(jdata)
    rounds = {
        'one': [2500, 30, 60, 120, 240, 480, 960],
        'two': [5000, 60, 120, 240, 480, 960, 1920],
        'three': [100000, 120, 240, 480, 960, 1920, 3840],
        'four': [25000, 240, 480, 960, 1920, 3840, 7680],
        'five': [500000, 480, 960, 1920, 3840, 7680, 15360],
        'six': [100000, 960, 1920, 3840, 7680, 15360, 30720],
        'seven': [250000, 1920, 3840, 7680, 15360, 30720, 61440],
        'eight': [500000, 3840, 7680, 15360, 30720, 61440, 122880],
        'nine': [1000000, 7680, 15360, 30720, 61440, 122880, 245760]
    }
    session = SessionLocal()
    md5 = hashlib.md5(jdata['usdt_password'].encode('UTF-8')).hexdigest()
    res = session.query(User).filter(User.usdt >= rounds[jdata['plan_key']][0], User.apikey == jdata['apikey'],
                                     User.usdt_password == md5).all()
    if len(res) > 0 and jdata['plan_key'] in rounds.keys():
        usdt = res[0].usdt  # 将未减前的资金保存着
        print('usdt:***********',type(usdt))
        # 扣去余额
        session.query(User).filter_by(apikey=jdata['apikey']).update({'usdt':usdt - float(rounds[jdata['plan_key']][0])})
        username = res[0].username
        # 检测方案Key与配置表是否对应，并且满足身份验证和余额验证条件  并根据轮次决定写入数据
        sys_res = session.query(Sys_bet_number).order_by(Sys_bet_number.period.desc()).first()
        rounds_res = session.query(Rounds).filter_by(username=username).order_by(Rounds.period.desc()).first()
        if rounds_res and rounds_res.period > sys_res.period:  # 如果Rounds里面的期数少于Sys_bet_number表里的期数，则不能挂机
             print(rounds_res.period,sys_res.period,'-----------------------------------------')
             session.close()
             return jsonify({'msg': '有未处理完的订单，不能重复挂机', 'code': 203})

        bet_period = sys_res.period  # 当前系统期数 + 1 得到投注期数
        res = session.query(User.username, User.usdt).filter_by(apikey=jdata['apikey']).first()
        session.query(User).filter_by(username=res.username).update({'usdt': res.usdt - rounds[jdata['plan_key']][0]})
        count = session.query(Sys_config).first()
        count = count.round_count  # 轮次，第一轮中就写1，第3轮中就写3,中奖则全部结束，并且未中奖轮都为亏损

        session.query(Rounds).filter_by(username=res.username).delete()  # 一次性只能一个订单
        profit_flag = 0;
        count = int(count)
        usdt_profit = 0
        if count == 8:
            profit_flag = 8
            count = 6  # 默认6轮 最高6轮

        for num in range(1, count + 1):
            bet_period = bet_period + 1
            print('bet_period',bet_period)
            usdt_profit = 0
            usdt_profit = rounds[jdata['plan_key']][num] * -1
            if num == count and profit_flag != 8:
                usdt_profit *= -1  # 如果最后一轮，将亏损变为盈利
            w = Rounds(
                username=res.username,
                period=bet_period,
                round_count=num,
                usdt_profit=usdt_profit,
                usdt_count=rounds[jdata['plan_key']][num]
            )
            s = Ratio(
                username=res.username,
                ratio_money=rounds[jdata['plan_key']][num],
                time=str(int(time.time())),
                period= bet_period
            )
            session.add(s)  # 将投注记录写进，每日结算的时候进行结算
            session.add(w)
        session.query(User).filter_by(username=username).update({'usdt': usdt+usdt_profit})
        session.commit()
        session.close()
        return jsonify({'msg': '挂机成功', 'code': 200})

    session.close()
    return jsonify({'msg': '挂机异常', 'code': 201})


@gameapi.route('/round', methods=["POST"])
def round():  # 获取轮次
    jdata = request.get_json()
    print(jdata)
    session = SessionLocal()
    resA = session.query(User).filter_by(apikey=jdata['apikey']).first()
    if resA is not None:
        res = session.query(Sys_bet_number).order_by(Sys_bet_number.period.desc()).first()  # 获取最新系统开奖的期数
        res = session.query(Rounds).filter(Rounds.username == resA.username, Rounds.period <= res.period).all()
        if len(res) > 0:
            data = {k: {'period': v.period, 'round_count': v.round_count, 'usdt_profit': v.usdt_profit,
                        'usdt_count': v.usdt_count}
                    for k, v in enumerate(res)}
        else:
            session.close()
            return jsonify({'msg': '无轮次记录', 'code': 202})

        session.close()
        return jsonify({'msg': '获取轮次记录成功', 'data': data, 'code': 200})  # 如果data为空值的话，那说明挂机后，奖还没有开或者没有挂机

    session.close()
    return jsonify({'msg': '获取轮次记录异常', 'code': 201})


@gameapi.route('/dayprofit')
def dayprofit():  # 今日盈亏
    pass


@gameapi.route('/getplatformaddress', methods=['POST'])
def getplataddress():  # 获取平台收币地址
    jdata = request.get_json()
    print(jdata)
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).first()
    if res is not None:
        res = session.query(Sys_config.platform_address).first()
        session.close()
        return jsonify({'msg': '获取平台收币地址成功', 'data': res.platform_address, 'code': 200})

    session.close()
    return jsonify({'msg': '获取平台收币地址失败', 'code': 201})
