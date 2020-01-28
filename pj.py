#TODO: pogledati može li se upotrebljivo ukrasti pprinter od astpretty


import enum, types, collections, contextlib


def identifikator(znak): return znak.isalnum() or znak == '_'


def pogledaj(mem, token):
    try: return mem[token.sadržaj]
    except KeyError: raise token.nedeklaracija() from None


# TODO: bolji API: Greška(poruka, pozicija ili token ili AST...)
# ali ostaviti i lex.greška() i parser.greška() for convenience
class Greška(Exception): """Baza za sve greške vezane uz poziciju u kodu."""
class LeksičkaGreška(Greška): """Greška nastala prilikom leksičke analize."""
class SintaksnaGreška(Greška): """Greška nastala prilikom sintaksne analize."""
class SemantičkaGreška(Greška):"""Greška nastala prilikom semantičke analize."""
class GreškaIzvođenja(Greška): """Greška nastala prilikom izvođenja."""


class Tokenizer:
    def __init__(self, string):
        self.pročitani, self.buffer, self.stream = [], None, iter(string)
        self.početak = self.i, self.j = 1, 0

    @property
    def pozicija(self): return self.i, self.j

    @property
    def sadržaj(self): return ''.join(self.pročitani)

    def čitaj(self):
        """Čita sljedeći znak iz buffera ili stringa."""
        znak = self.buffer or next(self.stream, '')
        self.pročitani.append(znak)
        self.buffer = None
        if znak == '\n':
            self.gornji_j = self.j
            self.i += 1
            self.j = 0
        else: self.j += 1
        return znak

    def vrati(self):
        """Poništava čitanje zadnjeg pročitanog znaka."""
        assert not self.buffer
        self.buffer = self.pročitani.pop()
        if self.j: self.j -= 1
        else:
            self.j = self.gornji_j
            self.i -= 1
            del self.gornji_j

    def pogledaj(self):
        """'Viri' u sljedeći znak, 'bez' čitanja."""
        znak = self.čitaj()
        self.vrati()
        return znak

    def slijedi(self, znak):
        """Čita sljedeći znak ako i samo ako je jednak očekivanom."""
        return self.čitaj() == znak or self.vrati()

    def zvijezda(self, uvjet):
        """Čita Kleene* (nula ili više) znakova koji zadovoljavaju uvjet."""
        while uvjet(self.čitaj()): pass
        self.vrati()

    def plus(self, uvjet):
        """Čita Kleene+ (jedan ili više) znakova koji zadovoljavaju uvjet."""
        prvi = self.čitaj()
        if not uvjet(prvi): raise self.greška('očekivan ' + uvjet.__name__)
        self.zvijezda(uvjet)
    
    def pročitaj(self, znak):
        """Čita zadani znak, ili prijavljuje leksičku grešku."""
        if znak != self.čitaj():
            raise self.greška('očekivano {!r}'.format(znak))

    def pročitaj_do(self, znak, uključivo=True):
        """Čita sve znakove do zadanog znaka."""
        self.zvijezda(lambda z: z and z != znak)
        if self.pogledaj() != znak:
            raise self.greška('{!r} nije pronađen'.format(znak))
        if uključivo: self.pročitaj(znak)

    def greška(self, info=''):
        """Konstruira leksičku grešku koja se treba prijaviti s raise."""
        if self.buffer: self.čitaj()
        poruka = 'Redak {}, stupac {}: '.format(*self.pozicija)
        poruka += 'neočekivan znak {!r}'.format(self.pročitani.pop())
        if info: poruka += ' (' + info + ')'
        return LeksičkaGreška(poruka)

    def token(self, tip):
        """Odašilje token."""
        t = Token(tip, self.sadržaj)
        t.početak = self.početak
        t.kraj = self.pozicija
        self.zanemari()
        return t

    def literal(self, odakle, case=True):
        """Odašilje doslovni token ako ga nađe, ili vrstu zadanu argumentom."""
        t = self.sadržaj if case else self.sadržaj.casefold()
        def p(odakle):
            if isinstance(odakle, enum.EnumMeta):
                for e in odakle:
                    if e.value == t or getattr(e.value, 'literal', None) == t:
                        return e
        nađen = p(odakle) or p(type(odakle))
        if nađen: return self.token(nađen)
        elif isinstance(type(odakle), enum.EnumMeta): return self.token(odakle)
        else: raise self.greška()

    def zanemari(self):
        """Resetira pročitano."""
        self.pročitani.clear()
        self.početak = self.pozicija


