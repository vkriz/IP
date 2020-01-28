from collections import ChainMap
from AST import *

#BKG
        
# Program -> MainClass ClassDecl
# MainClass -> CLASS ID VOTV PUBLIC STATIC VOID MAIN OOTV STRING UOTV UZATV ID OZATV VOTV Statements VZATV VZATV
# ClassDecl -> CLASS ID VOTV VarDecl MethodDecl VZATV
#              | CLASS ID EXTENDS ID VOTV VarDecl MethodDecl VZATV
#              | ClassDecl | ''
# VarDecl -> Type ID TZAREZ VarDecl | ''
# MethodDecl -> PUBLIC Type ID OOTV FormalList OZATV VOTV VarDecl Statements RETURN Exp TZAREZ VZATV MethodDecl | ''
# FormalList -> Type ID FormalRest | ''
# FormalRest -> , Type ID FormalRest | ''
# Type -> BOOLEAN | INT | ID
# Statements -> '' | Statement Statements
# Statement -> VOTV Statements VZATV
#              | IF OOTV Exp OZATV Statement ELSE Statement
#              | WHILE OOTV Exp OZATV Statement
#              | SYSTEM TOCKA OUT TOCKA PRINTLN OOTV Exp OZATV TZAREZ
#              | ID JEDNAKO Exp TZAREZ
# Izraz1 -> Izraz1 OOR Izraz2 | Izraz2
# Izraz2 -> Izraz2 AAND Izraz3 | Izraz3
# Izraz3 -> Izraz3 JEJE Izraz4 | Izraz3 NIJE Izraz4| Izraz4
# Izraz4 -> Izraz4 MANJE Izraz5 | Izraz4 MANJEJ Izraz5 | Izraz4 VECE Izraz5| Izraz4 VECEJ Izraz5  | Izraz5 
# Izraz5 -> Izraz5 PLUS Izraz6 | Izraz5 MINUS Izraz6 | Izraz6
# Izraz6 -> Izraz6 PUTA Izraz7 | Izraz6 DIV Izraz7 | Izraz7
# Izraz7 -> NEGACIJA Izraz7 | Izraz8
# Izraz8 -> Izraz8 TOCKA Izraz10 | Izraz9
# Izraz9 -> BROJ | TRUE | FALSE | ID | THIS | OOTV Izraz1 OZATV | NEW ID OOTV OZATV 
# Izraz10 -> ID OOTV ExpList OZATV
# ExpList -> Exp ExpRest | ''
# ExpRest -> , Exp ExpRest | ''


