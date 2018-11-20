
class PriceDoseNotExist(Exception):
    def __init__(self):
        self.error = "价格周期不存在，滚你妈的"