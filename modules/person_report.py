from modules.config import *
class Person_report(Base):
    def __repr__(self):
        return f'<Pr {self.id} {self.bet_usdt} {self.profit_usdt}>'
    __str__ = __repr__
    __tablename__ = 'person_report'
    id = Column(Integer,primary_key=True)
    username = Column(String)
    bet_usdt = Column(Float)
    profit_usdt = Column(Float)
    recharge = Column(Float)
    withdrawal = Column(Float)
    commission = Column(Float)