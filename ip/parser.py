from pj import *
from lexer import *

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
        klasa = self.MainClass()
        imek = klasa.ime
        klase[imek] = klasa
        print(imek)
        while not self >> E.KRAJ:
            klasa = self.ClassDecl()
            imek = klasa.ime
            if imek in klase: raise SemantičkaGreška(
                'Dvaput definirana klasa ' + imek.sadržaj)
            klase[imek] = klasa
        return klase

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
        print("prije")
        statement = self.Statement()
        print("poslije")
        self.pročitaj(JAVA.VZATV)
        return Main(param, statement)

    ## ClassDecl -> CLASS ID VOTV VarDecl MethodDecl VZTV
    ##              | CLASS ID EXTENDS ID VOTV VarDecl MethodDecl VZATV
    def ClassDecl(self):
        if self >> JAVA.CLASS:
            ime = self.pročitaj(JAVA.ID)
            ime_roditelja = None
            if self >> JAVA.EXTENDS:
                ime_roditelja = self.pročitaj(JAVA.ID)
                
            self.pročitaj(JAVA.VOTV)

            ## VarDecl -> Type ID TZAREZ | VarDecl | ''
            varijable = {}
            while not self >> {JAVA.PUBLIC, JAVA.VZATV}:
                varijabla = self.VarDecl()
                imev = varijabla.ime
                if imev in self.varijable: raise SemantičkaGreška(
                    'Dvaput deklarirana varijabla ' + imev.sadržaj)
                self.varijable[imev] = varijabla

            self.vrati()
            ## MethodDecl -> PUBLIC Type ID OOTV FormalList OZTV VOTV VarDecl Statements RETURN Exp TZAREZ VZTV
            ##               MethodDecl | ''
            metode = {}
            while not self >> JAVA.VZATV:
                metoda = self.MethodDecl()
                imem = metoda.ime
                if imem in self.metode: raise SemantičkaGreška(
                    'Dvaput definirana metoda ' + imem.sadržaj)
                self.metode[imem] = metoda
            return Klasa(ime_roditelja, ime, varijable, metode)

## VarDecl -> Type ID TZAREZ VarDecl | ''
    def VarDecl(self):
         tip = self.Type()
         ime = self.pročitaj(JAVA.ID)
         self.pročitaj(JAVA.TAZREZ)
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


        varijable = {}
        while not self >> {JAVA.VOTV, JAVA.IF, JAVA.WHILE, JAVA.SYSTEM, JAVA.ID, JAVA.RETURN}:
            varijabla = self.VarDecl()
            imev = varijabla.ime
            if imev in self.varijable: raise SemantičkaGreška(
                'Dvaput deklarirana varijabla ' + imev.sadržaj)
            self.varijable[imev] = varijabla

        self.vrati();
        statements = []
        while not self >> JAVA.RETURN:
            statements = append(self.Statement())
            
        povratna = self.Izraz1()
        self.pročitaj(JAVA.TZAREZ)
        self.pročitaj(JAVA.VZATV)

        return Metoda(tip, ime, argumenti, varijable, statements, povratna)

    def Type(self):
        #INT UOTV UZTV | BOOLEAN | INT | ID
        if self >> JAVA.INT:
             if self >> JAVA.UOTV:
                 self.pročitaj(JAVA.UZATV)
                 return "int []";
             else: return JAVA.INT
        elif self >> JAVA.BOOLEAN: return JAVA.BOOLEAN
        else: return JAVA.ID
   
    def FormalList(self):
        #Type ID FormalRest
        tip = self.Type()
        ime = self.pročitaj(JAVA.ID)
        rests = []      
        while not self >> JAVA.OOTV:
            rest = self.FormalRest()
            imer = rest.ime
            if imer in self.rests: raise SemantičkaGreška(
                'Dvaput deklarirana varijabla ' + imev.sadržaj)
            self.rests[imer] = rest
        return ListaArgumenata(tip, ime, rests)

    def FormalRest(self):
        # , Type ID | FormalRest | ''
        if self >> JAVA.ZAREZ:
            tip = self.Type()
            ime = self.pročitaj(JAVA.ID)
            return Rest(tip, ime)
## Statements -> '' | Statement Statements
## Statement -> VOTV Statements VZTV
##              | IF OOTV Exp OZTV Statement ELSE Statement
##              | WHILE OOTV Exp OZTV Statement
##              | SYSTEM TOCKA OUT TOCKA PRINTLN OOTV Exp OZTV TZAREZ
##              | ID JEDNAKO Exp TZAREZ
##              | ID UOTV Exp UZTV JEDNAKO Exp TZAREZ

    def Statement(self):
        if self >> JAVA.VOTV:
            statements = []
            while not self >> JAVA.VZATV:
                statements = append(self.Statement())
        elif self >> JAVA.IF: return self.grananje()
        #elif self >> JAVA.WHILE: return self.petlja()
        elif self >> JAVA.SYSTEM: return self.ispis()
        elif self >> JAVA.ID:
            if self >> JAVA.JEDNAKO: return self.pridruzivanje()
            elif self >> JAVA.UOTV: return self.pridruzivanje_niz()
            else: self.greška()
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
        self.pročitaj(JAVA.WHILE)
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
        print("prije izraz")
        exp = self.Izraz1()
        print("poslije izraz")
        print(exp)
        self.pročitaj(JAVA.OZATV)
        self.pročitaj(JAVA.TZAREZ)
        return Ispis(exp)

    def pridruzivanje(self):
        #ID JEDNAKO Exp TZAREZ
        self.vrati()
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
##        | NEW INT UOTV Exp UZTV
##        | NEW ID OOTV OZTV
##        | NEGACIJA Exp
##        | OOTV Exp OZTV

