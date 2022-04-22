# Coco/l reader
# COMPILER name
#  ScannerSpecifications
#  ParserSpecifications
#  END name .
#  .

VOCABULARY_RE = {
    'ident': '^[a-zA-Z_][a-zA-Z0-9]*',
    'number': '^[0-9]+',
    'string': '^\".*\"',
    'char': '^\'.\'',
}

LINE_COMMENT_INDICATOR = '//'
START_MULTILINE_COMMENT_INDICATOR = '/*'
END_MULTILINE_COMMENT_INDICATOR = '*/'

COCOL_KEYWORDS = {
    'ANY',
    'CHARACTERS',
    'COMMENTS',
    'COMPILER',
    'CONTEXT',
    'END',
    'FROM',
    'IF',
    'IGNORE',
    'IGNORECASE',
    'NESTED',
    'out',
    'PRAGMAS',
    'PRODUCTIONS',
    'SYNC',
    'TO',
    'TOKENS',
    'WEAK'
}

SPECIAL_CHARACTERS = {
    '=',
    '.'
    '|',
    '()',
    '[]',
    '\{\}',
    '/*',
    '*/',
}