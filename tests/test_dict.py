import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        a = {
            '2022-01-01':{
                #'underlying': 20,
                ('2022-01-16', 20): (1,1, 1, 2),
                ('2022-01-16', 21): (0.5, 1.5, 1, 3)
            }
        }
        print([m for m in a['2022-01-01'].items() if m[1][3]==2])
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
