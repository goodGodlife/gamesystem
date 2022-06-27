import random
import time

import schedule
from modules.sys_bet_number import Sys_bet_number
from modules.config import SessionLocal
from modules.relation import Relation
from modules.ratio import Ratio
from modules.user import User
from modules.rounds import Rounds


def openprize():  # 开系统奖，并且还根据期数给佣金计算提供参考数据
    session = SessionLocal()
    query = session.query(Sys_bet_number).order_by(Sys_bet_number.period.desc()).first()
    w = Sys_bet_number(
        period=query.period + 1,
        prize_number=str(random.randint(0, 99999)).zfill(5)
    )
    session.add(w)
    session.commit()
    session.close()
    return str(random.randint(0, 99999)).zfill(5)


def statistics():  # 统计用户的佣金反复结算与记录  结算到余额中，并在记录中获取
    session = SessionLocal()
    ratio_res = session.query(Ratio).filter_by(operation_time=None).all()
    if len(ratio_res) > 0:  # 有记录需要返利
        for ratio_k,ratio_value in enumerate(ratio_res):
            # print('##########',ratio_value.username)
            ratio_dic = {}
            relation_res = session.query(Relation).filter_by(username=ratio_value.username).first()  #根据用户名查找对应的关系网
            # print(relation_res.username,relation_res.relation,'关系链')

            if relation_res.relation == '' or relation_res.relation is None:  #如果上级是空或者没有，则进行更新时间，并不进行返利
                # print('没有上线',ratio_value.username)
                res = session.query(Ratio).filter_by(username=ratio_value.username).update({'operation_time':str(int(time.time()))})
                # print('res',res)
                session.commit()
                session.close()
                return 0

            relation_lis = relation_res.relation.split(',') # 如果没有上线，则分割不了
            # print("&&&&&&&&",relation_lis)  #OK
            for k, v in enumerate(relation_lis):  # 将需要返利用户名与返利值进行第一步生成字典
                # print('!!!!!',v)
                user_res = session.query(User).filter_by(username=v).first()
                # print('ration:::',user_res.ratio)
                ratio_dic[k] = {'username': v, 'ratio': user_res.ratio}
                # print(ratio_dic,'LLLKJLJ')

            ratio_data={0:{'username':ratio_dic[0]['username'],'ratio':ratio_dic[0]['ratio']}}
            print(id(ratio_data),id(ratio_dic))
            for item in ratio_dic.items():  #生成返回利最终目标字典
                if item[0]+1 in ratio_dic.keys():
                    temp = round(ratio_dic[item[0] + 1]['ratio'] - ratio_dic[item[0]]['ratio'],2)
                    print(temp)
                    ratio_data[item[0]+1] = {'username':ratio_dic[item[0]+1]['username'],'ratio':temp}


            print(ratio_data,'FFFF')
            for item in ratio_data.items():  # 照着字典的值，更新最终返佣值

                session.query(User).filter_by(username=item[1]['username']).update({'usdt':User.usdt + round(ratio_value.ratio_money * item[1]['ratio'] /100,2)})
                session.query(Ratio).filter_by(username=ratio_value.username).update({'operation_time':str(int(time.time()))})

        session.commit()
        session.close()
    session.close()
    return 0

statistics()
schedule.every(1).minutes.do(openprize)
schedule.every(10).minutes.do(statistics)

while True:
    schedule.run_pending()
