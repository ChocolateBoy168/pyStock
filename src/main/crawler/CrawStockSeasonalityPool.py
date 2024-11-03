'''
  解決問題: Can't get attribute '_pool' on <module '__main__'
  使用 multi processing , pool 需另外放在一個檔案,  避免放在同一個模組上.
'''

def a_pool(args):
	from src.main.crawler.CrawStockSeasonality import CrawStockSeasonality
	css = CrawStockSeasonality.instance()
	records = []
	if args == 'quit_browser':  # todo 如果兩個 process 以上[process_num > 2]那該如何讓每個 process裡的 browser都關閉？
		if css.browser != None:
			css.browser.close()
			css.browser.quit()
	else:
		css.init_browser_if_empty()
		# record = css.start_request(*args) # for set(...)
		records = css.start_request(args)  # for str
	return records

