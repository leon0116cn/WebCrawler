from datetime import datetime, timedelta
import sys
import requests
from bs4 import BeautifulSoup


TIME_OUT = 5

class ExchangeRate:

    def __init__(self, host, rate_date=None):
        self._rate_date = rate_date if rate_date else datetime.now().strftime('%Y-%m-%d')
        self._exchange_rate = []
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        self._web_url = host + '/cardholderServ/serviceCenter/rate?language=cn'
        r = requests.get(self._web_url, headers=self._headers, timeout=TIME_OUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        base_list = [(base['val'], base.string) for base in soup.find_all(id='baseCurrency') if base['val'] != '扣账币种']
        self._base_currency = sorted(base_list, key=lambda x: x[0])
        print(self._base_currency)
        trans_list = [(trans['val'], trans.string) for trans in soup.find_all(id='transactionCurrency') if trans['val'] != '交易币种']
        self._transaction_currency = sorted(trans_list, key=lambda y: y[0])
        print(self._transaction_currency)
        self._search_url = host + soup.find(id='rateForm')['action']

    def get_exchange_rates(self):
        for transaction in self._transaction_currency:
            base_list = []
            s = requests.Session()
            for base in self._base_currency:
                if base[0] == transaction[0]:
                    base_list.append((base[0], self._rate_date, 1))
                else:
                    payload = {
                     'curDate': self._rate_date,
                     'baseCurrency': base[0],
                     'transactionCurrency': transaction[0]
                    }
                    r = s.post(self._search_url, data=payload, timeout=TIME_OUT)
                    r.raise_for_status()
                    rate_json = r.json()
                    exchange_rate = rate_json.get('exchangeRate')
                    update_date = datetime.fromtimestamp(int(rate_json.get('updateDate')) / 1000).strftime('%Y-%m-%d')
                    base_list.append((base[0], update_date, exchange_rate))
            self._exchange_rate.append({transaction[0]: base_list})
        return self._exchange_rate

    @property
    def base_currency(self):
        return self._base_currency

    @property
    def transaction_currency(self):
        return self._transaction_currency

    @property
    def rate_date(self):
        return self._rate_date


def main():
    rate = ExchangeRate(sys.argv[1])
    print(rate.get_exchange_rates())


if __name__ == '__main__':
    main()
