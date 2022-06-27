from modules.config import *
class Plan_config(Base):
    __tablename__ = 'plan_config'
    id = Column(Integer,primary_key=True)
    one = Column(Integer)
    two = Column(Integer)
    three = Column(Integer)
    four = Column(Integer)
    five = Column(Integer)
    six = Column(Integer)
    seven = Column(Integer)
    eight = Column(Integer)
    nine = Column(Integer)
