from nltk.draw import CFGDemo, CFGEditor
from extract.grammar import getStolj

g,gs = getStolj()
CFGDemo(g , 'the early XI century')