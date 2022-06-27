from modules.config import *
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer,primary_key=True)
    username = Column(String)
    password = Column(String)
    usdt_password = Column(String)
    usdt = Column(Float)
    regis_time = Column(String)
    commission = Column(Float)
    apikey = Column(String)
    usdt_address = Column(String)
    ratio = Column(Float)
    permission = Column(String)

    def __repr__(self):
        return f'{self.id} {self.username} {self.apikey}'

    __str__ = __repr__