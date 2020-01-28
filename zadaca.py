from pj import *
from collections import ChainMap

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
    MANJE, PLUS, MINUS, PUTA, NEGACIJA= '<+-*!'
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
    class ARRAY(Token):
        def vrijednost(self, tipovi, vrijednosti, klase):
            return
        def izvrši(self, tipovi, vrijednosti, klase):
            return self.tip(tipovi, vrijednosti)

def java_lex(source):
    lex = Tokenizer(source)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == '&':
            sljedeći = lex.čitaj()
            if sljedeći == '&': yield lex.token(JAVA.AAND)
            else: raise lex.greška('u ovom jeziku nema samostalnog &')
        elif znak == '/':##prijedi preko kometara
            sljedeći = lex.čitaj()
            if sljedeći == '*':
                lex.pročitaj_do('*', True)
                if lex.čitaj()!='/': raise lex.greška('nije dobro zatvoren komentar')
            elif sljedeći == '/':
                lex.pročitaj_do('\n', True)
            else: raise lex.greška('nije dobar komentar')
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


##BKG
        
## Program -> MainClass ClassDecl
## MainClass -> CLASS ID VOTV PUBLIC STATIC VOID MAIN OOTV STRING UOTV UZTV ID OZTV VOTV Statements VZTV VZTV
## ClassDecl -> CLASS ID VOTV VarDecl MethodDecl VZTV
##              | CLASS ID EXTENDS ID VOTV VarDecl MethodDecl VZTV
##              | ClassDecl | ''
## VarDecl -> Type ID TZAREZ VarDecl | ''
## MethodDecl -> PUBLIC Type ID OOTV FormalList OZTV VOTV VarDecl Statements RETURN Exp TZAREZ VZTV MethodDecl | ''
## FormalList -> Type ID FormalRest | ''
## FormalRest -> , Type ID FormalRest | ''
## Type -> INT UOTV UZTV | BOOLEAN | INT | ID
## Statements -> '' | Statement Statements
## Statement -> VOTV Statements VZTV
##              | IF OOTV Exp OZTV Statement ELSE Statement
##              | WHILE OOTV Exp OZTV Statement
##              | SYSTEM TOCKA OUT TOCKA PRINTLN OOTV Exp OZTV TZAREZ
##              | ID JEDNAKO Exp TZAREZ
##              | ID UOTV Exp UZTV JEDNAKO Exp TZAREZ
## Exp -> Exp op Exp
##        | Exp UOTV Exp UZTV
##        | Exp TOCKA LENGTH
##        | Exp TOCKA ID OOTV ExpList OZTV
##        | BROJ
##        | TRUE
##        | FALSE
##        | ID
##        | THIS
##        | NEW INT UOTV Exp UZTV
##        | NEW ID OOTV OZTV
##        | NEGACIJA Exp
##        | OOTV Exp OZTV
## ExpList -> Exp ExpRest | ''
## ExpRest -> , Exp ExpRest | ''
## op -> AAND | MANJE | PLUS | MINUS | PUTA


