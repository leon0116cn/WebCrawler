from datetime import datetime, timedelta
import sys
import requests
from bs4 import BeautifulSoup


class ExchangeRate:

    def __init__(self, host):
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        self._web_url = host + 'cardholderServ/serviceCenter/rate?language=cn'
        r = requests.get(self._web_url, headers=self._headers, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        base_currency_list = soup.find_all(id='baseCurrency')
        self._base_currency = (base['val'] for base in base_currency_list if base['val'] != '扣账币种')
        trans_currency_list = soup.find_all(id='transactionCurrency')
        self._transaction_currency = (trans['val'] for trans in trans_currency_list if trans['val'] != '交易币种')
        self._search_url = host + soup.find(id='rateForm')['action']

    def query_exchange_rate(self, base_currency, transaction_currency, query_date):
        payload = {
            'curDate': query_date,
            'baseCurrency': base_currency,
            'transactionCurrency': transaction_currency
        }
        r = requests.post(self._search_url, data=payload, timeout=5)
        r.raise_for_status()
        rate_json = r.json()
        exchange_rate = rate_json.get('exchangeRate')
        update_date = datetime.fromtimestamp(int(rate_json.get('updateDate')) / 1000).strftime('%Y-%m-%d')
        return update_date, exchange_rate

    @property
    def base_currency(self):
        return self._base_currency

    @property
    def transaction_currency(self):
        return self._transaction_currency


def main():
    rate = ExchangeRate(sys.argv[1])
#    print(rate.query_exchange_rate('CNY', 'USD', datetime.now().strftime('%Y-%m-%d')))
    print(rate.query_exchange_rate('CNY', 'USD', (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')))
    print(rate.query_exchange_rate('CNY', 'USD', (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')))


if __name__ == '__main__':
    main()
