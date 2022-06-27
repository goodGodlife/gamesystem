from modules.config import *
class Sys_config(Base):
    __tablename__ = 'sys_config'
    id = Column(Integer,primary_key=True)
    round_count = Column(Integer)
    platform_address = Column(String)