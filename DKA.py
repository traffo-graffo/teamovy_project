class Deterministicky_automat:
    def __init__(self):
        self.stavy = set()
        self.abeceda = set()
        self.start_stav = None
        self.koncove_stavy = set()
        self.prechody = {}  # {(stav, symbol): nasl_stav}

    def nacitaj_dka(self): # metoda pre nacitanie DKA

        print("Zadaj stavy oddelene ciarkou:")
        self.stavy = set(input().split(","))

        print("Zadaj vstupne symboly oddelene ciarkou:")
        self.abeceda = set(input().split(","))

        print("Zaciatocny stav:")
        self.start_stav = input().strip()

        print("Koncove stavy oddelene ciarkou:")
        self.koncove_stavy = set(input().split(","))

        print("Zadaj prechody 'stav,symbol -> nasledujuci stav' (zadaj done pre koniec):")
        while True:
            prechod_vstup = input()
            if prechod_vstup.lower() == 'done':
                break
            try:
                left, right = prechod_vstup.split("->")
                stav, symbol = left.split(",")
                nasl_stav = right.strip()
                self.prechody[(stav.strip(), symbol.strip())] = nasl_stav
            except ValueError:
                print("Nespravny vstup.")

    def kontrola_konzistencie(self): # kontrola konzistencie DKA

        # Kontrola ci start_state je definovana v sete stavov
        if self.start_stav not in self.stavy:
            print("Tento stav nie je definovany.")
            return False

        # Kontrola co koncove stavy su definovane v sete stavov
        if not self.koncove_stavy.issubset(self.stavy):
            print("Error: Niektore stavy alebo stav niesu definovane v sete stavov, skontroluj zadavanie stavov.")
            return False


    
        for state in self.stavy:
            has_outgoing = any((state, symbol) in self.prechody for symbol in self.abeceda)
            has_incoming = any(next_state == state for next_state in self.prechody.values())
            if not (has_outgoing or has_incoming):
                print(f"Error: Stav {state} nie je na nic napojeny.")
                return False

        print("DKA je konzistentne")
        return True

    def zobraz(self):
        print("\nStavy:", self.stavy)
        print("Symboly na vstup:", self.abeceda)
        print("Start_stav:", self.start_stav)
        print("Koncove stavy:", self.koncove_stavy)
        print("Prechody:")
        for (state, symbol), next_state in self.prechody.items():
            print(f"  ({state}, '{symbol}') -> {next_state}")


def main():
    dfa = Deterministicky_automat()
    dfa.nacitaj_dka()
    dfa.zobraz()
    dfa.kontrola_konzistencie()


if __name__ == "__main__":
    main()
    
# Unit tests
import unittest

class TestDeterministicAutomaton(unittest.TestCase):
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
        

# if __name__ == "__main__":
#     unittest.main()
