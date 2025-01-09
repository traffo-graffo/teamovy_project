from software_project import *
from DKA import *
import unittest




class TestDKA(unittest.TestCase):
    def setUp(self):
        self.dfa = Deterministicky_automat()

    def test_nedefinovany_stav(self):
        self.dfa.stavy = {"q0", "q1"}
        self.dfa.abeceda = {"a", "b"}
        self.dfa.start_stav = "q0"
        self.dfa.koncove_stavy = {"q1"}
        self.dfa.prechody = {
            ("q0", "a"): "q2"  # q2 je nedefinovane
        }
        self.assertFalse(self.dfa.kontrola_konzistencie())


    def test_nedefinovany_start_state(self):
        self.dfa.stavy = {"q1", "q2"}
        self.dfa.abeceda = {"a", "b"}
        self.dfa.start_stav = "q0"  # q0 nedefinovane
        self.dfa.koncove_stavy = {"q1"}
        self.dfa.prechody = {
            ("q1", "a"): "q2",
            ("q2", "b"): "q1"
        }
        self.assertFalse(self.dfa.kontrola_konzistencie())
        
    def test_no_outgoing_or_incoming_transition(self):
        self.dfa.stavy = {"q0", "q1", "q2"}
        self.dfa.abeceda = {"a", "b"}
        self.dfa.start_stav = "q0"
        self.dfa.koncove_stavy = {"q1"}
        self.dfa.prechody = {
            ("q0", "a"): "q1",
            ("q1", "b"): "q0"
            # q2 je sam
        }
        self.assertFalse(self.dfa.kontrola_konzistencie())


class TestGrammar(unittest.TestCase):
    def setUp(self):
        self.gramatika = Gramatika()

    def test_pridaj_neterminal(self):
        self.gramatika.pridaj_neterminaly("S")
        self.assertIn("S", self.gramatika.neterminaly)

    def test_pridaj_terminal(self):
        self.gramatika.pridaj_terminal("a")
        self.assertIn("a", self.gramatika.terminaly)

    def test_pridaj_pravidlpo(self):
        self.gramatika.pridaj_neterminaly("S")
        self.gramatika.pridaj_pravidlo("S", "aSb")
        self.assertIn("S", self.gramatika.pravidla)
        self.assertIn("aSb", self.gramatika.pravidla["S"])

    def test_urci_start_symbol(self):
        self.gramatika.pridaj_neterminaly("S")
        self.gramatika.urci_start_symbol("S")
        self.assertEqual(self.gramatika.start_symbol, "S")
        self.gramatika.urci_start_symbol("A") 
        self.assertEqual(self.gramatika.start_symbol, "S")

    def test_odstran_nadbytocne_znaky(self):
        self.gramatika.pridaj_neterminaly("S")
        self.gramatika.pridaj_neterminaly("A")
        self.gramatika.pridaj_terminal("a")
        self.gramatika.pridaj_pravidlo("S", "aS")
        self.gramatika.pridaj_pravidlo("S", "a")
        self.gramatika.pridaj_pravidlo("A", "aA")  # A is redundant
        self.gramatika.urci_start_symbol("S")
        self.gramatika.odstran_nadbytocne_symboly()
        self.assertIn("S", self.gramatika.neterminaly)
        self.assertNotIn("A", self.gramatika.neterminaly)

def main():
    gramatika = Gramatika()



    print("Zadaj neterminaly (oddelene ciarkou):")
    neterminaly = input().split(",")
    for nt in neterminaly:
        gramatika.pridaj_neterminaly(nt.strip())

    print("Zadaj terminaly (odelene ciarkou):")
    terminaly = input().split(",")
    for t in terminaly:
        gramatika.pridaj_terminal(t.strip())

    print("Zadaj pravidla 'Neterminal -> prava strana' ('done' na ukoncenie):")
    while True:
        zadaj_pravidla = input()
        if zadaj_pravidla.lower() == 'done':
            break
        try:
            neterminal, PSP = zadaj_pravidla.split("->")
            gramatika.pridaj_pravidlo(neterminal.strip(), PSP.strip())
        except ValueError:
            print("Nespravny format")

    print("Zadaj zaciatocny netemrinal:")
    start_symbol = input().strip()
    gramatika.urci_start_symbol(start_symbol)

    gramatika.zobraz()

    print("\nKontrola typu gramatiky")
    if Kontrola.kontrola_bezkontextovosti(gramatika):
        print("Gramatika je bezkontextova.")
    else:
        print("Gramatika nie je bezkontextova.")

    if Kontrola.kontrola_regularity(gramatika):
        print("Gramatika je regularna.")
        print("\nTvorba DKA")
        dka = Vytvor_DKA(gramatika)
        dka.zobraz_DKA()
    else:
        print("Gramatika nie je regularna netvori sa DKA.")

    print("\nTvorba First a Follow.")
    ff = FF(gramatika)
    ff.display_first_follow()

    print("\nOdstranenie nadbytocnych symboklov")
    gramatika.odstran_nadbytocne_symboly()
    gramatika.zobraz()


    print("\nZadaj NKA pre transformaciu na DKA")
    pridaj_automat = PridajAutomat()
    pridaj_automat.input_nfa()
    pridaj_automat.vyrob_DKA()
    
    dfa = Deterministicky_automat()
    dfa.nacitaj_dka()
    dfa.zobraz()
    dfa.kontrola_konzistencie()
    
if __name__ == "__main__":
    main()
    unittest.main()