class JavaParser(Parser):
    def start(self):
        klase = {}
        main = self.MainClass()
        ime_main= main.ime
        if self >> JAVA.VZATV: pass
        while not self >> E.KRAJ:
            klasa = self.ClassDecl()
            imek = klasa.ime
            if imek in klase: raise SemantičkaGreška(       #ovdje još provjeri da li se zove kao i main class
                'Dvaput definirana klasa ' + imek.sadržaj)
            klase[imek] = klasa
        return Program(main, klase)

    def MainClass(self):
        self.pročitaj(JAVA.CLASS)
        ime = self.pročitaj(JAVA.ID)
        self.pročitaj(JAVA.VOTV)
        self.pročitaj(JAVA.PUBLIC)
        self.pročitaj(JAVA.STATIC)
        self.pročitaj(JAVA.VOID)
        self.pročitaj(JAVA.MAIN)
        self.pročitaj(JAVA.OOTV)
        self.pročitaj(JAVA.STRING)
        self.pročitaj(JAVA.UOTV)
        self.pročitaj(JAVA.UZATV)
        param = self.pročitaj(JAVA.ID)
        self.pročitaj(JAVA.OZATV)
        self.pročitaj(JAVA.VOTV)

        statement = self.Statement()

        self.pročitaj(JAVA.VZATV)
        self.pročitaj(JAVA.VZATV)
        return Main(ime, param, statement)

    ## ClassDecl -> CLASS ID VOTV VarDecl MethodDecl VZTV
    ##              | CLASS ID EXTENDS ID VOTV VarDecl MethodDecl VZATV
    def ClassDecl(self):
        if self >> JAVA.CLASS:
            ime = self.pročitaj(JAVA.ID)
            ime_roditelja = ""
            if self >> JAVA.EXTENDS:
                ime_roditelja = self.pročitaj(JAVA.ID)
                
            self.pročitaj(JAVA.VOTV)
            ## VarDecl -> Type ID TZAREZ | VarDecl | ''
            varijable = {}
            while not self >> {JAVA.PUBLIC, JAVA.VZATV}:
                varijabla = self.VarDecl()
                imev = varijabla.ime
                if imev in varijable: raise SemantičkaGreška(
                    'Dvaput deklarirana varijabla ' + imev.sadržaj)
                varijable[imev] = varijabla
            self.vrati()
            ## MethodDecl -> PUBLIC Type ID OOTV FormalList OZTV VOTV VarDecl Statements RETURN Exp TZAREZ VZTV
            ##               MethodDecl | ''
            metode = {}
            while not self >> JAVA.VZATV:
                metoda = self.MethodDecl()
                imem = metoda.ime
                if imem in metode: raise SemantičkaGreška(
                    'Dvaput definirana metoda ' + imem.sadržaj)
                metode[imem] = metoda
            return Klasa(ime_roditelja, ime, varijable, metode)

## VarDecl -> Type ID TZAREZ VarDecl | ''
    def VarDecl(self):
         tip = self.Type()
         ime = self.pročitaj(JAVA.ID)
         self.pročitaj(JAVA.TZAREZ)
         return Varijabla(tip, ime)

