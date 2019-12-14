from datetime import datetime, timedelta
from calendar import monthrange
from scipy import stats
from math import sqrt, log, exp, ceil
import numpy as np

# the most frequent models for constructing an inexact dates fuzzy set
# for others use 'precalculated' and provide the set

date_model = {
    'date',  # full date MDY
    'week',  # from Monday to Sunday; provide date,
    'month',  # provide year and month
    'quarter_year',  # provide year and month (any month in a quarter)
    'season',  # winter, summer / provide year and month (month starting a season), only for North hemisphere
    'year',  # provide year
    'decade',  # provide year
    'century',  # provide year
    'precalculated',  # fuzzy set is provided
    'inferred',  # inferred date e.g. DOB of a person who become mother on some date
}

date_inferred = {
    'DOB_mother' : 60*365, # DOB of person that became mother at date
    'DOB_father': 90*365, # DOB of person that became father at date
    'DOB_baptized': 365, # DOB of person that has been baptised at the date
    'DOB_DOD': 120*365, # DOB of person that has died at the date
}

# the most frequent models for modifying
# for others use 'precalculated' date model and provide the set
date_qualification = {
    None,  # without qualification
    'start',  # start, beginning e.g. the early ...
    'mid',  # middle e.g. the middle of the
    'end',  # e.g. the late
    'firsthalf',  # e.g. the first half of
    'secondhalf',  # e.g. the second half of
    'earlydecades',  # e.g. the early decades - only for century

}


