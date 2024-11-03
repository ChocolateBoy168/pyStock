
class AbstractCscApi:

	def __init__(self):
		pass

	def sendFutureOrder(self):
		return None, -1

	def decreaseOrderBySeqNo(self):
		return None, -1

	def cancelOrderByStockNo(self):
		return None, -1

	def cancelOrderBySeqNo(self):
		return None, -1

	def cancelAllOrder(self):
		return None, -1