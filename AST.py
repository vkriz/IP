from lexer import * 
from collections import ChainMap

class Ispis(AST('exp')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        print(self.exp.vrijednost(tipovi, vrijednosti, klase, ime_k))

class Grananje(AST('exp stat1 stat2')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        if (self.exp.vrijednost(tipovi, vrijednosti, klase, ime_k)): 
            self.stat1.izvrši(tipovi, vrijednosti, klase, ime_k)
        else:
            self.stat2.izvrši(tipovi, vrijednosti, klase, ime_k)

class Petlja(AST('exp stat')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        while(self.exp.vrijednost(tipovi, vrijednosti, klase, ime_k)):
            self.stat.izvrši(tipovi, vrijednosti, klase, ime_k)


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
        if (isinstance(lijevi, bool)):
            if (not isinstance(desni, bool)):
                raise SemantičkaGreška("Nekompatibilni tipovi")
            else:
                lijevi = desni
                vrijednosti[self.ime] = lijevi

class Tocka(AST('izraz1 izraz2')):
    def vrijednost(self, tipovi, vrijednosti, klase, ime_k):
        if self.izraz1 ^ JAVA.THIS:
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
            evaluiraniArgumenti.append(var.vrijednost(tipovi, vrijednosti, klase, ime_k))
        metode_d = dict(klase_d[ime_klase].metode)
        return metode_d[self.ime].izvrši(klasa.tipovi, klasa.vrijednosti, klase, evaluiraniArgumenti, ime_k)

class Varijabla(AST('tip ime')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        if (self.ime in tipovi):
            self.ime.redeklaracija()
        tipovi[self.ime] = self.tip
        if self.tip ^ JAVA.INT:
            vrijednosti[self.ime] = 0
        elif self.tip ^ JAVA.BOOLEAN:
            vrijednosti[self.ime] = False
        return self
    def vrijednost(self, tipovi, vrijednosti, klase, ime_k): 
        return vrijednosti[self.ime]
    def pridruzi(self, tipovi, vrijednosti, klase, vrijed, ime_k):
        vrijednosti[self.ime] = vrijed
        return vrijed
    
class LogičkaOperacija(AST('prvi drugi operacija')):
    def vrijednost(self, tipovi, vrijednosti, klase, ime_k):
        lijevi = self.prvi.vrijednost(tipovi, vrijednosti, klase, ime_k)
        if self.operacija ^ JAVA.AAND:
            if (lijevi is False): return False
        if self.operacija ^ JAVA.OOR:
            if (lijevi is True): return True
        desni = self.drugi.vrijednost(tipovi, vrijednosti, klase, ime_k)
        if self.operacija ^ JAVA.AAND:
            return bool(lijevi and desni)
        if self.operacija ^ JAVA.OOR:
            return bool(lijevi or desni)
        elif self.operacija ^ JAVA.MANJE: return lijevi < desni
        elif self.operacija ^ JAVA.MANJEJ: return lijevi <= desni
        elif self.operacija ^ JAVA.VECE: return lijevi > desni
        elif self.operacija ^ JAVA.VECEJ: return lijevi >= desni
        elif self.operacija ^ JAVA.JEJE: return lijevi == desni
        elif self.operacija ^ JAVA.NIJE: return lijevi != desni
    def izvrši(izraz, imena, vrijednosti, klase, ime_k):
        izraz.vrijednost(imena, vrijednosti, klase, ime_k) 

class AritmetičkaOperacija(AST('prvi drugi operacija')):
    def vrijednost(self, tipovi, vrijednosti, klase, ime_k):
        try:
            lijevi = self.prvi.vrijednost(tipovi, vrijednosti, klase, ime_k)
            desni = self.drugi.vrijednost(tipovi, vrijednosti, klase, ime_k)
        except ValueError:
            raise SemantičkaGreška("neispravna binarna operacija")
        if self.operacija ^ JAVA.PLUS:
            rezultat = lijevi + desni
        elif self.operacija ^ JAVA.MINUS:
            rezultat = lijevi - desni
        elif self.operacija ^ JAVA.PUTA:
            rezultat = lijevi * desni
        elif self.operacija ^ JAVA.DIV:
            rezultat = lijevi // desni  
        return rezultat
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        self.vrijednost(tipovi, vrijednosti, klase, ime_k)

class Negacija(AST('iza')):
    def vrijednost(self, tipovi, vrijednosti, klase, ime_k):
        vrijed = self.iza.vrijednost(tipovi, vrijednosti, klase, ime_k)
        if (not isinstance(vrijed, bool)):
            raise SemantičkaGreška("unarna negacija se izvršava samo na boolu")
        return not vrijed
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        self.vrijednost(tipovi, vrijednosti, klase, ime_k)

class Metoda(AST('tip ime argumenti varijable statements povratna')):
    def napuni(self, tipovi, vrijednosti, klase, ime_k):
        self.tipovi = tipovi.new_child()
        self.vrijednosti = vrijednosti.new_child()
        varijable = dict(self.varijable)
        self.ime_k = ime_k
        for var in varijable:
            varijable[var].izvrši(self.tipovi, self.vrijednosti, klase, ime_k)
    def izvrši(self, tipovi, vrijednosti, klase, evaluiraniArgumenti, ime_k):
        br = 0
        for arg in self.argumenti: 
            self.vrijednosti[arg.ime] = evaluiraniArgumenti[br]
            br=br+1
        for stat in self.statements:
            stat.izvrši(self.tipovi, self.vrijednosti, klase, ime_k)
        return self.povratna.vrijednost(self.tipovi, self.vrijednosti, klase, ime_k)

class Napravi_novi(AST('ime')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        return self.ime

class Vrati_praznu(AST('')):
    def vrijednost(self, tipovi, vrijednosti, klase, ime_k):
        return

class Statements(AST('statements')):
    def izvrši(self, tipovi, vrijednosti, klase, ime_k):
        for stat in self.statements:
            stat.izvrši(tipovi, vrijednosti, klase, ime_k)    

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