class InexactDate:
    """Inexact date type.

    Constructors:

    __new__()
    fromTimex()
    fromText()

    Operators:

    __repr__, __str__
    __eq__, __le__, __lt__, __ge__, __gt__, __hash__

    Methods:

    toText()

    Properties (readonly):
    year_from, month_from, day_from, year_to, month_to, day_to,
    model, expressed_range, intended_range, certainty
    """
    __slots__ = '_year_from', '_month_from', '_day_from', '_year_to', '_month_to', '_day_to', \
                '_model', '_qualification', '_intended_range', '_certainty', '_inferred_model', \
                '_fset', '_first_nonnull_date', \
                '_hashcode'

    def __new__(cls, model, year_from, month_from=None, day_from=None, year_to=None, month_to=None, day_to=None,
                qualification=None, intended_range=1, certainty=0.9, inferred_model=None):

        """Constructor.

        Arguments:

        model, year_from, month_from, day_from, year_to, month_to, day_to, intended_range=1, certainty=0.9 (required base 2)
        *_to are inclusive interval boundary
        """
        if model not in date_model:
            raise ValueError('Unknown date model!')
        if qualification not in date_qualification:
            raise ValueError('Unknown qualification!')

        if model == 'date':
            if not year_from or not month_from or not day_from:
                raise ValueError('Please specify year, month and day')
            year_to, month_to, day_to = year_from, month_from, day_from
        elif model == 'week':
            if not year_from or not month_from or not day_from:
                raise ValueError('Please specify year, month and day')
            dt = datetime(year_from, month_from, day_from)
            start = dt - timedelta(days=dt.weekday())
            year_from, month_from, day_from = start.year, start.month, start.day
            end = start + timedelta(days=6)
            year_to, month_to, day_to = end.year, end.month, end.day
        elif model == 'month':
            if not year_from or not month_from:
                raise ValueError('Please specify year and month ')
            start = datetime(year_from, month_from, 1)
            year_from, month_from, day_from = start.year, start.month, start.day
            end = start + timedelta(monthrange(year_from, month_from)[1]-1)
            year_to, month_to, day_to = end.year, end.month, end.day
        elif model == 'quarter_year':
            if not year_from or not month_from:
                raise ValueError('Please specify year and month ')
            start = datetime(year_from, max(filter(lambda i: i <= month_from, [1,4,7,10])), 1)
            year_from, month_from, day_from = start.year, start.month, start.day
            end = start + timedelta(monthrange(year_from, month_from)[1]) + \
                  timedelta(monthrange(year_from, month_from + 1)[1]) + \
                  timedelta(monthrange(year_from, month_from + 2)[1] - 1)
            year_to, month_to, day_to = end.year, end.month, end.day
        elif model == 'season':
            #  TODO check usage of Winter YEAR
            if not year_from or not month_from in (3,6,9,12):
                raise ValueError('Please specify year and the first month of the season')
            day_from = 21 if month_from == 9 else 23
            start = datetime(year_from, month_from, day_from)
            year_from, month_from, day_from = start.year, start.month, start.day
            end = start + timedelta(81)
            year_to, month_to, day_to = end.year, end.month, 22 if end.month == 9 else 20
        elif model == 'year':
            if not year_from:
                raise ValueError('Please specify year')
            year_from, month_from, day_from = year_from, 1, 1
            year_to, month_to, day_to = year_from, 12, 31
        elif model == 'decade':
            if not year_from:
                raise ValueError('Please specify year')
            year_from, month_from, day_from = (year_from // 10)*10, 1, 1
            year_to, month_to, day_to = (year_from // 10)*10+9, 12, 31
        elif model == 'century':
            if not year_from:
                raise ValueError('Please specify year')
            year_from, month_from, day_from = (year_from // 100)*100+1, 1, 1
            year_to, month_to, day_to = (year_from // 100)*100+100, 12, 31
        elif model == 'inferred':
            if not inferred_model or inferred_model not in date_inferred.keys():
                raise ValueError('Please specify model for inferring: '+', '.join(date_inferred.keys()))
            if not year_from:
                raise ValueError('Please specify year (and optionally month and day')
            year_to = year_from  # infer to the past
            month_to = month_from if month_from else 6
            day_to = day_from if day_from else 15
            d = datetime(year_to, month_to, day_to) - timedelta(date_inferred[inferred_model])
            year_from, month_from, day_from = d.year, d.month, d.day
        else:
            raise NotImplemented

        self = object.__new__(cls)

        self._year_from, self._month_from, self._day_from = year_from, month_from, day_from
        self._year_to, self._month_to, self._day_to = year_to, month_to, day_to
        self._hashcode = -1
        self._qualification = qualification
        self._certainty = certainty
        self._model = model
        self._inferred_model = inferred_model
        self._intended_range = intended_range

        if model != 'precalculated':
            if self._intended_range==1:
                self.__gen_fset_norm__()
            else:
                raise NotImplementedError

        return self

    # Read-only field accessors
    @property
    def date_struct(self):
        return self._year_from, self._month_from, self._day_from, self._year_to, self._month_to, self._day_to

    @property
    def fset(self):
        return self._first_nonnull_date, self._fset

    # generate fuzzy set
    def __gen_fset_norm__(self):
        first_day = datetime(self._year_from, self._month_from, self._day_from)
        last_day = datetime(self._year_to, self._month_to, self._day_to)
        span = (last_day-first_day).days + 1  # inclusive boundary

        if not self._inferred_model:
            if not self._qualification:  # uniform
                dist = stats.uniform
            elif self._qualification == 'start':
                dist = stats.beta(1, 3)
            elif self._qualification == 'end':
                dist = stats.beta(3, 1)
            elif self._qualification == 'mid':
                dist = stats.beta(5, 5)
            else:
                raise ValueError('Unknown qualification')
        else:
            # TODO - find better empirical distribution
            if self._inferred_model ==  'DOB_mother':
                dist = stats.beta(9.3, 7)
            elif self._inferred_model ==  'DOB_father':
                dist = stats.beta(9.3, 7)
            elif self._inferred_model ==  'DOB_baptized':
                dist = stats.beta(6, 2)
            elif self._inferred_model ==  'DOB_DOD':
                dist = stats.beta(8, 15)
            else:
                raise ValueError('Unknown inferred model')

        distv = dist.pdf(np.linspace(0.01, 0.99, span)) * self._certainty

        # normalisation
        if distv.max() > 1.:
            distv = distv / distv.max()

        # extend for uncertainty (1-certainty)
        fuzzy_plus_span = 0
        if self._certainty < 1:
            uncertainty = 1 - self._certainty
            # TODO find better span and probability distribution by empirical data
            fuzzy_plus_span = ceil((10 * sqrt(span))/self._certainty)  # extend for uncertainty to the both sides
            minv = distv.min()
            lamb = -(log(0.01))/fuzzy_plus_span  # lambda parameter for exponential distribution that covers 99% probabilty mass

            expf = lambda x: lamb*exp(-1*lamb*x)

            # expand fuzzy_plus_span if the largest value if greater then the minimal value in distribution
            distvf = [100.]
            num_extend = 0
            # TODO solve tail extension for skewed intervals
            while distvf[0] > minv:
                distvf = np.array(list(map(expf, [a + 0.5 for a in range(
                    fuzzy_plus_span)])))  # middle values for a crude aprox to sum to 1
                distvf = distvf / sum(distvf)
                distvf = distvf * (uncertainty / 2)
                num_extend += 1
                if num_extend > 4:
                    break

        self._fset = np.zeros((span+2*fuzzy_plus_span))
        self._fset[fuzzy_plus_span:fuzzy_plus_span+span] = distv
        if fuzzy_plus_span>0:
            self._fset[:fuzzy_plus_span] = np.flip(distvf, 0)
            self._fset[fuzzy_plus_span+span:] = distvf

        self._first_nonnull_date = (first_day - timedelta(days=fuzzy_plus_span)).toordinal()


if __name__ == '__main__':
    # test
    dayd, dayf = InexactDate('year', 1066, qualification='end', certainty=0.3).fset
    print(len(dayf))