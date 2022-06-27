from modules.config import *


class Relation(Base):
    __tablename__ = 'relation'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    relation = Column(Text)
