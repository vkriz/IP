from pj import *

class JAVA(enum.Enum):
    CLASS, PUBLIC, STATIC, VOID, MAIN, STRING = 'class', 'public', 'static', 'void', 'main' , 'String'
    IF, ELSE = 'if', 'else'
    NEW, THIS, SYSTEM, OUT, PRINTLN = 'new', 'this', 'System', 'out', 'println'
    EXTENDS = 'extends'
    RETURN = 'return'
    LENGTH = 'length'
    OOTV, OZATV, VOTV, VZATV, UOTV, UZATV = '(){}[]'
    TOCKA, TZAREZ, JEDNAKO, ZAREZ = '.',';', '=', ','
    AAND = '&&'
    MANJE, PLUS, MINUS, PUTA, NEGACIJA= '<+-*!'
    INT, BOOLEAN = 'int', 'boolean'
    TRUE, FALSE = 'true', 'false'
    class BROJ(Token):
        def vrijednost(self, mem): return int(self.sadržaj)
    class ID(Token):
        def vrijednost(self, mem): return pogledaj(mem, self)
    class ARRAY(Token):
        def vrijednost(self, imena, vrijednosti):
            return

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
            yield lex.literal(JAVA.ID)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            p = lex.sadržaj
            if p == '0' or p[0] != '0': yield lex.token(JAVA.BROJ)
            else: raise lex.greška('druge baze (osim 10) nisu podržane')
        else: yield lex.literal(JAVA)

        
if __name__ == '__main__':

    ##primjer1
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
    print(ulaz)

    tokeni2 = list(java_lex(ulaz))
    print(*tokeni2)

    ##moraju bit isti
    print(tokeni1==tokeni2)

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
    print(ulaz)

    tokeni3 = list(java_lex(ulaz))
    print(*tokeni3)

    print(tokeni1==tokeni3)

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
    print(ulaz)

    tokeni4 = list(java_lex(ulaz))
    print(*tokeni4)

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
    print(ulaz)

    tokeni5 = list(java_lex(ulaz))
    print(*tokeni5)

    print(tokeni4==tokeni5)