class E(enum.Enum):  # Everywhere
    """Često korišteni tipovi tokena, neovisno o konkretnom jeziku."""
    KRAJ = None      # End
    GREŠKA = '\x00'  # Error
    PRAZNO = ' '     # Empty
    VIŠAK = ''       # Extra


class Token(collections.namedtuple('TokenTuple', 'tip sadržaj')):
    # TODO: razmisliti je li Token unhashable, ili hashiran samo kao TokenTuple
    """Klasa koja predstavlja tokene."""
    def __new__(cls, tip, sadržaj):
        if isinstance(tip.value, type): cls = tip.value
        return super().__new__(cls, tip, sadržaj)

    def __init__(self, *args):
        # if self.tip is E.GREŠKA: prijavi grešku na početku tokena, ne na kraju
        self.uspoređeni = set()
        self.razriješen = False
    
    def __repr__(self):
        ime, sadržaj = self.tip.name, self.sadržaj
        if sadržaj not in {ime, ''}: ime += repr(self.sadržaj)
        return ime

    def __xor__(self, tip):
        """Vraća sebe (istina) ako je zadanog tipa, inače None (laž)."""
        if not isinstance(tip, set): tip = {tip}
        self.uspoređeni |= tip
        if self.tip in tip:
            self.razriješen = True
            return self

    def je(self, *tipovi):
        self.uspoređeni.update(tipovi)
        if self.tip in tipovi:
            self.razriješen = True
            return self

    def neočekivan(self, info=''):
        """Konstruira sintaksnu grešku: neočekivan tip tokena."""
        poruka = 'Redak {}, stupac {}: neočekivan token {!r}'
        if info: poruka += ' (' + info + ')'
        očekivano = ' ili '.join(t.name for t in self.uspoređeni if t!=self.tip)
        if očekivano: poruka += '\nOčekivano: ' + očekivano
        i, j = getattr(self, 'početak', '??')
        return SintaksnaGreška(poruka.format(i, j, self))

    if False:
      def redeklaracija(self, prvi=None):
        """Konstruira semantičku grešku redeklaracije."""
        i, j = getattr(self, 'početak', '??')
        poruka = 'Redak {}, stupac {}: redeklaracija {!r}'.format(i, j, self)
        if prvi is not None:
            info = 'Prva deklaracija je bila ovdje: redak {}, stupac {}'
            poruka += '\n' + info.format(*prvi.početak)
        return SemantičkaGreška(poruka)

    def nedeklaracija(self, dodatak=''):
        """Konstruira semantičku grešku nedeklariranog simbola."""
        i, j = getattr(self, 'početak', '??')
        poruka = 'Redak {}, stupac {}: nedeklarirano {!r}'.format(i, j, self)
        if dodatak: poruka += ' ' + dodatak.join('()')
        return SemantičkaGreška(poruka)

    def problem(self, info):
        """Konstruira grešku izvođenja."""
        poruka = 'Redak {}, stupac {}: {!r}: {}'
        i, j = getattr(self, 'početak', '??')
        return GreškaIzvođenja(poruka.format(i, j, self, info))

    def krivi_tip(self, *tipovi):
        """Konstruira semantičku grešku."""
        poruka = 'Redak {}, stupac {}: {!r}: tipovi ne odgovaraju: '
        poruka += ', '.join(map(str, tipovi))
        i, j = getattr(self, 'početak', '??')
        return SemantičkaGreška(poruka.format(i, j, self))

    @classmethod
    def kraj(cls):
        """Oznaka kraja niza tokena."""
        t = cls(E.KRAJ, '')
        t.početak = t.kraj = 'zadnji', 0
        t.razriješen = False
        return t


