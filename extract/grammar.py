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
    STOLJG = ''
    for l in open('ld_grammar.txt'):
        if l[:1] != '#':
            STOLJG += l

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