## MethodDecl -> PUBLIC Type ID OOTV FormalList OZTV VOTV VarDecl Statements RETURN Exp TZAREZ VZTV
##              MethodDecl | ''
    def MethodDecl(self):
        self.pročitaj(JAVA.PUBLIC)
        tip = self.Type()
        ime = self.pročitaj(JAVA.ID)
        self.pročitaj(JAVA.OOTV)
        argumenti = self.FormalList()
        self.pročitaj(JAVA.OZATV)
        self.pročitaj(JAVA.VOTV)


        self.varijable = {}
        while not self >> {JAVA.VOTV, JAVA.IF, JAVA.WHILE, JAVA.SYSTEM, JAVA.ID, JAVA.RETURN}:
            varijabla = self.VarDecl()
            imev = varijabla.ime
            if imev in self.varijable: raise SemantičkaGreška(
                'Dvaput deklarirana varijabla ' + imev.sadržaj)
            self.varijable[imev] = varijabla

        self.vrati();
        statements = []
        while not self >> JAVA.RETURN:
            statements.append(self.Statement())
        
        povratna = self.Izraz1()
        self.pročitaj(JAVA.TZAREZ)
        self.pročitaj(JAVA.VZATV)

        return Metoda(tip, ime, argumenti, self.varijable, statements, povratna)

    def Type(self):
        #INT UOTV UZTV | BOOLEAN | INT | ID        
        if self >> JAVA.INT:
             return self.zadnji
             if self >> JAVA.UOTV:
                 self.pročitaj(JAVA.UZATV)
                 return "int []";
             else:
                 return self.zadnji ##iz nekog razloga tu procita id
        elif self >> JAVA.BOOLEAN: return JAVA.BOOLEAN
        else: return self.pročitaj(JAVA.ID)
   
    def FormalList(self):
        #Type ID FormalRest
        rests = []  
        if self >> JAVA.OZATV:
            self.vrati()
            return ListaArgumenata("", "", rests)
        varijable = []
        varijabla = Varijabla(self.Type(), self.pročitaj(JAVA.ID))
        varijable.append(varijabla)
        while not self >> JAVA.OZATV:
            varijable.append(self.FormalRest())
        self.vrati()
        return varijable

    def FormalRest(self):
        # , Type ID | FormalRest | ''
        if self >> JAVA.ZAREZ:
            tip = self.Type()
            ime = self.pročitaj(JAVA.ID)
            return Varijabla(tip, ime)

    def Statement(self):
        if self >> JAVA.VOTV:
            statements = []
            while not self >> JAVA.VZATV:
                statements.append(self.Statement())
            return Statements(statements)
        elif self >> JAVA.IF: return self.grananje()
        elif self >> JAVA.WHILE: return self.petlja()
        elif self >> JAVA.SYSTEM: return self.ispis()
        elif self >> JAVA.ID:
            return self.pridruzivanje() ## ne moze dva puta self.vrati()
            #if self >> JAVA.JEDNAKO: return self.pridruzivanje()
            #elif self >> JAVA.UOTV: return self.pridruzivanje_niz()
            #else: self.greška()
        else: self.greška()

    def grananje(self):
        #IF OOTV Exp OZTV Statement ELSE Statement
        self.pročitaj(JAVA.OOTV)
        exp = self.Izraz1()
        self.pročitaj(JAVA.OZATV)
        stat1 = self.Statement()
        self.pročitaj(JAVA.ELSE)
        stat2 = self.Statement()
        return Grananje(exp, stat1, stat2)

    def petlja(self):
        #WHILE OOTV Exp OZTV Statement
        #self.pročitaj(JAVA.WHILE)
        self.pročitaj(JAVA.OOTV)
        exp = self.Izraz1()
        self.pročitaj(JAVA.OZATV)
        stat = self.Statement()
        return Petlja(exp, stat)
        
    def ispis(self):
        #SYSTEM TOCKA OUT TOCKA PRINTLN OOTV Exp OZTV TZAREZ
        self.pročitaj(JAVA.TOCKA)
        self.pročitaj(JAVA.OUT)
        self.pročitaj(JAVA.TOCKA)
        self.pročitaj(JAVA.PRINTLN)
        self.pročitaj(JAVA.OOTV)

        exp = self.Izraz1()

        self.pročitaj(JAVA.OZATV)
        self.pročitaj(JAVA.TZAREZ)
        return Ispis(exp)

    def pridruzivanje(self):
        #ID JEDNAKO Exp TZAREZ
        #self.vrati()
        self.vrati()
        ime = self.pročitaj(JAVA.ID)
        self.pročitaj(JAVA.JEDNAKO)
        exp = self.Izraz1()
        self.pročitaj(JAVA.TZAREZ)
        return Pridruzivanje(ime, exp)

    def pridruzivanje_niz(self):
        #ID UOTV Exp UZTV JEDNAKO Exp TZAREZ
        self.vrati()
        self.vrati()
        ime = self.pročitaj(JAVA.ID)
        self.pročitaj(JAVA.UOTV)
        exp1 = self.Izraz1()
        self.pročitaj(JAVA.UZATV)
        self.pročitaj(JAVA.JEDNAKO)
        exp2 = self.Izraz1()
        self.pročitaj(JAVA.TZAREZ)
        return Pridruzivanje_niz(ime, exp1, exp2)
            
## Exp -> Exp op Exp
##        | Exp UOTV Exp UZTV --> ovo nismo
##        | Exp TOCKA LENGTH
##        | Exp TOCKA ID OOTV ExpList OZTV
##        | BROJ
##        | TRUE
##        | FALSE
##        | ID
##        | THIS
##        | NEW INT UOTV Exp UZTV --> ovo nismo
##        | NEW ID OOTV OZTV
##        | NEGACIJA Exp
##        | OOTV Exp OZTV

