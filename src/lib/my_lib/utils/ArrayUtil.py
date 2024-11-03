# class ArrayUtil:

def head(ary: [], num: int):
	return ary[:num]


def tail(ary: [], num: int):
	return ary[-num:]


if __name__ == "__main__":
	ary = [1, 2, 3, 4, 5, 6]
	print(head(ary, 3))
	print(tail(ary, 3))
