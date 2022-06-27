from modules.config import *
class Withdrawal(Base):
    __tablename__ = 'withdrawal'
    id = Column(Integer,primary_key=True)
    username = Column(String)
    usdt_address = Column(String)
    usdt_count = Column(Float)
    time = Column(String)
    operate_time = Column(String)