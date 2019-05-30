from datetime import datetime
import sys
import requests
from bs4 import BeautifulSoup


TIME_OUT = 5


class ExchangeRate:

    def __init__(self, host, rate_date=None):
        self._rate_date = rate_date if rate_date else datetime.now().strftime('%Y-%m-%d')
        self._exchange_rates = {}
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        self._web_url = host + '/cardholderServ/serviceCenter/rate?language=cn'
        r = requests.get(self._web_url, headers=self._headers, timeout=TIME_OUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        a_b = [(b['val'], b.string) for b in soup.find_all(id='baseCurrency') if b['val'] != '扣账币种']
        self._base_currency = dict(sorted(a_b, key=lambda x: x[0]))
        a_t = [(t['val'], t.string) for t in soup.find_all(id='transactionCurrency') if t['val'] != '交易币种']
        self._trans_currency = dict(sorted(a_t, key=lambda y: y[0]))
        self._search_url = host + soup.find(id='rateForm')['action']

    def get_exchange_rates(self):
        for t_k, t_v in self._trans_currency.items():
            base_dict = {}
            s = requests.Session()
            for b_k, b_v in self._base_currency.items():
                if b_k == t_k:
                    base_dict[b_k] = (t_v, t_k, b_k, b_v, self._rate_date, 1)
                else:
                    payload = {
                     'curDate': self._rate_date,
                     'baseCurrency': b_k,
                     'transactionCurrency': t_k
                    }
                    r = s.post(self._search_url, data=payload, timeout=TIME_OUT)
                    r.raise_for_status()
                    rate_json = r.json()
                    rate = rate_json.get('exchangeRate')
                    update_date = datetime.fromtimestamp(int(rate_json.get('updateDate'))/1000).strftime('%Y-%m-%d')
                    base_dict[b_k] = (t_k, t_v, b_k, b_v, update_date, rate)
            self._exchange_rates = {t_k: base_dict}
            print(self._exchange_rates)
        return self._exchange_rates

    @property
    def base_currency(self):
        return self._base_currency

    @property
    def transaction_currency(self):
        return self._trans_currency

    @property
    def rate_date(self):
        return self._rate_date


def main():
    rate = ExchangeRate(sys.argv[1])
    print(rate.transaction_currency)
    print(rate.base_currency)
    print(rate.get_exchange_rates())


if __name__ == '__main__':
    main()
