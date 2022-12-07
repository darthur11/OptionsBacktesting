import unittest

import black_scholes


class MyTestCase(unittest.TestCase):
    obj = black_scholes.BlackScholes(21.89, 22, 0.03, "2022-11-26", "2022-12-16", 0.052)

    eps = 10 ** -6
    bench_call_price = 2.000412
    bench_put_price = 2.057675

    def test_call_price_correct(self):
        call_price = self.obj.price_call()
        print(call_price)
        self.assertAlmostEqual(first=call_price, second=self.bench_call_price,
                               msg="They should be almost equal",
                               delta=self.eps)

    def test_put_price_correct(self):
        put_price = self.obj.price_put()
        print(put_price)
        self.assertAlmostEqual(first=put_price, second=self.bench_put_price,
                               msg="They should be almost equal",
                               delta=self.eps)


if __name__ == '__main__':
    unittest.main()
