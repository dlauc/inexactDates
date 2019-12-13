import unittest
from inexactdate.inexactdates import InexactDate
# TODO write tests


class InexactDateTest(unittest.TestCase):
    def test(self):
        # week
        y,m,d,y2,m2,d2 = InexactDate('week', 2019, 12, 12).date_struct
        self.assertEqual(d, 9)
        self.assertEqual(d2, 15)

if __name__ == '__main__':
    unittest.main()