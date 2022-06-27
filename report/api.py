from flask import Flask, Blueprint, request, jsonify
from sqlalchemy.sql import func

from modules.config import *
from modules.person_report import *
from modules.user import *

reportapi = Blueprint('reportapi', __name__, url_prefix='/report')


@reportapi.route('/getsubordinate')
def getsubordinate():  # 获取下线
    pass


@reportapi.route("/personreport",methods=['POST'])
def personreport():  # 获取个人报表
    jdata = request.get_json()
    ses = SessionLocal()
    res = ses.query(User).filter_by(apikey=jdata['apikey']).all()
    if len(res) > 0:
        res = ses.query(Person_report).filter_by(username=res[0].username).all()
        ses.close()
        if len(res) > 0:
            dic = {'msg': '获取个人报表成功', 'code': 200, 'username': res[0].username, 'bet_usdt': res[0].bet_usdt,
                   'profit': res[0].profit_usdt, 'recharge': res[0].recharge
                , 'withdrawal': res[0].withdrawal, 'commission': res[0].commission}
            return jsonify(dic)
        else:
            return jsonify({'msg': '暂未获取到个人报表数据', 'code': 201})
    else:
        ses.close()
        return jsonify({'msg': '获取个人报表出现异常', 'code': 202})


@reportapi.route('/teamreport',methods=['POST'])
def teamreport():  # 获取团队报表

    jdata = request.get_json()
    ses = SessionLocal()

    subque = ses.query(User.username.label('username')).filter(User.apikey == jdata['apikey']).subquery()
    resA = ses.query(User.username.label('lowuser')).filter(User.superior == subque.c.username).subquery()

    resB = ses.query(Person_report).filter(Person_report.username == resA.c.lowuser).all()

    pr_sum = list(
        ses.query(Person_report).with_entities(func.sum(Person_report.bet_usdt), func.sum(Person_report.profit_usdt),
                                               func.sum(Person_report.recharge),
                                               func.sum(Person_report.withdrawal),
                                               func.sum(Person_report.commission)).all())
    lst = ['bet_usdt', 'profit_usdt', 'recharge', 'withdrawal', 'commission']
    data = dict(list(zip(lst, *pr_sum)))

    ses.close()
    return jsonify({'msg': data, 'code': 202})
