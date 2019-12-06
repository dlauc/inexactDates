from nltk import CFG, ChartParser, RecursiveDescentParser
from nltk.tree import Tree
from nltk.draw.tree import TreeView

def test():
    STOLJG = """
    S -> DAN '.' MJESEC GODINA'.'
    ZNAMENKA -> '1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9'
    ZNAMENKA0 -> ZNAMENKA | '0'
    DAN -> ZNAMENKA | '1' ZNAMENKA0 | '2' ZNAMENKA0 | '30' | '31'
    MJESEC -> 'siječnja' | 'veljače' | 'ožujka' | 'travnja' | 'svibnja' | 'lipnja' | 'srpnja' | 'kolovoza' | 'listopada' | 'studenog' | 'prosinca'
    GODINA -> ZNAMENKA | ZNAMENKA ZNAMENKA0 | ZNAMENKA ZNAMENKA0 ZNAMENKA0 | ZNAMENKA ZNAMENKA0 ZNAMENKA0 ZNAMENKA0
    """
    grammar = CFG.fromstring(STOLJG)
    parser = RecursiveDescentParser(grammar)
    sent = '2 1 . siječnja 1 9 0 1 .'.split()
    print(sent)
    for tree in parser.parse(sent):
        print(tree)
        tree.draw()
        TreeView(tree)._cframe.print_to_file('output.ps')

def stolj():
    pass