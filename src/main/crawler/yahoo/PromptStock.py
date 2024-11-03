import requests
from bs4 import BeautifulSoup


class PromptStock():
	def __init__(self):
		self.template_url = "https://tw.stock.yahoo.com/q/q?s={0}"

	def getPrompt(self, stockNo):
		url = self.template_url.format(stockNo)
		print(url)
		try:
			result = requests.get(url)
			if result.status_code == 200:
				soup = BeautifulSoup(result.text, 'html.parser')
				# print(soup.prettify())
				data = {}
				# for table in soup.find_all('table'):
				#     print(table.text)
				table = soup.find_all('table')[2]
				rows = table.find_all('tr')
				titles = rows[0].find_all('th')
				titles = [ele.text.strip() for ele in titles]
				# print(titles)

				values = rows[1].find_all('td')
				values = [ele.text.strip() for ele in values]
				# print(values)

				data['stockNo'] = stockNo
				data['time'] = values[1]
				data['price'] = float(values[2]) if values[2] != '－' else -1
				data['buy'] = float(values[3]) if values[3] != '－' else -1
				data['sell'] = float(values[4]) if values[4] != '－' else -1
				data['number'] = int(values[6].replace(',', '')) if values[6] != '－' else -1
				data['lastClose'] = float(values[7]) if values[7] != '－' else -1
				data['open'] = float(values[8]) if values[8] != '－' else -1
				data['high'] = float(values[9]) if values[9] != '－' else -1
				data['low'] = float(values[10]) if values[10] != '－' else -1
				print(data)
				return data

		except Exception as e:
			print("getPrompt " + str(e))
		return None


if __name__ == "__main__":
	prompt = PromptStock()
	prompt.getPrompt(2303)