class JavaParser(Parser):
    def start(self):
        klase = {}
        main = self.MainClass()
        ime_main= main.ime
        if self >> JAVA.VZATV: pass
        while not self >> E.KRAJ:
            klasa = self.ClassDecl()
            imek = klasa.ime
            if imek in klase:
                raise SemantičkaGreška('Dvaput definirana klasa ' + imek.sadržaj)
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

    def ClassDecl(self):
        if self >> JAVA.CLASS:
            ime = self.pročitaj(JAVA.ID)
            ime_roditelja = ""
            if self >> JAVA.EXTENDS:
                ime_roditelja = self.pročitaj(JAVA.ID)
                
            self.pročitaj(JAVA.VOTV)
            varijable = {}
            while not self >> {JAVA.PUBLIC, JAVA.VZATV}:
                varijabla = self.VarDecl()
                imev = varijabla.ime
                if imev in varijable:
                    raise SemantičkaGreška('Dvaput deklarirana varijabla ' + imev.sadržaj)
                varijable[imev] = varijabla
            self.vrati()
            metode = {}
            while not self >> JAVA.VZATV:
                metoda = self.MethodDecl()
                imem = metoda.ime
                if imem in metode:
                    raise SemantičkaGreška('Dvaput definirana metoda ' + imem.sadržaj)
                metode[imem] = metoda
            return Klasa(ime_roditelja, ime, varijable, metode)

    def VarDecl(self):
         tip = self.Type()
         ime = self.pročitaj(JAVA.ID)
         self.pročitaj(JAVA.TZAREZ)
         return Varijabla(tip, ime)

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
            if imev in self.varijable:
                raise SemantičkaGreška('Dvaput deklarirana varijabla ' + imev.sadržaj)
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
        if self >> { JAVA.INT, JAVA.BOOLEAN }:
             return self.zadnji
        else: return self.pročitaj(JAVA.ID)
   
    def FormalList(self):
        varijable = []
        if self >> JAVA.OZATV:
            self.vrati()
            return varijable
        varijabla = Varijabla(self.Type(), self.pročitaj(JAVA.ID))
        varijable.append(varijabla)
        while not self >> JAVA.OZATV:
            varijable.append(self.FormalRest())
        self.vrati()
        return varijable

    def FormalRest(self):
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
        elif self >> JAVA.ID: return self.pridruzivanje()
        else: self.greška()

    def grananje(self):
        self.pročitaj(JAVA.OOTV)
        exp = self.Izraz1()
        self.pročitaj(JAVA.OZATV)
        stat1 = self.Statement()
        self.pročitaj(JAVA.ELSE)
        stat2 = self.Statement()
        return Grananje(exp, stat1, stat2)

    def petlja(self):
        self.pročitaj(JAVA.OOTV)
        exp = self.Izraz1()
        self.pročitaj(JAVA.OZATV)
        stat = self.Statement()
        return Petlja(exp, stat)
        
    def ispis(self):
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
        self.vrati()
        ime = self.pročitaj(JAVA.ID)
        self.pročitaj(JAVA.JEDNAKO)
        exp = self.Izraz1()
        self.pročitaj(JAVA.TZAREZ)
        return Pridruzivanje(ime, exp)

# Izraz1 -> Izraz1 OOR Izraz2 | Izraz2
# Izraz2 -> Izraz2 AAND Izraz3 | Izraz3
# Izraz3 -> Izraz3 JEJE Izraz4 | Izraz3 NIJE Izraz4| Izraz4
# Izraz4 -> Izraz4 MANJE Izraz5 | Izraz4 MANJEJ Izraz5 | Izraz4 VECE Izraz5| Izraz4 VECEJ Izraz5  | Izraz5 
# Izraz5 -> Izraz5 PLUS Izraz6 | Izraz5 MINUS Izraz6 | Izraz6
# Izraz6 -> Izraz6 PUTA Izraz7 | Izraz6 DIV Izraz7 | Izraz7
# Izraz7 -> NEGACIJA Izraz7 | Izraz8
# Izraz8 -> Izraz8 TOCKA Izraz10 | Izraz9
# Izraz9 -> BROJ | TRUE | FALSE | ID | THIS | OOTV Izraz1 OZATV | NEW ID OOTV OZATV 
# Izraz10 -> ID OOTV ExpList OZATV

    def Izraz1(self): 
        trenutni = self.Izraz2()
        while True:
            if self >> JAVA.OOR:
                operacija = self.zadnji
                trenutni = LogičkaOperacija(trenutni, self.Izraz2(), operacija)
            else: return trenutni

    def Izraz2(self): 
        trenutni = self.Izraz3()
        while True:
            if self >> JAVA.AAND:
                operacija = self.zadnji
                trenutni = LogičkaOperacija(trenutni, self.Izraz3(), operacija)
            else: return trenutni

    def Izraz3(self): 
        trenutni = self.Izraz4()
        while True:
            if self >> {JAVA.JEJE, JAVA.NIJE}:
                operacija = self.zadnji
                trenutni = LogičkaOperacija(trenutni, self.Izraz4(), operacija)
            else: return trenutni

    def Izraz4(self): 
        trenutni = self.Izraz5()
        while True:
            if self >> {JAVA.MANJE, JAVA.MANJEJ, JAVA.VECE, JAVA.VECEJ }:
                operacija = self.zadnji
                trenutni = LogičkaOperacija(trenutni, self.Izraz5(), operacija)
            else: return trenutni

    def Izraz5(self): 
        trenutni = self.Izraz6()
        while True:
            if self >> {JAVA.PLUS, JAVA.MINUS}:
                operacija = self.zadnji
                trenutni = AritmetičkaOperacija(trenutni, self.Izraz6(), operacija)
            else: return trenutni

    def Izraz6(self): 
        trenutni = self.Izraz7()
        while True:
            if self >> {JAVA.PUTA, JAVA.DIV}:
                operacija = self.zadnji
                trenutni = AritmetičkaOperacija(trenutni, self.Izraz7(), operacija)
            else: return trenutni

    def Izraz7(self): 
        if self >> JAVA.NEGACIJA:
            iza = self.Izraz7()
            return Negacija(iza)
        baza = self.Izraz8()
        return baza

    def Izraz8(self): 
        trenutni = self.Izraz9()
        while True:
            if self >> JAVA.TOCKA:
                trenutni = Tocka(trenutni, self.Izraz10())
            else: return trenutni
        
    def Izraz9(self):
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
            return Vrati_praznu()

    def Izraz10(self):
        if self >> JAVA.ID:
            ime = self.zadnji
            self.pročitaj(JAVA.OOTV)
            varijable = self.ExpList()
            self.pročitaj(JAVA.OZATV)
            return IzvrijedniFunkciju(ime, varijable)
        
    def ExpList(self):
        expReturn = []
        expReturn.append(self.Izraz1())
        while not self >> JAVA.OZATV:
            expReturn.append(self.ExpRest())
        self.vrati()
        return expReturn

    def ExpRest(self):
        if self >> JAVA.ZAREZ:
            exp = self.Izraz1()
            return exp


