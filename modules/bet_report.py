from modules.config import *
class Bet_report(Base):
    __tablename__ = 'bet_report'
    username = Column(String)
    bet_number = Column(Integer)
    bet_usdt = Column(Float)
