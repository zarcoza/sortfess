import re

# Pattern regex untuk deteksi kata kotor & variasinya
BAD_WORDS_REGEX = {
    'asu':     r'a[\$s5]?u+',
    'wts':  r'w[3e][t7][e3][sz5]+',
    'bangsat': r'b[a4]ngs[a@]t',
    'kontol':  r'k[o0]nt[o0]l',
    'memek':   r'm[e3]m[e3]k',
    'wtb':       r'w[\W_][t7][\W_][b8]',                     # wtb, w.t.b, w7b, w+t+b
    'yatim':     r'y[\W_][a4][\W_]*t[\W_][i1][\W_]*[m]',      # yatim, y4tim, y@t1m
    'piatu':     r'p[\W_][i1][\W_][a4][\W_]t[\W_][u]',      # piatu, p14tu, pi4tuu
    'jual':      r'j[\W_][u][\W_][a4][\W_]*[l1]',             # jual, ju4l, jval
    'jualan':    r'j[\W_][u][\W_][a4][\W_][l1][\W_][a4][\W_]*[n]', # jualan, ju4l4n
    'kinci':     r'k[\W_][i1][\W_]*n[\W_][c][\W_]*[i1]',      # kinci, k1nc1
    'freelance': r'f[\W_]r[\W_][e3]{2}[\W_]l[\W_][a4][\W_]n[\W_]*c[\W_][e3]', # freelance, free1ance, fre3l4nce
    'jb':        r'j[\W_]*[b8]',                               # jb, j8
}

def contains_bad_word(text: str) -> bool:
    text = text.lower()
    for pattern in BAD_WORDS_REGEX.values():
        if re.search(pattern, text):
            return True
    return False