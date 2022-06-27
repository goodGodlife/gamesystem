from modules.config import *
class Ratio(Base):
    __tablename__ = 'ratio'
    id = Column(Integer,primary_key=True)
    username = Column(String)
    ratio_money = Column(Float)
    period = Column(Integer)
    time = Column(String)
    operation_time = Column(String)