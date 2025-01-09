class Gramatika:
    def __init__(self):
        self.neterminaly = set()  # Set neterminalov
        self.terminaly = set()      # Set terminalov
        self.pravidla = {}             # Dictionary pre pravidla {non_terminal: [productions]}
        self.start_symbol = None    # Starting non-terminal symbol

    def pridaj_neterminaly(self, neterminal): # prida neterminaly
        self.neterminaly.add(neterminal)

    def pridaj_terminal(self, terminal): # prida terminaly
        self.terminaly.add(terminal)

    def pridaj_pravidlo(self, neterminal, prava_strana_pravidla): # funkcia ktora prida pravidlo, s kontrolou, ci sa neterminal nachadza na lavej strane pravidla
        """Add a production rule for a non-terminal.
        Args:
            non_terminal (str): The non-terminal symbol.
            production (str): The production string (combination of terminals and/or non-terminals).
        """
        if neterminal not in self.neterminaly:
            print(f"Error: '{neterminal}' nie je definovany neterminal.")
            return
        if neterminal not in self.pravidla:
            self.pravidla[neterminal] = []
        self.pravidla[neterminal].append(prava_strana_pravidla)

    def urci_start_symbol(self, start_symbol): # urci ktory neterminal je start symbol 
        """Set the starting non-terminal symbol."""
        if start_symbol in self.neterminaly:
            self.start_symbol = start_symbol
        else:
            print(f"Error: '{start_symbol}' nie je zadany medzi neterminalmi.")

    def odstran_nadbytocne_symboly(self): # odstrani nadbytocne symboly
        # Vytvori set kam sa ulozia vsetky generujuce
        generujuce_symboly = set()
        for neterminal, prave_strany in self.pravidla.items(): # tvorba mnoziny Nt
            for prava_strana in prave_strany:
                if all(symbol in self.terminaly for symbol in prava_strana):
                    generujuce_symboly.add(neterminal)

        doslo_k_zmene = True # flag ci doslo k zmene, teda ci sa pridal znak do setu generujucich symbolov 
        while doslo_k_zmene:
            doslo_k_zmene = False
            for neterminal, prave_strany in self.pravidla.items():
                if neterminal not in generujuce_symboly:
                    for prava_strana in prave_strany:
                        if all(symbol in generujuce_symboly or symbol in self.terminaly for symbol in prava_strana):
                            generujuce_symboly.add(neterminal)
                            doslo_k_zmene = True
                            break

        self.neterminaly = self.neterminaly.intersection(generujuce_symboly) # tu sa do v neterminaloch nechaju len tie neterminaly, ktore patria do generujuce symboly
        self.pravidla = {nt: prods for nt, prods in self.pravidla.items() if nt in generujuce_symboly}

        # Odstranenie nedosiahnutelnych symbolov, generacia mnoziny Vd
        dosiahnutelne = {self.start_symbol}
        na_spracovanie = [self.start_symbol] # pomocna, symboly ktore este treba spracovat

        while na_spracovanie:
            aktualny = na_spracovanie.pop()
            if aktualny in self.pravidla:
                for prava_strana in self.pravidla[aktualny]:
                    for symbol in prava_strana:
                        if symbol in self.neterminaly and symbol not in dosiahnutelne:
                            dosiahnutelne.add(symbol)
                            na_spracovanie.append(symbol)

        self.neterminaly = self.neterminaly.intersection(dosiahnutelne)
        self.pravidla = {nt: prods for nt, prods in self.pravidla.items() if nt in dosiahnutelne}

    def zobraz(self): # pomocna fcia na zobrazenie gramatiky
        print("Neterminaly:", ", ".join(self.neterminaly))
        print("Terminaly:", ", ".join(self.terminaly))
        print("Start_symbol:", self.start_symbol)
        print("Pravidla:")
        for non_terminal, productions in self.pravidla.items():
            print(f"  {non_terminal} -> {' | '.join(productions)}")


class Kontrola:
    @staticmethod
    def kontrola_bezkontextovosti(gramatika): # kontrola tohgo ci je gramatika bezkontextova
        for neterminal in gramatika.pravidla: # Prejdeme ci vsetky neterminaly (ktore pouzivame ako lavu stranu pravidla)
            if neterminal not in gramatika.neterminaly: # ak znak nie je v sete neterminalov, znamena to ze na lavej strane nie je neterminal
                return False
        return True

    @staticmethod
    def kontrola_regularity(gramatika): # kontroluje ci je gramatika regularna, teda ak je prava strana vsetkych poravidile jeden terminal alebo terminal a neterminal
        for neterminal, prava_strana_pravidla in gramatika.pravidla.items(): # prejdeme kazde pravidlo
            for terminal in prava_strana_pravidla:
                if len(terminal) == 1: # ak je dlzka PSP 1 a znak nie je terminal nie je regularna
                    if terminal not in gramatika.terminaly:
                        return False
                elif len(terminal) == 2: # ak je dlzka PSP 2 a prvy znak nieje terminal alebo druhy nie je neterminal nie je regularna
                    if terminal[0] not in gramatika.terminaly or terminal[1] not in gramatika.neterminaly:
                        return False
                else:
                    return False
        return True


