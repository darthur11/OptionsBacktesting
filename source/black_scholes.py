import datetime
import math

import scipy.stats


class BlackScholes:
    def __init__(self, S, K, r, T_start, T_end, sig):
        '''
        :param S: underlying spot price
        :param K: strike
        :param r: risk-free rate
        :param T: time to expiration in days
        :param sig: volatility, in %
        '''
        self.r = r
        self.K = K
        self.S = S
        T_start_dt = datetime.datetime.strptime(T_start, "%Y-%m-%d").date()
        T_end_dt = datetime.datetime.strptime(T_end, "%Y-%m-%d").date()
        self.delta_days = T_end_dt - T_start_dt
        self.T = float(self.delta_days.days)/250
        self.sig = sig * math.sqrt(250)

    def get_metrics(self):
        d1 = (math.log(self.S/self.K) + (self.r + self.sig**2/2)*self.T) / (self.sig*math.sqrt(self.T))
        d2 = d1 - self.sig * math.sqrt(self.T)
        return d1, d2

    def price_call(self):
        d1, d2 = self.get_metrics()
        prob_d1, prob_d2 = scipy.stats.norm.cdf(d1), scipy.stats.norm.cdf(d2)
        value = self.S * prob_d1 - self.K * math.exp(-self.r * self.T) * prob_d2
        return value

    def price_put(self):
        d1, d2 = self.get_metrics()
        prob_d1, prob_d2 = scipy.stats.norm.cdf(-d1), scipy.stats.norm.cdf(-d2)
        value = self.K * math.exp(-self.r * self.T) * prob_d2 - self.S * prob_d1
        return value

    def get_price(self, put_call):
        if put_call=="C":
            return self.price_call()
        elif put_call=="P":
            return self.price_put()
        else:
            print("???")