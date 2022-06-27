import hashlib
import time

from flask import Flask, Blueprint, request, jsonify
from modules.config import SessionLocal
from modules.user import User
from modules.withdrawal import Withdrawal
from modules.recharge import Recharge
from modules.platform_usdt_address import Platform_usdt_address

usdtapi = Blueprint('usdtapi', __name__, url_prefix='/usdt')


@usdtapi.route('/bind', methods=['POST'])
def bind():  # 绑定usdt地址与修改是同一个地址
    jdata = request.get_json()
    session = SessionLocal()
    md5 = hashlib.md5(jdata['password'].encode('UTF-8')).hexdigest()
    res = session.query(User).filter_by(apikey=jdata['apikey'],usdt_password=md5).update({'usdt_address': jdata['usdt_address']})
    if res > 0:
        session.commit()
        session.close()
        return jsonify({'msg': '绑定USDT地址成功', 'code': 200})

    session.close()
    return jsonify({'msg': '绑定USDT地址异常', 'code': 201})


@usdtapi.route('/getusdt', methods=['POST'])
def getusdt():  # 提币usdt
    jdata = request.get_json()
    print(jdata)
    session = SessionLocal()
    md5 = hashlib.md5(jdata['usdt_password'].encode('UTF-8')).hexdigest()
    print('apikey:', jdata['apikey'])
    res = session.query(User).filter(User.apikey == jdata['apikey'], User.usdt_password == md5,
                                     User.usdt >= jdata['usdt_count'], User.usdt_address is not None).update({
        'usdt': User.usdt - jdata['usdt_count']})
    if res:
        # 条件匹配，提币成功，写进表里等待操作
        res = session.query(User).filter_by(apikey=jdata['apikey']).first()
        w = Withdrawal(
            username=res.username,
            usdt_address=res.usdt_address,
            usdt_count=jdata['usdt_count'],
            time=int(time.time())

        )
        session.add(w)
        session.commit()
        session.close()
        return jsonify({'msg': '申请提现成功,请等待审核', 'code': 200})

    session.close()
    return jsonify({'msg': '申请提币异常', 'code': 202})


@usdtapi.route('/usdtfill', methods=['POST'])
def usdtfill():  # 充币
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).first()
    if res:
        username = jdata['username']
        if jdata['username'] == '' or jdata['username'] is None:
            username = res.username
        else:
            accept_username_res = session.query(User).filter_by(username=jdata['username']).first()
            if accept_username_res is None:  # 如果没有找到对应的用户名，则说明输入错误
                session.close()
                return jsonify({'msg': '对方用户名不存在,检测用户名', 'code': 203})

        w = Recharge(
            username=res.username,
            platfrom_address=jdata['platformaddress'],
            usdt=jdata['count'],
            accept_username=username,
            time=int(time.time())

        )
        session.add(w)
        session.commit()
        session.close()
        return jsonify({'msg': '充币成功，请等待平台审核', 'code': 200})

    session.close()
    return jsonify({'msg': '充币异常', 'code': 201})


@usdtapi.route('/getusdtaddress')
def getusdtaddress():  # 获取平台usdt地址 充币的时候需要使用
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).all()
    if len(res) > 0:  # 判断apikey成功
        res = session.query(Platform_usdt_address).first()
        session.close()
        return jsonify({'msg': '返回平台地址成功', 'code': 200, 'data': res.platform_usdt_address})
    session.close()
    return jsonify({'msg': '获取平台地址失败', 'code': 201})


@usdtapi.route('/updateaddress', methods=['POST'])
def updateaddress():  # 修改usdt地址
    jdata = request.get_json()
    session = SessionLocal()
    md5 = hashlib.md5(jdata['usdt_password'].encode('UTF-8')).hexdigest()
    res = session.query(User).filter_by(apikey=jdata['apikey'], usdt_password=md5)
    res = res.update({'usdt_address': jdata['usdt_address']})
    print(res)
    if res > 0:
        session.commit()
        session.close()
        return jsonify({'msg': '修改usdt地址成功', 'code': 200})

    session.close()
    return jsonify({'msg': '修改usdt地址异常', 'code': 201})


@usdtapi.route('/getuseraddress', methods=['POST'])
def getuseraddress():  # 获取个人的USDT地址
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).first()
    if res:
        session.close()
        return jsonify({'msg': '获取个人地址成功', 'code': 200, 'data': res.usdt_address})
    session.close()
    return jsonify({'msg': '获取个人Usdt失败', 'code': 201})