class FF: # trieda pre tvorby fuirst a follow
    def __init__(self, gramatika):
        self.gramatika = gramatika
        self.first = {nt: set() for nt in gramatika.neterminaly}
        self.follow = {nt: set() for nt in gramatika.neterminaly}
        self.najdi_first()
        self.najdi_follow()

    def najdi_first(self):
        for terminal in self.gramatika.terminaly: # prave stranypravidiel su vzdy bud terminal alebo zacinaju sa terminalom v regularnej gramatike a teda first su ich terminbaly
            self.first[terminal] = {terminal}

        doslo_k_zmene = True # flag na zmenu
        while doslo_k_zmene:
            doslo_k_zmene = False
            for neterminal, PSP in self.gramatika.pravidla.items():
                for prod in PSP: # kazdy item v PSP
                    stara_dlzka = len(self.first[neterminal]) #ulozim dlzku
                    if prod[0] in self.gramatika.terminaly: # ak je na pravej strane terminal, pridam do first mnoziny 
                        self.first[neterminal].add(prod[0])
                    else:
                        for symbol in prod: # ak nie je, vyprazdnim pomocou ''
                            self.first[neterminal].update(self.first[symbol] - {''})
                            if '' not in self.first[symbol]:
                                break
                        else:
                            self.first[neterminal].add('')
                    if len(self.first[neterminal]) > stara_dlzka: # ak je nova dlzka vacsia, doslo k zmene, pokracujem cyklus
                        doslo_k_zmene = True

    def najdi_follow(self):
        """Compute the FOLLOW set for all non-terminals."""
        self.follow[self.gramatika.start_symbol].add('$') # do follow Start symbolu pridam $ ako koniec file alebo epsilon
        doslo_k_zmene = True # flag
        while doslo_k_zmene:
            doslo_k_zmene = False 
            for non_terminal, productions in self.gramatika.pravidla.items():
                for production in productions:
                    follow_temp = self.follow[non_terminal] # temp follow kopia
                    for i, symbol in enumerate(production): # pre kazdy symbol pravej strany
                        if symbol in self.gramatika.neterminaly:
                            stara_velkost = len(self.follow[symbol])
                            if i + 1 < len(production):
                                next_symbol = production[i + 1]
                                self.follow[symbol].update(self.first[next_symbol] - {''})
                                if '' in self.first[next_symbol]:
                                    self.follow[symbol].update(follow_temp)
                            else:
                                self.follow[symbol].update(follow_temp)
                            if len(self.follow[symbol]) > stara_velkost:
                                doslo_k_zmene = True

    def display_first_follow(self): # pomocna metoda pre vypisanie First a Follow
        print("FIRST sety:")
        for non_terminal, first_set in self.first.items():
            print(f"  FIRST({non_terminal}) = {{ {', '.join(first_set)} }}")
        print("\nFOLLOW sety:")
        for non_terminal, follow_set in self.follow.items():
            print(f"  FOLLOW({non_terminal}) = {{ {', '.join(follow_set)} }}")


class Vytvor_DKA:
    def __init__(self, gramatika):
        self.gramatika = gramatika
        self.stavy = set()
        self.abeceda = gramatika.terminaly
        self.start_state = gramatika.start_symbol
        self.prechody = {}  # {(state, symbol): next_state}
        self.koncove_stavy = set()
        self.vytvor_DKA()

    def vytvor_DKA(self): # z regularnej gramatiky vyutvori DKA
        for non_terminal, prod in self.gramatika.pravidla.items():
            for PSP in prod:
                if len(PSP) == 1 and PSP in self.gramatika.terminaly: # ak je na pravej strane iba terminal ideme do akceptujuceho stavu
                    self.prechody[(non_terminal, PSP)] = 'q_akceptujuci'
                    self.koncove_stavy.add('q_akceptujuci')
                elif len(PSP) == 2 and PSP[0] in self.gramatika.terminaly and PSP[1] in self.gramatika.neterminaly:
                    # Case: A -> aB
                    self.prechody[(non_terminal, PSP[0])] = PSP[1]

                self.stavy.add(non_terminal)
                if len(PSP) == 2:
                    self.stavy.add(PSP[1])

    def zobraz_DKA(self): # pomocna na zobrazenie
        print("Stavy:", self.stavy)
        print("Abeceda:", self.abeceda)
        print("Start_state:", self.start_state)
        print("Koncove stavy:", self.koncove_stavy)
        print("Prechody:")
        for (stav, symbol), do_stavu in self.prechody.items():
            print(f"  ({stav}, '{symbol}') -> {do_stavu}")