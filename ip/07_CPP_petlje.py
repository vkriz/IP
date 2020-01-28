"""Interpreter za jednostavni fragment jezika C++: petlje, grananja, ispis.

    petlje: for(var = broj; var < broj; var ++ ili var += broj) naredba
    grananja: if(var == broj) naredba
    ispis: cout << var1 << var2 << ..., s opcionalnim << endl na kraju

Naredba može biti i blok u vitičastim zagradama.
Podržana je i naredba break za izlaz iz unutarnje petlje.
"""


from pj import *


class CPP(enum.Enum):
    FOR, COUT, ENDL, IF = 'for', 'cout', 'endl', 'if'
    OOTV, OZATV, VOTV, VZATV = '(){}'
    MANJE, JEDNAKO, TOČKAZ = '<=;'
    PLUSP, PLUSJ, ISPIS, JJEDNAKO = '++', '+=', '<<', '=='
    class BREAK(Token):
        literal = 'break'
        def izvrši(self, mem): raise Prekid
    class BROJ(Token):
        def vrijednost(self, mem): return int(self.sadržaj)
    class IME(Token):
        def vrijednost(self, mem): return pogledaj(mem, self)


def cpp_lex(source):
    lex = Tokenizer(source)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == '+':
            sljedeći = lex.čitaj()
            if sljedeći == '+': yield lex.token(CPP.PLUSP)
            elif sljedeći == '=': yield lex.token(CPP.PLUSJ)
            else: raise lex.greška('u ovom jeziku nema samostalnog +')
        elif znak == '<':
            if lex.slijedi('<'): yield lex.token(CPP.ISPIS)
            else: yield lex.token(CPP.MANJE)
        elif znak == '=':
            if lex.slijedi('='): yield lex.token(CPP.JJEDNAKO)
            else: yield lex.token(CPP.JEDNAKO)
        elif znak.islower():
            lex.zvijezda(str.islower)
            yield lex.literal(CPP.IME)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            p = lex.sadržaj
            if p == '0' or p[0] != '0': yield lex.token(CPP.BROJ)
            else: raise lex.greška('druge baze (osim 10) nisu podržane')
        else: yield lex.literal(CPP)


# start -> naredba naredbe
# naredbe -> '' | naredba naredbe
# naredba -> petlja | ispis TOČKAZ | BREAK TOČKAZ | grananje
# for -> FOR OOTV IME JEDNAKO BROJ TOČKAZ IME MANJE BROJ
# 	  TOČKAZ IME inkrement OZATV
# petlja -> for naredba | for VOTV naredbe VZATV
# inkrement -> PLUSP | PLUSJ BROJ
# ispis -> COUT varijable | COUT varijable ISPIS ENDL
# varijable -> '' | ISPIS IME varijable
# grananje -> IF OOTV IME JJEDNAKO BROJ OZATV naredba

class CPPParser(Parser):
    def start(self):
        naredbe = []
        while not self >> E.KRAJ: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self >> CPP.FOR: return self.petlja()
        elif self >> CPP.COUT: return self.ispis()
        elif self >> CPP.IF: return self.grananje()
        elif self >> CPP.BREAK: return self.prekid()
        else: raise self.greška()

    def petlja(self):
        self.pročitaj(CPP.OOTV)
        i = self.pročitaj(CPP.IME)
        self.pročitaj(CPP.JEDNAKO)
        početak = self.pročitaj(CPP.BROJ)
        self.pročitaj(CPP.TOČKAZ)

        i2 = self.pročitaj(CPP.IME)
        if i != i2: raise SemantičkaGreška('nisu podržane različite varijable')
        self.pročitaj(CPP.MANJE)
        granica = self.pročitaj(CPP.BROJ)
        self.pročitaj(CPP.TOČKAZ)

        i3 = self.pročitaj(CPP.IME)
        if i != i3: raise SemantičkaGreška('nisu podržane različite varijable')
        if self >> CPP.PLUSP: inkrement = nenavedeno
        elif self >> CPP.PLUSJ: inkrement = self.pročitaj(CPP.BROJ)
        self.pročitaj(CPP.OZATV)

        if self >> CPP.VOTV:
            blok = []
            while not self >> CPP.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        return Petlja(i, početak, granica, inkrement, blok)
        
    def ispis(self):
        varijable = []
        novired = False
        while self >> CPP.ISPIS:
            if self >> CPP.IME: varijable.append(self.zadnji)
            elif self >> CPP.ENDL: novired = True; break
        self.pročitaj(CPP.TOČKAZ)
        return Ispis(varijable, novired)

    def grananje(self):
        self.pročitaj(CPP.OOTV)
        lijevo = self.pročitaj(CPP.IME)
        self.pročitaj(CPP.JJEDNAKO)
        desno = self.pročitaj(CPP.BROJ)
        self.pročitaj(CPP.OZATV)
        naredba = self.naredba()
        return Grananje(lijevo, desno, naredba)

    def prekid(self):
        br = self.zadnji
        self.pročitaj(CPP.TOČKAZ)
        return br


class Prekid(Exception): pass


class Program(AST('naredbe')):
    def izvrši(self):
        memorija = {}
        for naredba in self.naredbe: naredba.izvrši(memorija)
    
class Petlja(AST('varijabla početak granica inkrement blok')):
    def izvrši(self, mem):
        kv = self.varijabla.sadržaj
        mem[kv] = self.početak.vrijednost(mem)
        while mem[kv] < self.granica.vrijednost(mem):
            try:
                for naredba in self.blok: naredba.izvrši(mem)
            except Prekid:
                break
            inkr = self.inkrement
            if inkr is nenavedeno: inkr = 1
            else: inkr = inkr.vrijednost(mem)
            mem[kv] += inkr 

class Ispis(AST('varijable novired')):
    def izvrši(self, mem):
        for var in self.varijable: print(var.vrijednost(mem), end=' ')
        if self.novired: print()

class Grananje(AST('lijevo desno naredba')):
    def izvrši(self, mem):
        if self.lijevo.vrijednost(mem) == self.desno.vrijednost(mem):
            self.naredba.izvrši(mem)


if __name__ == '__main__':

    lex = list(cpp_lex('''
        for ( i = 8 ; i < 13 ; i += 2 )
            for(j=0; j<3; j++) {
                cout<<i<<j<<endl;
                if(i == 9) if (j == 1) break;
            }
        '''))

    print(*lex)
    cpp = CPPParser.parsiraj(cpp_lex('''
        for ( i = 8 ; i < 13 ; i += 2 )
            for(j=0; j<3; j++) {
                cout<<i<<j<<endl;
                if(i == 9) if (j == 1) break;
            }
    '''))
    print(cpp)
    cpp.izvrši()


# DZ: omogućiti i grananjima da imaju blokove - uvesti novi AST Blok
#     omogućiti da parametri petlje budu varijable, ne samo brojevi
