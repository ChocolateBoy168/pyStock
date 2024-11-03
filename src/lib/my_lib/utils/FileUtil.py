import os

import errno


def is_file_empty(fileName):
	'''
	import pandas as pd
	if hasattr(pd.io.common, 'EmptyDataError'):
		try:
			pd.read_csv(fileName)
			return False
		except pd.io.common.EmptyDataError:
			return True
	else:
		return os.path.getsize(fileName) == 0
	'''
	isEmpty = os.path.getsize(fileName) == 0
	return isEmpty


# https://linuxize.com/post/python-check-if-file-exists/
def is_file_exist(file: str):
	return os.path.exists(file)


def make_dirs_if_not_exist(file: str):
	if not os.path.exists(os.path.dirname(file)):
		try:
			os.makedirs(os.path.dirname(file))
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise


def create_file_if_not_exist(file: str, delete_if_exist=False):
	if delete_if_exist is True:
		delete_file_if_exist(file)
	make_dirs_if_not_exist(file)
	if is_file_exist(file) is False:
		f = open(file, "w+")
		f.close()


def delete_file_if_exist(file: str):
	if is_file_exist(file) is True:
		os.remove(file)


def write(file: str, with_new_line: bool, word: str):
	fp = open(file, "a")
	fp.write(word)
	if with_new_line:
		fp.write('\n')
	fp.close()


def write(file: str, with_new_line: bool, separator: str, words: []):
	fp = open(file, "a")
	fp.write(separator.join(words))
	if with_new_line:
		fp.write('\n')
	fp.close()


if __name__ == "__main__":
	print(is_file_empty('/assets/history/ticks/night/MTX00/test.csv'))