# Izraz1 -> Izraz1 (&&, <) Izraz2 | Izraz2 
# Izraz2 -> Izraz2 (+, -) Izraz3 | Izraz3
# Izraz3 -> Izraz3 * Izraz4 | Izraz4
# Izraz4 -> ! Izraz5 | Izraz5
# Izraz5 -> Izraz5 . Izraz7 | Izraz6 | Izraz5 UOTV Izraz1 UZATV
# Izraz6 -> BROJ | TRUE | FALSE | ID | THIS | (Izraz1) | NEW ID OOTV OZATV | NEW INT UOTV Izraz1 UZTV | OOTV Izraz1 OZTV
# Izraz7 -> LENGTH | ID OOTV ExpList OZATV

    def Izraz1(self): # Izraz1 -> Izraz1 (&&, <) Izraz2 | Izraz2 
        #print("Izraz1")
        trenutni = self.Izraz2()
        while True:
            if self >> { JAVA.AAND, JAVA.MANJE }:
                operacija = self.zadnji
                trenutni = LogičkaOperacija(trenutni, self.Izraz2(), operacija)
            else: return trenutni

    def Izraz2(self): # Izraz2 -> Izraz2 (+, -) Izraz3 | Izraz3
        #print("Izraz2")
        trenutni = self.Izraz3()
        while True:
            if self >> { JAVA.PLUS, JAVA.MINUS }:
                operacija = self.zadnji
                trenutni = AritmetičkaOperacija(trenutni, self.Izraz3(), operacija)
            else: return trenutni

    def Izraz3(self): # Izraz3 -> Izraz3 * Izraz4 | Izraz4
        #print("Izraz3")
        trenutni = self.Izraz4()
        while True:
            if self >> JAVA.PUTA:
                operacija = self.zadnji
                trenutni = AritmetičkaOperacija(trenutni, self.Izraz4(), operacija)
            else: return trenutni

    def Izraz4(self): # Izraz4 -> ! Izraz5 | Izraz5
        #print("Izraz4")
        if self >> JAVA.NEGACIJA:
            iza = self.Izraz5()
            return Negacija(iza)
        baza = self.Izraz5()
        return baza

    def Izraz5(self): # Izraz5 -> Izraz5 . Izraz7 | Izraz6 | Izraz5 UOTV Izraz1 UZATV
        #print("Izraz5")
        trenutni = self.Izraz6()
        while True:
            if self >> JAVA.TOCKA:
                trenutni = Tocka(trenutni, self.Izraz7())
            elif self >> JAVA.UOTV:
                trenutni = Uglate(trenutni, self.Izraz1())
                self.pročitaj(JAVA.UZATV)
            else: return trenutni
        
    def Izraz6(self): # Izraz6 -> BROJ | TRUE | FALSE | ID | THIS | (Izraz1) | NEW ID OOTV OZATV | NEW INT UOTV Izraz1 UZTV | OOTV Izraz1 OZTV
        #print("Izraz6")
        if self >> JAVA.OOTV:
            u_zagradi = self.Izraz1()
            self.pročitaj(JAVA.OZATV)
            return u_zagradi
        if self >> JAVA.NEW:
            ime = self.pročitaj(JAVA.ID)
            self.pročitaj(JAVA.OOTV)
            self.pročitaj(JAVA.OZATV)
            return Napravi_novi(ime)
        if self >> { JAVA.BROJ, JAVA.BOOL, JAVA.ID, JAVA.THIS }:
            return self.zadnji
        else:
            return ""

    def Izraz7(self): # Izraz7 -> LENGTH | ID OOTV ExpList OZATV
        #print("Izraz7")
        if self >> JAVA.ID:
            ime = self.zadnji
            self.pročitaj(JAVA.OOTV)
            varijable = self.ExpList()
            self.pročitaj(JAVA.OZATV)
            return IzvrijedniFunkciju(ime, varijable)
        if self >> JAVA.LENGTH:
            return self.zadnji
        
## ExpList -> Exp ExpRest | ''  
    def ExpList(self):
        expReturn = []
        expReturn.append(self.Izraz1())
        while not self >> JAVA.OZATV:
            expReturn.append(self.ExpRest())
        self.vrati()
        return expReturn

## ExpRest -> , Exp ExpRest | ''   
    def ExpRest(self):
        if self >> JAVA.ZAREZ:
            exp = self.Izraz1()
            return exp


