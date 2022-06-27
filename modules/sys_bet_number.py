from modules.config import *
class Sys_bet_number(Base):
    __tablename__ = 'sys_bet_number'
    id = Column(Integer,primary_key=True)
    period = Column(String)
    prize_number = Column(Integer)