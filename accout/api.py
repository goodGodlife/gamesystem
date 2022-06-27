import time

from flask import Flask, Blueprint, request, jsonify
import string
import base64
import uuid

from modules.relation import Relation
from modules.user import *
from modules.config import *
import hashlib

accout = Blueprint('accout', __name__, url_prefix='/accout')


@accout.route('/login', methods=['POST'])
def login():  # 登录
    jdata = request.get_json()
    md5 = hashlib.md5(jdata['password'].encode('utf-8')).hexdigest()
    session = SessionLocal()
    print(jdata['username'],md5)
    res = session.query(User).filter_by(username=jdata['username'], password=md5).all()
    print('res',res)
    if len(res) > 0:
        print('OK')
        r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
        s = r_uuid.decode("UTF-8")
        user = session.query(User).filter_by(username=jdata['username'], password=md5).first()
        user.apikey = s
        session.add(user)
        session.commit()
        session.close()
        return jsonify({"msg": '登录成功', 'code': 200, 'data': s})

    session.close()
    return jsonify({'msg': '登录异常或者密码错误', 'code': 202})


@accout.route('/register', methods=['POST'])
def register():  # 注册
    jdata = request.get_json()
    session = SessionLocal()
    resA = session.query(User).filter_by(apikey=jdata['apikey']).first()
    resB = session.query(User).filter_by(username=jdata['username']).first()
    print(jdata['username'],type(jdata['ratio']))

    if len(jdata['username']) <0:
        session.close()
        return jsonify({'msg':'输入的参数不正确，请输入正确的值','code':203})
    print(resA,resB)
    if resA and resB is None:  #判断apikey 和 username
        md5 = hashlib.md5('a123456'.encode('UTF-8')).hexdigest()
        res = session.query(User).filter_by(apikey=jdata['apikey']).first()
        if res and jdata['ratio'] > res.ratio:
            session.close()
            return jsonify({'msg': '返佣比例值异常', 'code': 203})

        relation_res = session.query(Relation).filter(Relation.username == resA.username).first()
        if relation_res and relation_res.relation is not None:  #将关系网写入
            s = Relation(username =jdata['username'], relation= resA.username + ',' + relation_res.relation)
            session.add(s)
        else:
            s = Relation(username = jdata['username'],relation=resA.username)
            session.add(s)

        w = User(username=jdata['username'], password=md5, ratio=float(jdata['ratio']),regis_time=str(int(time.time())))
        session.add(w)
        session.commit()
        session.close()
        return jsonify({'msg': '注册成功', 'code': 200})

    session.close()
    return jsonify({'msg': '注册失败,用户名被占用,请重新输入用户名', 'code': 202})


@accout.route('/modifypassword', methods=['POST'])
def modifypassword():  # 修改密码
    jdata = request.get_json()
    ses = SessionLocal()
    md5 = hashlib.md5(jdata['old_password'].encode('UTF-8')).hexdigest()
    md5New = hashlib.md5(jdata['new_password'].encode('UTF-8')).hexdigest()
    res = ses.query(User).filter_by(apikey=jdata['apikey'], password=md5).update({"password": md5New})
    if res > 0 and len(jdata['new_password']) > 6:
        ses.commit()
        ses.close()
        return jsonify({'msg': '密码修改成功', 'code': 200})

    ses.close()
    return jsonify({'msg': '修改密码异常', 'code': 202})


@accout.route('/modifyusdtpassword', methods=['POST'])
def modifyusdtpassword():  # 修改USDT密码 修改操作密码
    jdata = request.get_json()
    print(jdata)
    ses = SessionLocal()
    md5 = hashlib.md5(jdata['old_usdt_password'].encode('UTF-8')).hexdigest()
    md5New = hashlib.md5(jdata['new_usdt_password'].encode('UTF-8')).hexdigest()
    res = ses.query(User).filter_by(apikey=jdata['apikey'], usdt_password=md5).update({"usdt_password": md5New})
    if res > 0 and len(jdata['new_usdt_password']) >= 6:
        ses.commit()
        ses.close()
        return jsonify({'msg': '修改操作密码成功', 'code': 200})

    ses.close()
    return jsonify({'msg': '修改操作密码异常', 'code': 202})


@accout.route('/bindusdtpassword', methods=['POST'])
def bindusdtpassword():  # 设置usdt密码 绑定操作密码
    jdata = request.get_json()
    print(jdata)
    ses = SessionLocal()
    md5usdt = hashlib.md5(jdata['bind_usdt_password'].encode('UTF-8')).hexdigest()
    res = ses.query(User).filter(User.apikey == jdata['apikey'], User.usdt_password.is_(None)).update(
        {'usdt_password': md5usdt})
    if res > 0 and len(jdata['bind_usdt_password']) >= 6:
        print(res)
        ses.commit()
        ses.close()
        return jsonify({'msg': '绑定操作密码成功', 'code': 200})
    ses.close()
    return jsonify({'msg': '绑定操作密码异常或者有密码，请前往修改操作密码', 'code': 202})


@accout.route('/getusdt', methods=['POST'])  # 获取usdt余额
def getusdt():
    jdata = request.get_json()
    print(jdata)
    ses = SessionLocal()
    res = ses.query(User).filter_by(apikey=jdata['apikey']).all()
    if len(res) > 0:
        ses.close()
        return jsonify({'msg': '获取余额成功', 'code': 200, 'data': res[0].usdt})
    ses.close()
    return jsonify({'msg': '获取余额异常', 'code': 202})


@accout.route('/getratio', methods=['POST'])
def getratio():  # 返回用户的返佣比例值
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).first()
    if res:
        session.close()
        return jsonify({'msg': '获取返佣比例值成功', 'code': 200, 'data': res.ratio})

    session.close()
    return jsonify({'msg': '获取返佣比例值异常', 'code': 201})


@accout.route('/getusername',methods=['POST'])
def getusrename():  #获取帐号名
    jdata = request.get_json()
    session = SessionLocal()
    res = session.query(User).filter_by(apikey=jdata['apikey']).first()
    if res:
        session.close()
        return jsonify({'msg':'获取帐户名成功','code':200,'data':res.username})
    session.close()
    return jsonify({'msg':'获取用户名异常','code':201})