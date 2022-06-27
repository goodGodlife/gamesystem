import time

import requests
from modules.config import SessionLocal
from modules.recharge import Recharge
from modules.sys_config import Sys_config
from modules.withdrawal import Withdrawal
from modules.user import User
from modules.rounds import Rounds
from flask import Blueprint, request, jsonify

admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/getrechargeorder', methods=['POST'])
def getrechargeorder():  # 获取充值申请订单
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).one()
    if res and res.permission == 'admin':
        recharge_res = session.query(Recharge).filter(Recharge.operate_time is None).all()
        if len(recharge_res) > 0:  # 找到有充值的订单
            dic = {k: {'username': v.username, 'platform_addredd': v.platform_address, 'usdt': v.usdt,
                       'accept_username': v.accpet_username,
                       'time': v.time} for k, v in enumerate(recharge_res)}
            session.close()
            return jsonify({'msg': '获取充值订单成功', 'code': 200, 'data': dic})

    session.close()
    return jsonify({'msg': '获取充值订单失败', 'code': 201, 'data': '未获取到充值订单数据'})


@admin.route('/getwithdrawalorder', methods=['POST'])
def getwithdrawalorder():  # 获取提币订单
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).one()
    if res and res.permission == 'admin':
        withdrawal_res = session.query(Withdrawal).filter(Withdrawal.operate_time is None).all()
        if len(withdrawal_res):
            dic = {k: {'username': v.username, 'usdt_address': v.usdt_address,
                       'usdt_count': v.usdt_count, 'time': v.time} for k, v in enumerate(withdrawal_res)}
            session.close()
            return jsonify({'msg':'获取提币订单成功','code':200,'data':dic})

    session.close()
    return jsonify({'msg':'获取提币订单失败','code':201,'data':0})

@admin.route('/getrounds',methods=['POST'])
def getrouds():  #获取轮次订单，即挂机订单
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).one()
    if res and res.permission == 'admin':
        rounds_res = session.query(Rounds).all()
        ###########停止开发#####################

@admin.route('/getroudconfig',methods=['POST'])
def getroudconfig(): #轮次配置
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).one()
    if res and res.permission == 'admin':
        round_config = session.query(Sys_config.round_count).one()
        session.close()
        return jsonify({'msg':'获取轮次配置参数成功','code':200,'data':round_config.round_count})
    session.close()
    return jsonify({'msg':'获取轮次配置参数异常','code':201,'data':0})


@admin.route('/getbalance',methods=['POST'])
def getbalance():  #获取余额割管器
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).one()
    if res and res.permission == 'admin':
        balance_res = session.query(User).filter(User.usdt>0).order_by(User.usdt).desc().all()
        if len(balance_res)>0:
            dic={k:{'username':v.username,'balance':v.usdt} for k ,v in enumerate(balance_res)}
            session.close()
            return jsonify({'msg':'获取余额记录成功','code':200,'data':dic})
    session.close()
    return jsonify({'msg':'获取余额记录失败','code':201,'data':0})

@admin.route('/operationrecharge',methods=['POST'])
def operationbalance():  #操作充值同意或者拒绝   apikey  flag  username
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).one()
    if res and res.permission == 'admin':
        if jdata['flag'] == 'no': #拒绝充值  不添加余额
            res = session.query(Recharge).filter_by(username=jdata['username']).update({'operate_time':str(int(time.time()))})
            if res >0:
                session.close()
                return jsonify({'msg':'拒绝充值成功','code':200})
            session.close()
            return jsonify({'msg':'拒绝充值操作异常','code':201})

        elif jdata['flag'] == 'yes': # 同意  添加余额
            recharge_res = session.query(Recharge).filter_by(username=jdata['username']).all()
            if len(recharge_res)>0:  #有待处理订单
                for k,v in enumerate(recharge_res):
                    session.query(User).filter_by(username=v.username).update({'usdt':User.usdt + v.usdt})
                session.close()
                return jsonify({'msg':'操作充值订单成功','code':200})

            session.close()
            return jsonify({'msg':'操作充值订单失败','code':201})