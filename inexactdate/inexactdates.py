from datetime import datetime, timedelta
from scipy import stats
from math import sqrt, log, exp
import numpy as np

# the most frequent models for constructing an inexact dates fuzzy set
# for others use 'precalculated' and provide the set

date_model = {
    'date',  # full date MDY
    'week',  # from Monday to Sunday; provide date,
    'month',  # provide year and month
    'quarter_year',  # provide year and month (any month in a quarter)
    'season',  # winter, summer / provide year and month (any month in a season)
    'year',  # provide year
    'decade',  # provide year
    'century',  # provide year
    'precalculated',  # fuzzy set is provided
    'inferred',  # inferred date e.g. DOB of a person who become mother on some date
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
                '_model', '_qualification', '_intended_range', '_certainty', \
                '_fset', '_first_nonnull_date', \
                '_hashcode'

    def __new__(cls, model, year_from, month_from=None, day_from=None, year_to=None, month_to=None, day_to=None,
                qualification=None, intended_range=1, certainty=0.9, inferred=None):

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

        self = object.__new__(cls)

        self._year_from, self._month_from, self._day_from = year_from, month_from, day_from
        self._year_to, self._month_to, self._day_to = year_to, month_to, day_to
        self._hashcode = -1
        self._qualification = qualification
        self._certainty = certainty
        self._model = model
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

        distv = dist.pdf(np.linspace(0.01, 0.99, span)) * self._certainty

        # extend for uncertainty (1-certainty)
        fuzzy_plus_span = 0
        if self._certainty < 1:
            uncertainty = 1 - self._certainty
            # TODO find better span and probability distribution by empirical data
            fuzzy_plus_span = 10 * round(sqrt(span))  # extend for uncertainty to the both sides
            minv = distv.min() / 2
            lamb = -(log(0.01))/fuzzy_plus_span  # lambda parameter for exponential distribution that covers 99% probabilty mass
            expf = lambda x: lamb*exp(-1*lamb*x)
            distvf = np.array(list(map(expf, range(fuzzy_plus_span)))) * uncertainty/2

            # expand fuzzy_plus_span if the largest value if greater then the minimal value in distribution
            while distvf[0] > minv:
                fuzzy_plus_span = round(fuzzy_plus_span*1.5)
                distvf = np.reciprocal(np.exp(np.linspace(0, 5, fuzzy_plus_span)))

        self._fset = np.zeros((span+2*fuzzy_plus_span))
        self._fset[fuzzy_plus_span:fuzzy_plus_span+span] = distv
        if fuzzy_plus_span>0:
            self._fset[:fuzzy_plus_span] = np.flip(distvf, 0)
            self._fset[fuzzy_plus_span+span:] = distvf

        self._first_nonnull_date = (first_day - timedelta(days=fuzzy_plus_span)).toordinal()


if __name__ == '__main__':
    # test
    dayf, dayd = InexactDate('date', 1066, 10, 1).fset
    print(len(dayd))
    weekf, weekd = InexactDate('week', 1066, 10, 1).fset
    print(len(weekd))
