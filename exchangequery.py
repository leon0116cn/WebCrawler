from datetime import datetime, timedelta
import sys
import requests
from bs4 import BeautifulSoup


TIME_OUT = 3

class ExchangeRate:

    def __init__(self, host, rate_date=None):
        self._rate_date = rate_date if rate_date else datetime.now().strftime('%Y-%m-%d')
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        self._web_url = host + 'cardholderServ/serviceCenter/rate?language=cn'
        self._s = requests.Session()
        r = self._s.get(self._web_url, headers=self._headers, timeout=TIME_OUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        base_currency_list = soup.find_all(id='baseCurrency')
        self._base_currency = tuple(sorted([base['val'] for base in base_currency_list if base['val'] != '扣账币种']))
        trans_currency_list = soup.find_all(id='transactionCurrency')
        self._transaction_currency = tuple(sorted([trans['val'] for trans in trans_currency_list if trans['val'] != '交易币种']))
        self._search_url = host + soup.find(id='rateForm')['action']

    def get_exchange_rates(self):
        for base in self._base_currency:
            for transaction in self._transaction_currency:
                print(self._query_exchange_rate(base, transaction, self._rate_date))

    def _query_exchange_rate(self, base_currency, transaction_currency, query_date):
        payload = {
            'curDate': query_date,
            'baseCurrency': base_currency,
            'transactionCurrency': transaction_currency
        }
        if base_currency == transaction_currency:
            return base_currency, transaction_currency, query_date, 1
        r = self._s.post(self._search_url, data=payload, timeout=TIME_OUT)
        r.raise_for_status()
        rate_json = r.json()
        exchange_rate = rate_json.get('exchangeRate')
        update_date = datetime.fromtimestamp(int(rate_json.get('updateDate')) / 1000).strftime('%Y-%m-%d')
        return base_currency, transaction_currency, update_date, exchange_rate

    @property
    def base_currency(self):
        return self._base_currency

    @property
    def transaction_currency(self):
        return self._transaction_currency


def main():
    rate = ExchangeRate(sys.argv[1], rate_date=(datetime.now().strftime('%Y-%m-%d')))
    print(rate.base_currency)
    print(rate.transaction_currency)
    print(rate.get_exchange_rates())


if __name__ == '__main__':
    main()
