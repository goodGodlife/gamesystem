from modules.config import *
class Platform_usdt_address(Base):
    __tablename__ = 'platform_usdt_address'
    id = Column(Integer,primary_key=True)
    platform_usdt_address = Column(String)