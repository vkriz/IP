from pj import *

class JAVA(enum.Enum):
    CLASS, PUBLIC, STATIC, VOID, MAIN, STRING = 'class', 'public', 'static', 'void', 'main' , 'String'
    IF, ELSE, WHILE = 'if', 'else', 'while'
    NEW, THIS, SYSTEM, OUT, PRINTLN = 'new', 'this', 'System', 'out', 'println'
    EXTENDS = 'extends'
    RETURN = 'return'
    LENGTH = 'length'
    OOTV, OZATV, VOTV, VZATV, UOTV, UZATV = '(){}[]'
    TOCKA, TZAREZ, JEDNAKO, ZAREZ = '.',';', '=', ','
    AAND = '&&'
    OOR = '||'
    MANJE, PLUS, MINUS, PUTA, NEGACIJA, VECE, DIV= '<+-*!>/'
    MANJEJ = '<='
    VECEJ = '>='
    JEJE = '=='
    NIJE = '!='
    INT, BOOLEAN = 'int', 'boolean'
    class BROJ(Token):
        def vrijednost(self, tipovi, vrijednosti,klase, ime_k): 
            return int(self.sadržaj)
        def izvrši(self, tipovi, vrijednosti, klase, ime_k):
            self.vrijednost(tipovi, vrijednosti, klase, ime_k)
    class ID(Token):
        def vrijednost(self, tipovi, vrijednosti, klase,ime_k): 
            try: return vrijednosti[self]
            except KeyError: self.nedeklaracija()
        def izvrši(self, tipovi, vrijednosti):
            self.vrijednost(tipovi, vrijednosti, klase)
    class BOOL(Token):
        def vrijednost(self, tipovi, vrijednosti, klase, ime_k):
            return self.sadržaj == 'true'
        def izvrši(self, tipovi, vrijednosti):
            self.vrijednost(tipovi, vrijednosti)

def java_lex(source):
    lex = Tokenizer(source)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == '=':
            sljedeći = lex.čitaj()
            if sljedeći == '=': yield lex.token(JAVA.JEJE)
            else:
                lex.vrati()
                yield lex.token(JAVA.JEDNAKO)
        elif znak == '!':
            sljedeći = lex.čitaj()
            if sljedeći == '=': yield lex.token(JAVA.NIJE)
            else:
                lex.vrati()
                yield lex.token(JAVA.NEGACIJA)
        elif znak == '<':
            sljedeći = lex.čitaj()
            if sljedeći == '=': yield lex.token(JAVA.MANJEJ)
            else:
                lex.vrati()
                yield lex.token(JAVA.MANJE)
        elif znak == '>':
            sljedeći = lex.čitaj()
            if sljedeći == '=': yield lex.token(JAVA.VECEJ)
            else:
                lex.vrati()
                yield lex.token(JAVA.VECE)
        elif znak == '&':
            sljedeći = lex.čitaj()
            if sljedeći == '&': yield lex.token(JAVA.AAND)
            else: raise lex.greška('u ovom jeziku nema samostalnog &')
        elif znak == '|':
            sljedeći = lex.čitaj()
            if sljedeći == '|': yield lex.token(JAVA.OOR)
            else: raise lex.greška('u ovom jeziku nema samostalnog |')
        elif znak == '/':##prijedi preko kometara
            sljedeći = lex.čitaj()
            if sljedeći == '*':
                lex.pročitaj_do('*', True)
                if lex.čitaj()!='/': raise lex.greška('nije dobro zatvoren komentar')
            elif sljedeći == '/':
                lex.pročitaj_do('\n', True)
            else:
                lex.vrati()
                yield lex.token(JAVA.DIV)
        elif znak.isalpha():
            sljedeci = lex.čitaj()
            while(str.isalpha(sljedeci) or str.isdigit(sljedeci) or sljedeci=='_'):
                sljedeci = lex.čitaj()
            lex.vrati();
            if lex.sadržaj in {'true', 'false'}: yield lex.token(JAVA.BOOL)
            else: yield lex.literal(JAVA.ID)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            p = lex.sadržaj
            if p == '0' or p[0] != '0': yield lex.token(JAVA.BROJ)
            else: raise lex.greška('druge baze (osim 10) nisu podržane')
        else: yield lex.literal(JAVA)
