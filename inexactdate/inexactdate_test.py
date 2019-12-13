import unittest
from inexactdate.inexactdates import InexactDate
# TODO write tests


class InexactDateTest(unittest.TestCase):
    def test(self):
        # week
        y,m,d,y2,m2,d2 = InexactDate('week', 2019, 12, 12).date_struct
        self.assertEqual(d, 9)
        self.assertEqual(d2, 15)
        # month
        y,m,d,y2,m2,d2 = InexactDate('month', 2019, 12).date_struct
        self.assertEqual(d, 1)
        self.assertEqual(d2, 31)

        # quarter
        y,m,d,y2,m2,d2 = InexactDate('quarter_year', 2019, 12).date_struct
        self.assertEqual(m, 10); self.assertEqual(m2, 12)
        self.assertEqual(d, 1); self.assertEqual(d2, 31)

        # decade
        y,m,d,y2,m2,d2 = InexactDate('decade', 1955).date_struct
        self.assertEqual(y, 1950); self.assertEqual(y2, 1959)

        # cenutury
        y,m,d,y2,m2,d2 = InexactDate('century', 1955).date_struct
        self.assertEqual(y, 1901); self.assertEqual(y2, 2000)

if __name__ == '__main__':
    unittest.main()