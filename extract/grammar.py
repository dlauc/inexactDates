from nltk.parse.generate import generate
from nltk import ChartParser, FeatureEarleyChartParser
from nltk.grammar import CFG, FeatureGrammar
import pandas as pd
from num2words import num2words
import re

tok = re.compile(r'\w+|\S',re.UNICODE)

# pomoćni
def normalize(s):
    s = s.lower()
    return tok.findall(s)

def int_to_roman(input, lower=True):
    if not isinstance(input, type(1)):
        raise(TypeError, "expected integer, got %s" % type(input))
    if not 0 < input < 4000:
        raise(ValueError, "Argument must be between 1 and 3999")
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = []
    for i in range(len(ints)):
        count = int(input / ints[i])
        result.append(nums[i] * count)
        input -= ints[i] * count
    rec = ''.join(result)
    if lower:
        rec = rec.lower()
    return rec


def getStolj():
    # Gramatika za stoljeća
    # TODO pojednostiviti the of na poč i kraju kval
    STOLJG = """
    S[NORM=?n,QUAL=?q,CERT=?c] -> S_TOCNO | S_PRIB
    S_TOCNO[NORM=?n,QUAL=?q,CERT='1'] -> STOLJ[NORM=?n,QUAL=?q] 
    S_PRIB[NORM=?n,QUAL=?q,CERT='0.5'] -> ABOUT STOLJ[NORM=?n,QUAL=?q]
    ABOUT -> 'about' | 'approximately in' | 'approximately in' | 'around'
    CENT1 -> 'century'|'cent.'|'c.'
    CENT -> '-' CENT1 | CENT1
    AD -> 'ad'|'ce'|'a' '.' 'd' '.'|'c' '.' 'e.'
    BC -> 'bc'|'bce'|'b' '.' 'c' '.'|'b' '.' 'c' '.' 'e' '.'
    STOLJ_N -> CENT | CENT AD
    STOLJ_O -> CENT BC
    STOLJ_P[QUAL='start'] -> 'the' 'early' | 'the' 'start' 'of' 'the' | 'the' 'start' 'of' | 'start' 'of' 'the' | 'start' 'of' | 'the' 'beginning' 'of' 'the' | 'the' 'beginning' 'of' | 'beginning' 'of' 'the' | 'beginning' 'of' | 'beginning' 'in' | 'beginning' 'in' 'the' | 'early' | 'the' 'early' | 'early' 'in' 'the' | 'early' 'in' | 'the' 'early' 'years' 'of' 'the' | 'the' 'early' 'years' 'in' 'the' | 'early' 'years' 'of' 'the' | 'early' 'years' 'of' | 'earlier' | 'the' 'dawn' 'of' 'the' | 'dawn' 'of' 'the' | 'the' 'dawn' 'of' 
    STOLJ_P[QUAL='end'] -> 'the' 'late' | 'late' | 'the' 'end' 'of' 'the' | 'the' 'end' 'of' | 'end' 'of' | 'end' 'of' 'the' | 'later' | 'late' 'in' 'the' | 'the' 'dusk' 'of' 'the' | 'dusk' 'of' 'the' | 'the' 'dusk' 'of' 
    STOLJ_P[QUAL='mid'] -> 'the' 'mid' '-' | 'the' 'middle' 'of' 'the' | 'the' 'mid' | 'mid' '-' | 'mid' | 'the' 'middle'
    STOLJ_P[QUAL='fhalf'] -> 'the' 'first' 'half' 'of' 'the' | 'first' 'half' 'of' 'the' | 'first' 'half' 'of' | 'the' 'first' 'half' 'of'
    STOLJ_P[QUAL='shalf'] -> 'the' 'second' 'half' | 'the' 'second' 'half' 'of' 'the' | 'the' 'letter' 'half' 'of' 'the' | 'the' 'letter' 'half' | 'the' 'latter' 'half' 'of' 'the' | 'the' 'latter' 'half' | 'the' 'last' 'half' 'of' 'the'
    STOLJ_P[QUAL='dec'] -> 'the' 'early' 'decades' 'of' 'the' | 'the' 'early' 'decades' 'of' | 'early' 'decades' 'of' 'the' | 'early' 'decades' 'of' | 'the' 'last' 'decades' 'of' 'the' | 'the' 'last' 'decades' 'of' | 'last' 'decades' 'of' 'the' | 'last' 'decades' 'of' | 'the' 'first' 'two' 'decades' 'of' 'the' | 'the' 'first' 'two' 'decades' 'of' | 'first' 'two' 'decades' 'of' | 'first' 'two' 'decades' 'of' 'the' | 'the' 'last' 'two' 'decades' 'of' 'the' | 'the' 'last' 'two' 'decades' 'of' | 'last' 'two' 'decades' 'of' 'the' | 'last' 'two' 'decades' 'of' | 'first' 'treee' 'decades' 'of' 'the' | 'first' 'tree' 'decades' 'of' | 'the' 'first' 'tree' 'decades' 'of' 'the' | 'the' 'first' 'tree' 'decades' 'of' | 'the' 'last' 'tree' 'decades' 'of' 'the' | 'the' 'last' 'tree' 'decades' 'of' | 'last' 'tree' 'decades' 'of' 'the' | 'last' 'tree' 'decades' 'of'
    STOLJ_P[QUAL='quart1'] -> 'the' 'first' 'quarter' 'of' 'the' | 'the' 'first' 'quarter' 'of' | 'first' 'quarter' 'of' 'the' | 'first' 'quarter' 'of'
    STOLJ_P[QUAL='quart2'] -> 'the' 'second' 'quarter' 'of' 'the' | 'the' 'second' 'quarter' 'of' | 'second' 'quarter' 'of' 'the' 
    STOLJ_P[QUAL='quart3'] -> 'the' 'third' 'quarter' 'of' 'the' | 'the' 'third' 'quarter' 'of' | 'second' 'third' 'of' 'the' 
    STOLJ_P[QUAL='quart4'] -> 'the' 'fourth' 'quarter' 'of' 'the' | 'the' 'fourth' 'quarter' 'of' | 'fourth' 'quarter' 'of' | 'the' 'last' 'quarter' 'of' 'the' | 'the' 'last' 'quarter' 'of' | 'last' 'quarter' 'of' 'the' | 'last' 'quarter' 'of' 
    STOLJ[NORM=?n,QUAL='0'] -> 'the' STOLJ_S[NORM=?n] STOLJ_N | STOLJ_S[NORM=?n] STOLJ_N
    STOLJ[NORM=?n,QUAL='0'] -> 'the' STOLJ_S[NORM=?n] STOLJ_O | STOLJ_S[NORM=?n] STOLJ_O
    STOLJ[NORM=?n,QUAL=?q] -> STOLJ_P[QUAL=?q] STOLJ_S[NORM=?n] STOLJ_N
    STOLJ[NORM=?n,QUAL=?q] -> STOLJ_P[QUAL=?q] STOLJ_PNE[NORM=?n] STOLJ_O
    """

    for i in range(1,50):
      format_str = (i-1, int_to_roman(i),  int_to_roman(i),  int_to_roman(i)+num2words(i,to='ordinal', lang='en')[-2:],
                    i,i,num2words(i,to='ordinal_num', lang='en'), num2words(i,to='cardinal', lang='en'), num2words(i,to='ordinal', lang='en'))
      p = "STOLJ_S[NORM='{:02d}xx'] -> '{}.'|'{}'|'{}'|'{}.'|'{}'|'{}'|'{}'|'{}'".format(*format_str)
      STOLJG += p+'\n'
      #print(p)

    for i in range(-50,0):
      format_str = (-i-1, int_to_roman(-i),  int_to_roman(-i),  int_to_roman(-i)+num2words(-i,to='ordinal', lang='en')[-2:],
                    -i,-i,num2words(-i,to='ordinal_num', lang='en'), num2words(-i,to='cardinal', lang='en'), num2words(-i,to='ordinal', lang='en'))
      p = "STOLJ_PNE[NORM='-{:02d}xx'] -> '{}.'|'{}'|'{}'|'{}.'|'{}'|'{}'|'{}'|'{}'".format(*format_str)
      STOLJG += p+'\n'
      #print(p)

    # generiranje
    grammar = FeatureGrammar.fromstring(STOLJG)

    return grammar, STOLJG

if __name__=='__main__':
    # test
    grammar, grammarS = getStolj()
    parser = FeatureEarleyChartParser(grammar)
    if False:
        for sentence in generate(grammar, n=1):
            print(' '.join(sentence))
        df1 = pd.read_csv('https://github.com/dlauc/inexactDates/raw/master/stoljeca_wiki.csv')
        print('različitih oblika = {}, ukupno = {}'.format(df1.text.count(), df1.n.sum()))
        test = df1[df1.n > 1]
        test = test.sort_values(by=['n'], ascending=False).reset_index(drop=True)
        ok = 0;
        neok = 0
        for i in range(0, 1000):
            s = normalize(test.at[i, 'text'])
            # print(test.at[i,'text'], s)
            try:
                trees = list(parser.parse(s))
                if len(trees) == 0:
                    print(s, 'neprepoznato')
                    neok += test.at[i, 'n']
                else:
                    # print(s, 'OK')
                    ok += test.at[i, 'n']
            except Exception as e:
                # neok += test.at[i,'n']
                print(e, s)

        print('ukupno ok/neok', ok, neok)

    s = normalize('the first quarter of the 20th century')
    print(s)
    t = parser.parse(s)
    t = list(t)[0]
    print(t)
    t.draw()