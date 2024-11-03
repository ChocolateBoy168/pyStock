
import http.client
import re
import threading
import uuid
from argparse import ArgumentParser

from src.lib.my_lib.module.LoggerModule import LoggerWithRotate, Logger
from src.lib.my_lib.utils.DatetimeUtil import DatetimeUtil
from src.lib.my_lib.utils.JsonUtil import JsonUtil

version = "1.0.0"


class MyCustomError(Exception):
	def __init__(self, *args):
		if args:
			self.message = args[0]
		else:
			self.message = None

	def __str__(self):
		if self.message:
			return 'MyCustomError, {0} '.format(self.message)
		else:
			return 'MyCustomError has been raised'






def is_not_empty_array(data):
	return (data is not None) and (isinstance(data, list) is True) and (len(data) > 0)


'''
def http_post(host, port, path, params,
              read_to_response_wrapper, async_fn=None,
              is_ssl=False,
              timeout=10,
              _thread=True,
              _inner_return=[None] * 1):
    if _thread is True:
        t = threading.Thread(target=http_post,
                             args=[host, port, path, params, read_to_response_wrapper, async_fn, is_ssl, timeout, False,
                                   _inner_return])
        t.start()
        if async_fn is None:  # for sync
            t.join()
            return _inner_return[0]
        # return t
    else:
        try:
            # headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            # params_data = urllib.parse.urlencode(params)

            headers = {'Content-type': 'application/json'}
            json_data = json.dumps(params)
            if is_ssl:
                conn = http.client.HTTPSConnection(host, port, timeout=timeout)
            else:
                conn = http.client.HTTPConnection(host, port, timeout=timeout)
            conn.request("POST", path, json_data, headers)
            r = conn.getresponse()
            # print("status:\n{}\nheaders:\n{}\nread:\n{}\n".format(r.status, r.getheaders(), r.read()))
            _inner_return[0] = read_to_response_wrapper(r)  # for sync
            if async_fn is not None:  # for async
                async_fn(_inner_return[0])
        except Exception as e:
            msg = "Exception 1 => {0}".format(e)
            Logger.error(msg)
            _inner_return[0] = read_to_response_wrapper(e)  # for sync
            if async_fn is not None:  # for async
                async_fn(_inner_return[0])
        finally:
            if conn is not None:
                conn.close()
'''


def http_post(host, port, path, params,
			  read_to_response_wrapper, async_fn=None,
			  is_ssl=False,
			  timeout=10,
			  _thread=True,
			  _inner_return=[None] * 1):
	return http_request(host, port, "POST", path, params,
						read_to_response_wrapper, async_fn,
						is_ssl,
						timeout,
						_thread,
						_inner_return)


def http_get(host, port, path, params,
			 read_to_response_wrapper, async_fn=None,
			 is_ssl=False,
			 timeout=10,
			 _thread=True,
			 _inner_return=[None] * 1):
	return http_request(host, port, "GET", path, params,
						read_to_response_wrapper, async_fn,
						is_ssl,
						timeout,
						_thread,
						_inner_return)


# todo 這目前 param只針對json , 之後須搭配  requests.post 混用 for form params
def http_request(host, port, method, path, params,
				 read_to_response_wrapper, async_fn=None,
				 is_ssl=False,
				 timeout=10,
				 _thread=True,
				 _inner_return=[None] * 1):
	'''
		sync  : async_fn is None
		async : async_fn is not None
	'''

	if _thread is True:
		t = threading.Thread(target=http_request,
							 args=[host, port, method, path, params, read_to_response_wrapper, async_fn, is_ssl,
								   timeout, False,
								   _inner_return])
		t.start()
		if async_fn is None:  # for sync
			t.join()
			return _inner_return[0]
	# return t
	else:
		try:
			# headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
			# params_data = urllib.parse.urlencode(params)

			headers = {'Content-type': 'application/json'}
			# json_data = json.dumps(params)
			json_data = JsonUtil.to_json_str(params, ensure_ascii=True)
			# json_data = JsonUtil.to_json_str(params) #  'latin-1' codec can't encode characters in position 403-404: Body ('做多') is not valid Latin-1. Use body.encode('utf-8') if you want to send it encoded in UTF-8.
			if is_ssl:
				conn = http.client.HTTPSConnection(host, port, timeout=timeout)
			else:
				conn = http.client.HTTPConnection(host, port, timeout=timeout)
			conn.request(method, path, json_data, headers)
			r = conn.getresponse()
			# print("status:\n{}\nheaders:\n{}\nread:\n{}\n".format(r.status, r.getheaders(), r.read()))
			_inner_return[0] = read_to_response_wrapper(r)  # for sync
			if async_fn is not None:  # for async
				async_fn(_inner_return[0])
		except Exception as e:
			msg = "Exception 1 => {0}".format(e)
			LoggerWithRotate.error(msg)
			_inner_return[0] = read_to_response_wrapper(e)  # for sync
			if async_fn is not None:  # for async
				async_fn(_inner_return[0])
		finally:
			if conn is not None:
				conn.close()


def sys_mac_addr(way=2):
	result = None
	if result is None:  # Using getnode() + format() [ This is for better formatting ]
		# after each 2 digits, join elements of getnode().
		''' 
		#fail
		list = ['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
				  for ele in range(0, 2 * 6, 2)][::-1]
		'''
		l = ['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
			 for ele in range(0, 8 * 6, 8)][::-1]
		result = ":".join(l)

	if result is None:  # Using getnode() + findall() + re()[ This is for reducing complexity]
		l = re.findall('..', '%012x' % uuid.getnode())
		result = ":".join(l)

	if result is None:  # Using uuid.getnode()
		result = hex(uuid.getnode())

	return result


def random_str(size):
	return str(uuid.uuid1()).replace('-', '')[:size]


def parse_arg(name):
	return parse_args([name])


def parse_args(names):
	ap = ArgumentParser(description='Parse args')
	result = []
	for name in names:
		# todo 小心 name bug? ex: '--api_path' 改成 '--api_path2' 也可以parse, 似乎認關鍵字
		ap.add_argument(
			name,
			dest=name,
			help=f'need arg \"{name}\"',
			default=None,
			type=str
		)
	namespace = ap.parse_args()
	# ap.print_help()
	for name in names:
		val = namespace.__dict__[name]
		if val is None:
			Logger.warning(f'Maybe miss arg \"{name}\"!')
		result.append(val)
	return result


def any_of(items, fn):
	if (items is not None) and (len(items) >= 1):
		return any([fn(item) for item in items])  # any([]) is False
	else:
		raise RuntimeError("items 至少要1個以上")


def all_of(items, fn):
	if (items is not None) and (len(items) >= 1):
		return all([fn(item) for item in items])  # all([]) is True
	else:
		raise RuntimeError("items 至少要1個以上")


def any_compare_of(items, compare_fn):
	if (items is not None) and (len(items) >= 2):
		ary = []
		for num, element in enumerate(items):
			if num < len(items) - 1:
				ary.append(compare_fn(items[num], items[num + 1]))
		return any(ary)
	else:
		raise RuntimeError("items 至少要2個以上才可以比較")


def all_compare_of(items, compare_fn):
	if (items is not None) and (len(items) >= 2):
		ary = []
		for num, element in enumerate(items):
			if num < len(items) - 1:
				ary.append(compare_fn(items[num], items[num + 1]))
		return all(ary)
	else:
		raise RuntimeError("items 至少要2個以上才可以比較")


if __name__ == "__main__":
	print(sys_mac_addr())
	print(DatetimeUtil.utc_now_format_str())
	print(DatetimeUtil.today_to_utc())