#----------------------------------------------------------------------------
        
if __name__ == '__main__':
    #testovi za lekser:

    #primjer1
    ulaz = '''
        class Factorial {
            public static void main(String[] a) {
                 System.out.println(new Fac().ComputeFac(10));
             }
        }
        '''
    print(ulaz)
    tokeni1 = list(java_lex(ulaz))
    print(*tokeni1)
        #CLASS'class' ID'Factorial' VOTV'{' PUBLIC'public' STATIC'static' VOID'void'
        #MAIN'main' OOTV'(' STRING'String' UOTV'[' UZATV']' ID'a' OZATV')' VOTV'{'
        #SYSTEM'System' TOCKA'.' OUT'out' TOCKA'.' PRINTLN'println' OOTV'(' NEW'new'
        #ID'Fac' OOTV'(' OZATV')' TOCKA'.' ID'ComputeFac' OOTV'(' BROJ'10' OZATV')'
        #OZATV')' TZAREZ';' VZATV'}' VZATV'}'

    #primjer2 - komentari
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
    print(ulaz)
    tokeni2 = list(java_lex(ulaz))
    print(*tokeni2)
        #CLASS'class' ID'Factorial' VOTV'{' PUBLIC'public' STATIC'static' VOID'void'
        #MAIN'main' OOTV'(' STRING'String' UOTV'[' UZATV']' ID'a' OZATV')' VOTV'{'
        #SYSTEM'System' TOCKA'.' OUT'out' TOCKA'.' PRINTLN'println' OOTV'(' NEW'new'
        #ID'Fac' OOTV'(' OZATV')' TOCKA'.' ID'ComputeFac' OOTV'(' BROJ'10' OZATV')'
        #OZATV')' TZAREZ';' VZATV'}' VZATV'}'

    #oba primjera bi trebala biti ista (komentari zanemareni)
    print(tokeni1==tokeni2)
        #true

    #primjer3 - sample kod
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
    tokeni = list(java_lex(ulaz))
    print("lekser za sample kod")
    print(*tokeni)
        #CLASS'class' ID'Factorial' VOTV'{' PUBLIC'public' STATIC'static' VOID'void'
        #MAIN'main' OOTV'(' STRING'String' UOTV'[' UZATV']' ID'a' OZATV')' VOTV'{'
        #SYSTEM'System' TOCKA'.' OUT'out' TOCKA'.' PRINTLN'println' OOTV'(' NEW'new'
        #ID'Fac' OOTV'(' OZATV')' TOCKA'.' ID'ComputeFac' OOTV'(' BROJ'10' OZATV')'
        #OZATV')' TZAREZ';' VZATV'}' VZATV'}' CLASS'class' ID'Fac' VOTV'{' PUBLIC'public'
        #INT'int' ID'ComputeFac' OOTV'(' INT'int' ID'num' OZATV')' VOTV'{' INT'int'
        #ID'num_aux' TZAREZ';' IF'if' OOTV'(' ID'num' MANJE'<' BROJ'1' OZATV')' ID'num_aux'
        #JEDNAKO'=' BROJ'1' TZAREZ';' ELSE'else' ID'num_aux' JEDNAKO'=' ID'num' PUTA'*'
        #OOTV'(' THIS'this' TOCKA'.' ID'ComputeFac' OOTV'(' ID'num' MINUS'-' BROJ'1' OZATV')'
        #OZATV')' TZAREZ';' RETURN'return' ID'num_aux' TZAREZ';' VZATV'}' VZATV'}'


    #test za parser i izvršavanje
    #primjer1 - sample kod
    java = JavaParser.parsiraj(java_lex(ulaz))
    print("parser za sample kod")
    print(java)
        #Program(main=Main(ime=ID'Factorial', param=ID'a', statement=Ispis(
        #exp=Tocka(izraz1=Napravi_novi(ime=ID'Fac'), izraz2=IzvrijedniFunkciju(
        #ime=ID'ComputeFac', varijable=[BROJ'10'])))), klase={ID'Fac': Klasa(ime_roditelja='',
        #ime=ID'Fac', varijable={}, metode={ID'ComputeFac': Metoda(tip=INT'int', ime=ID'ComputeFac',
        #argumenti=[Varijabla(tip=INT'int', ime=ID'num')], varijable={ID'num_aux':
        #Varijabla(tip=INT'int', ime=ID'num_aux')}, statements=[Grananje(exp=LogičkaOperacija(
        #prvi=ID'num', drugi=BROJ'1', operacija=MANJE'<'), stat1=Pridruzivanje(ime=ID'num_aux', exp=BROJ'1'),
        #stat2=Pridruzivanje(ime=ID'num_aux', exp=AritmetičkaOperacija(prvi=ID'num', drugi=Tocka(izraz1=THIS'this',
        #izraz2=IzvrijedniFunkciju(ime=ID'ComputeFac', varijable=[AritmetičkaOperacija(prvi=ID'num', drugi=BROJ'1',
        #operacija=MINUS'-')])), operacija=PUTA'*')))], povratna=ID'num_aux')})})

    #testovi za izvršavanje
    #primjer1 - sample kod
    java.izvrši()
        #3628800

    #primjer2 - if, else
    ulaz = '''
        class Printanje {
            public static void main(String[] a) {
                if(2+1<5){
                    System.out.println(10);
                    System.out.println(10);
                }
                 else
                     System.out.println(5);
            }
        }
        '''
    print(ulaz)
    java = JavaParser.parsiraj(java_lex(ulaz))
    java.izvrši()
        #10
        #10

    #primjer3 - poziv fje
    ulaz = '''
        class Zbroj {
            public static void main(String[] a) {
                 System.out.println(new Zbr().Compute(10, 5));
             }
        }
        class Zbr {
         public int Compute(int a, int b) {
             return a+b;
         }
        }
        '''
    print(ulaz)
    java = JavaParser.parsiraj(java_lex(ulaz))
    java.izvrši()
        #15

    #primjer4 - while
    ulaz = '''
        class While {
            public static void main(String[] a) {
                 System.out.println(new Wh().Vrti(5));
             }
        }
        class Wh {
         public int Vrti(int a) {
             while(0<a){
                 a = a - 1;
             }
             return a;
         }
        }
        '''
    print(ulaz)
    java = JavaParser.parsiraj(java_lex(ulaz))
    java.izvrši()
        #0

    #primjer5 - funkcija bez argumenata
    ulaz = '''
        class Ispis {
            public static void main(String[] a) {
                 System.out.println(new Isp().Pisi());
             }
        }
        class Isp {
         public int Pisi() {
             return 5;
         }
        }
        '''
    print(ulaz)
    java = JavaParser.parsiraj(java_lex(ulaz))
    java.izvrši()
        #5


    #primjer6 - boolean, if, !=
    ulaz = '''
        class IF {
            public static void main(String[] a) {
                 System.out.println(new WH().Pisi(true));
             }
        }
        class WH {
         public boolean Pisi(boolean a) {
             boolean b;
             if(a!=true) b = false;
             else b = true;
             return b;
         }
        }
        '''
    print(ulaz)

    java = JavaParser.parsiraj(java_lex(ulaz))
    java.izvrši()
        #True

    #primjer6 - <=, pridruzivanje
    ulaz = '''
        class IF {
            public static void main(String[] a) {
                 System.out.println(new WH().Pisi(10));
             }
        }
        class WH {
         public boolean Pisi(int a) {
             boolean c;
             int b;
             b = 5;
             if(a<=b+5) c = true;
             else c = false;
             return c;
         }
        }
        '''
    print(ulaz)

    java = JavaParser.parsiraj(java_lex(ulaz))
    java.izvrši()
        #True


    #primjer7 - && 
    ulaz = '''
        class IF {
            public static void main(String[] a) {
                 System.out.println(new WH().Pisi(false));
             }
        }
        class WH {
         public boolean Pisi(boolean a) {
             boolean c;
             int b;
             {
                 b = 5;
                 if(2<=b+5 && a) c = true;
                 else c = false;
             }
             return c;
         }
        }
        '''
    print(ulaz)

    java = JavaParser.parsiraj(java_lex(ulaz))
    java.izvrši()
        #False

    #primjer8 - || 
    ulaz = '''
        class IF {
            public static void main(String[] a) {
                 System.out.println(new WH().Pisi(false));
             }
        }
        class WH {
         public boolean Pisi(boolean a) {
             boolean c;
             int b;
             {
                 b = 5;
                 if(2>=b+5 || a) c = true;
                 else c = false;
             }
             return c;
         }
        }
        '''
    print(ulaz)

    java = JavaParser.parsiraj(java_lex(ulaz))
    java.izvrši()
        #False

    
    #primjer9 - svasta 
    ulaz = '''
        class IF {
            public static void main(String[] a) {
                 System.out.println(new WH().Pisi(false));
             }
        }
        class WH {
         public boolean Pisi(boolean a) {
             boolean c;
             int b;
             {
                 b = 5;
                 if(2>=b+5 || a) c = true;
                 else c = false;
             }
             return c;
         }
        }
        '''
    print(ulaz)

    java = JavaParser.parsiraj(java_lex(ulaz))
    java.izvrši()
        #False

    #primjer10 - cjelobrojno dijeljenje, ==, ||
    ulaz = '''
        class IF {
            public static void main(String[] a) {
                 System.out.println(new WH().Pisi(10));
             }
        }
        class WH {
         public int Pisi(int a) {
             int b;
             {
                 b = 5;
                 if(2>=b+5 || a==10) b = 100/a;
                 else b = 50/a;
             }
             return b;
         }
        }
        '''
    print(ulaz)

    java = JavaParser.parsiraj(java_lex(ulaz))
    java.izvrši()
        #10