class Ispis(AST('exp')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        print(self.exp.vrijednost(tipovi, vrijednosti, klase, ime_k))


# IF OOTV Exp OZTV Statement ELSE Statement
class Grananje(AST('exp stat1 stat2')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        if (self.exp.vrijednost(tipovi, vrijednosti, klase, ime_k)): #ako je vrijednost ovog true, izvršava se tijelo if-a
            self.stat1.izvrši(tipovi, vrijednosti, klase, ime_k)

        else:
            self.stat2.izvrši(tipovi, vrijednosti, klase, ime_k)


class Petlja(AST('exp stat')):
    def izvrši(self, tipovi, vrijednosti, klase):
        while (self.exp.vrijednost(tipovi, vrijednosti, klase)):
            try:
                self.stat.izvrši(tipovi, vrijednosti, klase)
            except BreakException: break
            except ContinueException: continue

class Pridruzivanje(AST('ime exp')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        lijevi = self.ime.vrijednost(tipovi, vrijednosti, klase, ime_k)
        desni = self.exp.vrijednost(tipovi, vrijednosti, klase, ime_k)
        if (isinstance(lijevi, int)):
            if (not isinstance(desni, int)):
                raise SemantičkaGreška("Nekompatibilni tipovi")
            else:
                lijevi = desni
                vrijednosti[self.ime] = lijevi

class Pridruzivanje_niz(AST('ime exp')):
    def izvrši(self, mem):
        return

class Tocka(AST('izraz1 izraz2')):
    def vrijednost(self, tipovi, vrijednosti, klase, ime_k):
        print(self.izraz1)
        if self.izraz1 ^ JAVA.THIS:
            print(ime_k)
            ime_klase = ime_k;
            klase_d = dict(klase)
            klasa = klase_d[ime_klase]
            return self.izraz2.izvrši(ime_klase, tipovi, vrijednosti, klase, ime_k)
        else:
            ime_klase = self.izraz1.izvrši(tipovi, vrijednosti, klase, ime_k)
            klase_d = dict(klase)
            klasa = klase_d[ime_klase]
            return self.izraz2.izvrši(ime_klase, klasa.tipovi, klasa.vrijednosti, klase, ime_klase)
    
class IzvrijedniFunkciju(AST('ime varijable')):
    def izvrši(self, ime_klase, tipovi, vrijednosti, klase, ime_k):
        evaluiraniArgumenti = []
        klase_d = dict(klase)
        klasa = klase_d[ime_klase]
        for var in self.varijable:
            print("varijable")
            print(var)
            evaluiraniArgumenti.append(var.vrijednost(tipovi, vrijednosti, klase, ime_k))
        metode_d = dict(klase_d[ime_klase].metode)

        return metode_d[self.ime].izvrši(klasa.tipovi, klasa.vrijednosti, klase, evaluiraniArgumenti, ime_k)

class ListaArgumenata(AST('tip ime rests')):
    def izvrši(self, tipovi, vrijednosti, klase):
        return

class Varijabla(AST('tip ime')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        #ako već postoji ova varijabla, digni grešku
        if (self.ime in tipovi):
            self.ime.redeklaracija()

        tipovi[self.ime] = self.tip
        #svakoj se varijabli daje defaultna vrijednost
        if self.tip ^ JAVA.INT:
            vrijednosti[self.ime] = 0
        elif self.tip ^ JAVA.BOOLEAN:
            vrijednosti[self.ime] = False
        return self
    def vrijednost(self, tipovi, vrijednosti, klase, ime_k): 
        return vrijednosti[self.ime]
    def pridruzi(self, tipovi, vrijednosti, klase, vrijed):
        vrijednosti[self.ime] = vrijed
        return vrijed
    
class LogičkaOperacija(AST('prvi drugi operacija')):
    def vrijednost(self, tipovi, vrijednosti, klase, ime_k):
        # prvo evaluiraj lijevu stranu, ovisno o njenoj vrijednosti evaluiraj desnu
        if(isinstance(self.prvi.vrijednost(tipovi, vrijednosti, klase, ime_k), list)):
            lijevi = self.prvi.vrijednost(tipovi, vrijednosti, klase, ime_k)[0]
        else: lijevi = self.prvi.vrijednost(tipovi, vrijednosti, klase, ime_k)
        #if(not isinstance(lijevi, JAVA.BOOL)):
         #   raise SemantičkaGreška("neispravna logička operacija")

        if self.operacija ^ JAVA.AAND:
            if (lijevi is False): return False

        if(isinstance(self.drugi.vrijednost(tipovi, vrijednosti,klase, ime_k), list)):
            desni = self.drugi.vrijednost(tipovi, vrijednosti, klase,ime_k)[0]
        else: desni = self.drugi.vrijednost(tipovi, vrijednosti, klase, ime_k)
       # if(not isinstance(desni, bool)):
        #    raise SemantičkaGreška("neispravna logička operacija")
        
        if self.operacija ^ JAVA.AAND:
            return  bool(lijevi and desni)
    
        if self.operacija ^ JAVA.MANJE: return lijevi < desni
        

    def izvrši(izraz, imena, vrijednosti):
        izraz.vrijednost(imena, vrijednosti)          
        return rezultat  
    def izvrši(izraz, imena, vrijednosti, klase, ime_k):
        izraz.vrijednost(imena, vrijednosti, klase, ime_k)  

class AritmetičkaOperacija(AST('prvi drugi operacija')):
    def vrijednost(self, tipovi, vrijednosti, klase, ime_k):
        try:
            print("prvi")
            print(self.prvi)
            print(self.prvi.vrijednost(tipovi, vrijednosti, klase, ime_k))
            lijevi = self.prvi.vrijednost(tipovi, vrijednosti, klase, ime_k)
            if(isinstance(lijevi, list)):
                lijevi = lijevi[0]
            desni = self.drugi.vrijednost(tipovi, vrijednosti, klase, ime_k)
            if(isinstance(desni, list)):
                desni = desni[0]

        except ValueError:
            raise SemantičkaGreška("neispravna binarna operacija")

        if self.operacija ^ JAVA.PLUS:
            rezultat = lijevi + desni
        elif self.operacija ^ JAVA.MINUS:
            print("lijevi")
            print(lijevi)
            print("desni")
            print(desni)
            rezultat = lijevi - desni
        elif self.operacija ^ JAVA.PUTA:
            rezultat = lijevi * desni               

        return rezultat

    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        self.vrijednost(tipovi, vrijednosti, klase, ime_k)

class Negacija(AST('iza')):
    def vrijednost(self, tipovi, vrijednosti, klase):
        value = self.iza.vrijednost(tipovi, vrijednosti)[0]
        if (not isinstance(value, bool)):
            raise SemantičkaGreška("unarna negacija se izvršava samo na boolu")
        return [not value]
    def izvrši(self, tipovi, vrijednosti, klase):
        self.vrijednost(tipovi, vrijednosti, klase)

class Metoda(AST('tip ime argumenti varijable statements povratna')): #self.varijable = {}, statements =[], argumenti = []
    def napuni(self, tipovi, vrijednosti, klase, ime_k):
        self.tipovi = tipovi.new_child()
        self.vrijednosti = vrijednosti.new_child()
        varijable = dict(self.varijable)
        self.ime_k = ime_k
        for var in varijable:
            print(var)
            varijable[var].izvrši(self.tipovi, self.vrijednosti, klase, ime_k)

        #for var in self.varijable:
        #    var.izvrši(self.tipovi, self.vrijednosti, klase)
    def izvrši(self, tipovi, vrijednosti, klase, evaluiraniArgumenti, ime_k):
        br = 0
        for arg in self.argumenti: #arg nam je sad tipa Varijabla
            self.vrijednosti[arg.ime] = evaluiraniArgumenti[br]
            br=br+1
        print("EVALUIRANI")
        print(evaluiraniArgumenti)
        for stat in self.statements:
            stat.izvrši(self.tipovi, self.vrijednosti, klase, ime_k)
        return self.povratna.vrijednost(self.tipovi, self.vrijednosti, klase, ime_k)

class Napravi_novi(AST('ime')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        return self.ime

class Statements(AST('statements')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        for stat in self.statements:
            stat.izvrši(tipovi, vrijednosti, klase, ime_k)    


## Program -> MainClass ClassDecl
## MainClass -> CLASS ID VOTV PUBLIC STATIC VOID MAIN OOTV STRING UOTV UZTV ID OZTV VOTV Statements VZTV VZTV
## ClassDecl -> CLASS ID VOTV VarDecl MethodDecl VZTV
##              | CLASS ID EXTENDS ID VOTV VarDecl MethodDecl VZTV
##              | ClassDecl | ''

class Main(AST('ime param statement')):
    def izvrši(self, tipovi, vrijednosti, klase):
        return
    
class Klasa(AST('ime_roditelja ime varijable metode')):
    def napuni(self, tipovi, vrijednosti, klase):
        if self.ime_roditelja != '':
            self.tipovi = klase[self.ime_roditelja].tipovi.new_child()
            self.vrijednosti = klase[self.ime_roditelja].vrijednosti.new_child()
        else:
            self.tipovi = ChainMap()
            self.vrijednosti = ChainMap()
        for var in self.varijable:
            var.izvrši(self.tipovi, self.vrijednosti, klase)
        metode = dict(self.metode)
        for ime_met in metode:
            metode[ime_met].napuni(self.tipovi, self.vrijednosti, klase, self.ime)
    
    
class Program(AST('main klase')):
    def izvrši(self):
        tipovi = ChainMap()
        vrijednosti = ChainMap()
        klase = dict(self.klase)
        for ime_klase in klase.keys():
            klase[ime_klase].napuni(tipovi, vrijednosti, self.klase)

        self.main.statement.izvrši(tipovi, vrijednosti, self.klase, "")


#------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    ##primjer1
    ulaz = '''
        class Factorial {
            public static void main(String[] a) {
                 System.out.println(new Fac().ComputeFac(10));
             }
        }
        '''
    #print(ulaz)

    #tokeni1 = list(java_lex(ulaz))
    #print(*tokeni1)
    #CLASS'class' ID'Factorial' VOTV'{' PUBLIC'public' STATIC'static'
    #VOID'void' MAIN'main' OOTV'(' STRING'String' UOTV'[' UZATV']' ID'a'
    #OZATV')' VOTV'{' SYSTEM'System' TOCKA'.' OUT'out' TOCKA'.' PRINTLN'println'
    #OOTV'(' NEW'new' ID'Fac' OOTV'(' OZATV')' TOCKA'.' ID'ComputeFac' OOTV'('
    #BROJ'10' OZATV')' OZATV')' TZAREZ';' VZATV'}' VZATV'}'

    ##primjer2 - kometari /* */
    ulaz = '''
        /*Komentar*/
        class Factorial {
            public static void main(String[] a) {
                 System.out.println(new Fac().ComputeFac(10));
             }
        }
        /*   Komentar */
        '''
    ##print(ulaz)

    #tokeni2 = list(java_lex(ulaz))
    ##print(*tokeni2)

    ##moraju bit isti
    #print(tokeni1==tokeni2)

    ##primjer3 - svi komentari
    ulaz = '''
        /*Komentar sdsa dsas 5465 .-,.,sdd 8797daskklè @dklas */
        class Factorial {
            public static void main(String[] a) {
                //printa broj v=5
                 System.out.println(new Fac().ComputeFac(10));
             }
             //v=5
        }
        /*   Komentar */
        '''
    ##print(ulaz)

    ##tokeni3 = list(java_lex(ulaz))
    ##print(*tokeni3)

    ##print(tokeni1==tokeni3)

    ##primjer4 
    ulaz = '''
       class Fac {
         public int ComputeFac(int num) {
             int num_aux;
             if (num < 1)
                 num_aux = 1;
             else
                 num_aux = num * (this.ComputeFac(num-1));
         return num_aux;
         }
        }
        '''
    #print(ulaz)

    #tokeni4 = list(java_lex(ulaz))
    ##print(*tokeni4)

    ##primjer5
    ulaz = '''
    /* lkjklasjdlkas kdasjdlka
    laskdèlsak */
       class Fac {
         public int ComputeFac(int num) {
             int num_aux; //nesto
             if (num < 1)
                 num_aux = 1;
             else
                 num_aux = num * (this.ComputeFac(num-1));
         return num_aux;
         }
        }
        '''
    ##print(ulaz)

    ##tokeni5 = list(java_lex(ulaz))
    ##print(*tokeni5)

    ##print(tokeni4==tokeni5)

    ##primjer1
    ulaz = '''
        class Factorial {
            public static void main(String[] a) {
                 System.out.println(new Fac().ComputeFac(10));
             }
        }
        class Fac {
         public int ComputeFac(int num) {
             int num_aux; //nesto
             if (num < 1)
                 num_aux = 1;
             else
                 num_aux = num * (this.ComputeFac(num-1));
         return num_aux;
         }
        }
        '''
    print(ulaz)
    print("lekser")
    tokeni6 = list(java_lex(ulaz))
    print(*tokeni6)

    print("parser")
    java = JavaParser.parsiraj(java_lex(ulaz))
    print(java)
    
    ulaz = '''
        class Factorial {
            public static void main(String[] a) {
            {
                if(true){
                    System.out.println(10);
                    System.out.println(10);
                }
                 else
                     System.out.println(5);
                }
             }
        }
        }
        '''
    print(ulaz)
    print("lekser")
    tokeni6 = list(java_lex(ulaz))
    print(*tokeni6)

    print("parser")
    java = JavaParser.parsiraj(java_lex(ulaz))
    print(java)
    java.izvrši()



    ulaz = '''
        class Factorial {
            public static void main(String[] a) {
                if(true)
                    System.out.println(new Fac().ispis(2+3*2));
                
                 else
                     System.out.println(5);
            }
        }
        class Fac {
            public int ispis(int a){
                return a;
            }
        }
        '''
    print(ulaz)
    print("lekser")
    tokeni6 = list(java_lex(ulaz))
    print(*tokeni6)

    print("parser")
    java = JavaParser.parsiraj(java_lex(ulaz))
    print(java)
    java.izvrši()

    ulaz = '''
        class Factorial {
            public static void main(String[] a) {
                if(true)
                    System.out.println(new Fac().ispis(2+3*2));
                
                 else
                     System.out.println(5);
            }
        }
        class Fac {
            public int ispis(int a){
                int b;
                
                if(a<10)
                    b = 1;
                else
                    b = 2;
                    
                return a+b;
            }
        }
        '''
    print(ulaz)
    print("lekser")
    tokeni6 = list(java_lex(ulaz))
    print(*tokeni6)

    print("parser")
    java = JavaParser.parsiraj(java_lex(ulaz))
    print(java)
    java.izvrši()

    ulaz = '''
        class Factorial {
            public static void main(String[] a) {
                 System.out.println(new Fac().ComputeFac(10));
             }
        }
        class Fac {
         public int ComputeFac(int num) {
             int num_aux; //nesto
             if (num < 1)
                 num_aux = 1;
             else
                 num_aux = num * 5;
         return num_aux;
         }
        }
        '''
    print(ulaz)
    print("lekser")
    tokeni6 = list(java_lex(ulaz))
    print(*tokeni6)

    print("parser")
    java = JavaParser.parsiraj(java_lex(ulaz))
    print(java)
    java.izvrši()

    ulaz = '''
        class Factorial {
            public static void main(String[] a) {
                 System.out.println(new Fac().ComputeFac(4));
             }
        }
        class Fac {
         public int ComputeFac(int num) {
             int num_aux; //nesto
             if (num < 1)
                 num_aux = 1;
             else
                 num_aux = num * (this.ComputeFac(num-1));
         return num_aux;
         }
        }
        '''
    print(ulaz)
    print("lekser")
    tokeni6 = list(java_lex(ulaz))
    print(*tokeni6)

    print("parser")
    java = JavaParser.parsiraj(java_lex(ulaz))
    print(java)
    java.izvrši()
