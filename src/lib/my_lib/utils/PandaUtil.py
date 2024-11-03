from pandas import DataFrame


class PandaUtil:
	_instance = None

	def __new__(cls, *args, **kw):
		if not cls._instance:
			cls._instance = super(PandaUtil, cls).__new__(cls, *args, **kw)
			cls._instance.__initialized = False
		return cls._instance

	def __init__(self):
		if self.__initialized:
			return
		self.__initialized = True

	@staticmethod
	def to_records_dict(df: DataFrame):
		return df.to_dict(orient='records')

	@staticmethod
	def to_index_dict(df: DataFrame):
		return df.to_dict(orient='index')

	@staticmethod
	def tail_cell_val(df, column_name):
		result = None
		if (df is not None) and (df.shape[0] > 0):
			tail_df = df.tail(1)
			result = tail_df.iloc[0][column_name]
		return result