# Izraz1 -> Izraz1 . Izraz2 | Izraz2
# Izraz2 -> Izraz2 (&&, <) Izraz3 | Izraz3 
# Izraz3 -> Izraz3 (+, -) Izraz4 | Izraz4
# Izraz4 -> Izraz4 * Izraz5 | Izraz5
# Izraz5 -> ! Izraz6
# Izraz6 -> BROJ | TRUE | FALSE | ID | THIS | (Izraz1) | LENGTH | NEW ID OOTV OZATV
#           | ID OOTV ExpList OZATV

    def Izraz1(self):
        print("Izraz1")
        trenutni = self.Izraz2()
        while True:
            if self >> JAVA.TOCKA:
                trenutni = Tocka(trenutni, self.Izraz2())
            else: return trenutni

    def Izraz2(self):
        print("Izraz2")
        trenutni = self.Izraz3()
        while True:
            if self >> { JAVA.AAND, JAVA.MANJE }:
                operacija = self.zadnji
                trenutni = LogičkaOperacija(trenutni, self.Izraz3(), operacija)
            else: return trenutni

    def Izraz3(self):
        print("Izraz3")
        trenutni = self.Izraz4()
        while True:
            if self >> { JAVA.PLUS, JAVA.MINUS }:
                operacija = self.zadnji
                trenutni = AritmetičkaOperacija(trenutni, self.izraz4(), operacija)
            else: return trenutni

    def Izraz4(self):
        print("Izraz4")
        trenutni = self.Izraz5()
        while True:
            if self >> JAVA.PUTA:
                operacija = self.zadnji
                trenutni = AritmetičkaOperacija(trenutni, self.izraz5(), operacija)
            else: return trenutni

    def Izraz5(self):
        print("Izraz5")
        if self >> JAVA.NEGACIJA:
            iza = self.Izraz1()
            return Negacija(iza)
        baza = self.Izraz6()
        return baza
        
    def Izraz6(self):
        print("Izraz6")
        if self >> JAVA.OOTV:
            u_zagradi = self.Izraz1()
            self.pročitaj(JAVA.OZATV)
            return u_zagradi
        if self >> JAVA.ID:
            ime = self.zadnji
            print(ime)
            if self >> JAVA.OOTV:
                varijable = self.ExpList()
                self.pročitaj(JAVA.OZATV)
                return IzvrijedniFunkciju(ime, varijable)
            else: return ime
        if self >> JAVA.NEW:
            ime = self.pročitaj(JAVA.ID)
            self.pročitaj(JAVA.OOTV)
            self.pročitaj(JAVA.OZATV)
            print("new")
            return Napravi_klasu(ime)
        if self >> { JAVA.BROJ, JAVA.TRUE, JAVA.FALSE, JAVA.ID, JAVA.THIS, JAVA.LENGTH }:
            print(self.zadnji)
            return self.zadnji
        
## ExpList -> Exp ExpRest | ''  
    def ExpList(self):
        exp = self.Izraz1()
        print(exp)
        expRests = []
        while not self >> JAVA.OZATV:
            expRests.append(self.ExpRest())
        self.vrati()
        return ListaExp(exp, expRests)

## ExpRest -> , Exp ExpRest | ''   
    def ExpRest(self):
        if self >> JAVA.ZAREZ:
            exp = self.Izraz1()
            return exp

        

class Ispis(AST('exp')):
    def izvrši(self, mem):
        return

class Grananje(AST('exp stat1 stat2')):
    def izvrši(self, mem):
        return

class Pridruzivanje(AST('ime exp')):
    def izvrši(self, mem):
        return

class Pridruzivanje_niz(AST('ime exp')):
    def izvrši(self, mem):
        return

class Napravi_klasu(AST('ime')):
    def izvrši(self, mem):
        return
    
class Main(AST('param statement')):
    def izvrši(self, mem):
        return

class Tocka(AST('izraz1 izraz2')):
    def izvrši(self, mem):
        return

class ListaExp(AST('exp, expRest')):
    def izvrši(self, mem):
        return

class ListaExp1(AST('exp')):
    def izvrši(self, mem):
        return

class expRest(AST('exp, expRest')):
    def izvrši(self, mem):
        return
    
class IzvrijedniFunkciju(AST('ime varijable')):
    def izvrši(self, mem):
        return
    
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
