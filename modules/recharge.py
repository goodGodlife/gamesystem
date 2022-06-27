from modules.config import *
class Recharge(Base):
    __tablename__ = 'recharge'
    id = Column(Integer,primary_key=True)
    username = Column(String)
    platfrom_address = Column(String)
    usdt = Column(Float)
    accept_username = Column(String)
    time = Column(String)
    operate_time = Column(String)
    flag = Column(Integer)