class Parser:
    def __init__(self, tokeni):
        self.buffer, self.stream = None, iter(tokeni)
        self.zadnji, self.KRAJ = None, Token.kraj()

    def čitaj(self):
        """Čitanje sljedećeg tokena iz buffera ili inicijalnog niza."""
        token = self.buffer
        if token is None:
            if self.zadnji is not None and not self.zadnji.razriješen:
                raise self.greška()
            token = next(self.stream, self.KRAJ)
        self.buffer = None
        self.zadnji = token
        return token

    def vrati(self):
        """Poništavanje čitanja zadnjeg pročitanog tokena."""
        assert not self.buffer, 'Buffer je pun'
        self.buffer = self.zadnji

    pogledaj = Tokenizer.pogledaj

    def pročitaj(self, *tipovi):
        """Čita jedan od dozvoljenih simbola, ili javlja sintaksnu grešku."""
        token = self.čitaj()
        if token ^ set(tipovi): return token
        self.vrati()
        raise self.greška()

    def slijedi(self, *tipovi):
        """Čita sljedeći token samo ako je odgovarajućeg tipa."""
        return self.zadnji if self.čitaj().je(*tipovi) else self.vrati()

    def __rshift__(self, tip):
        """Čita sljedeći token samo ako je odgovarajućeg tipa."""
        return self.zadnji if self.čitaj() ^ tip else self.vrati()

    def vidi(self, *tipovi): return self.pogledaj().je(*tipovi)

    def __ge__(self, tip): return self.pogledaj() ^ tip

    def greška(self): return self.zadnji.neočekivan()

    @classmethod
    def parsiraj(klasa, tokeni):
        parser = klasa(tokeni)
        try: rezultat = parser.start()
        except NoneInAST: raise parser.greška()  # BUG: nije dovoljno precizno!
        else:
            parser.pročitaj(E.KRAJ)
            return rezultat
        

elementarni = str, int, bool


class NoneInAST(Exception): pass

def AST_adapt(component):
    if isinstance(component, (Token, AST0, elementarni)): return component
    elif isinstance(component, (tuple, list)):
        if None in component: raise NoneInAST('Neobuhvaćen slučaj!')
        return ListaAST(component)
    elif isinstance(component, dict):
        if None in component or None in component.values():
            raise NoneInAST('Neobuhvaćen slučaj!')
        return RječnikAST(component.items())
    elif component is None: raise NoneInAST('Neobuhvaćen slučaj!')
    else: raise TypeError('Nepoznat tip komponente {}'.format(type(component)))


class AST0:
    """Bazna klasa za sva apstraktna sintaksna stabla."""
    def __xor__(self, tip):
        return isinstance(tip, type) and isinstance(self, tip)

    def je(self, *tipovi): return isinstance(self, tipovi)
    

class Atom(Token, AST0): """Atomarni token kao apstraktno stablo."""

class ListaAST(tuple):
    def __repr__(self): return repr(list(self))

class RječnikAST(tuple):
    def __repr__(self): return repr(dict(self))

class Nenavedeno(AST0):
    """Atribut koji nije naveden."""
    def __bool__(self): return False
    def __repr__(self): return type(self).__name__.join('<>')

nenavedeno = Nenavedeno()

def AST(atributi):
    AST2 = collections.namedtuple('AST2', atributi)
    # AST2.__new__.__defaults__ = tuple(nenavedeno for field in AST2._fields)
    
    class AST1(AST2, AST0):
        def __new__(cls, *args, **kw):
            new_args = [AST_adapt(arg) for arg in args]
            new_kw = {k: AST_adapt(v) for k, v in kw.items()}
            return super().__new__(cls, *new_args, **new_kw)
    return AST1
