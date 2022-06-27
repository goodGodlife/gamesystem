from modules.config import *
class Rounds(Base):
    __tablename__ = 'rounds'
    id = Column(Integer,primary_key=True)
    username  = Column(String)
    period = Column(String)
    round_count = Column(Integer)
    usdt_profit = Column(Float)
    kind = Column(String)
    usdt_count = Column(Float)
