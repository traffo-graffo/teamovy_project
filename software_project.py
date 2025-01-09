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
        self.pravidla = {nt: [prod for prod in prods if all(symbol in generujuce_symboly or symbol in self.terminaly for symbol in prod)] for nt, prods in self.pravidla.items() if nt in generujuce_symboly}
        # tu sa preiteruju vsetky pravidla ktore obsahuju neterminaly alebo terminaly z generujucej mnoziny, je to blbo dlhe ale fici to
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
        self.prechody = {}
        self.koncove_stavy = set()
        self.vytvor_DKA()

    def vytvor_DKA(self): # z regularnej gramatiky vyutvori DKA
        for non_terminal, prod in self.gramatika.pravidla.items():
            for PSP in prod:
                if len(PSP) == 1 and PSP in self.gramatika.terminaly: # ak je na pravej strane iba terminal ideme do akceptujuceho stavu
                    self.prechody[(non_terminal, PSP)] = 'q_akceptujuci'
                    self.koncove_stavy.add('q_akceptujuci')
                elif len(PSP) == 2 and PSP[0] in self.gramatika.terminaly and PSP[1] in self.gramatika.neterminaly:
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


class PridajAutomat:
    def __init__(self):
        self.stavy = set()
        self.abeceda = set()
        self.start_state = None
        self.prechody = {} 
        self.koncove_stavy = set()

    def input_nfa(self): # zadavanie DKA
        print("Zadaj stavy (oddelene ciarkou):")
        self.stavy = set(input().split(","))

        print("Zadaj vstupy (oddelene ciarkou):")
        self.abeceda = set(input().split(","))
        self.abeceda.add('epsilon')  # Pravidlo pre pridavanie epsilonu

        print("Zadaj pociatocny stav:")
        self.start_state = input().strip()

        print("Zadaj koncove stavy (oddelene ciarkou):")
        self.koncove_stavy = set(input().split(","))

        print("Zadaj prechody  'Stav,vstupny_symbol -> ddo_stavu,do_stavu,...' (Napis 'done' pre ukoncenie zadavania):")
        while True:
            zadane_prechody = input()
            if zadane_prechody.lower() == 'done':
                break
            try:
                lava_strana, prava_strana = zadane_prechody.split("->")
                stav, vstupny_symbol = lava_strana.split(",")
                do_stavu = prava_strana.split(",")
                if (stav, vstupny_symbol) not in self.prechody: # ak este neexistuje takyto prechod pridaj novy stav z a vstupny symbol
                    self.prechody[(stav, vstupny_symbol)] = []
                self.prechody[(stav, vstupny_symbol)].extend(do_stavu)
            except ValueError:
                print("Nieco bolo zle zadane")

    def riesenie_epsilonu(self, stav): # metoda na vyhodenie epislonu pre spojenie stavov ktore na seba prechadzali na epsilon
        stack = [stav]
        spojeny_stav = {stav}

        while stack: # kym v stacku nieco je popni to a ries
            prave_riesi = stack.pop()
            if (prave_riesi, 'epsilon') in self.prechody: # ak sa nachadza tento stav v prechodoch
                for next_state in self.prechody[(prave_riesi, 'epsilon')]:
                    if next_state not in spojeny_stav:
                        spojeny_stav.add(next_state)
                        stack.append(next_state)

        return spojeny_stav

    def vyrob_DKA(self): # konverzia NKA na DKA
        DKA_stavy = set()
        DKA_start_state = frozenset(self.riesenie_epsilonu(self.start_state))
        DKA_koncove_stavy = set()
        DKA_prechody = {}
        nespracovane_stavy = [DKA_start_state]

        while nespracovane_stavy: # kym este existuju nespracovane stavy
            prave_rieseny = nespracovane_stavy.pop()
            DKA_stavy.add(prave_rieseny)
            if any(state in self.koncove_stavy for state in prave_rieseny): # ak je nejaky stav v koncovych stavoch tak ho pridaj do prave riesenych
                DKA_koncove_stavy.add(prave_rieseny)
            for symbol in self.abeceda - {'epsilon'}: # zbavenie sa epislonovych prechodiov
                nasledujuci_stav = set()
                for stav in prave_rieseny:
                    if (stav, symbol) in self.prechody:
                        for do_stavu in self.prechody[(stav, symbol)]:
                            nasledujuci_stav.update(self.riesenie_epsilonu(do_stavu))
                if nasledujuci_stav:
                    nasledujuci_stav = frozenset(nasledujuci_stav)
                    DKA_prechody[(prave_rieseny, symbol)] = nasledujuci_stav
                    if nasledujuci_stav not in DKA_stavy:
                        nespracovane_stavy.append(nasledujuci_stav)

        self.zobraz_DKA(DKA_stavy, DKA_start_state, DKA_koncove_stavy, DKA_prechody)

    def zobraz_DKA(self, DKA_stavy, DKA_start_state, DKA_koncove_stavy, DKA_prechody):
        print("\nDKA Stavy:", [list(stav) for stav in DKA_stavy])
        print("DKA abeceda:", self.abeceda - {'epsilon'})
        print("DkA Start State:", list(DKA_start_state))
        print("DkA Koncove_stavy:", [list(stav) for stav in DKA_koncove_stavy])
        print("DKA Prechody:")
        for (stav, symbol), dalsi_stav in DKA_prechody.items():
            print(f"  ({list(stav)}, '{symbol}') -> {list(dalsi_stav)}")


# def main():
#     gramatika = Gramatika()

#     print("Zadaj neterminaly (oddelene ciarkou):")
#     neterminaly = input().split(",")
#     for nt in neterminaly:
#         gramatika.pridaj_neterminaly(nt.strip())

#     print("Zadaj terminaly (comma-separated):")
#     terminaly = input().split(",")
#     for t in terminaly:
#         gramatika.pridaj_terminal(t.strip())

#     print("Zadaj pravidla 'NonTerminal -> production' ('done' na ukoncenie):")
#     while True:
#         zadaj_pravidla = input()
#         if zadaj_pravidla.lower() == 'done':
#             break
#         try:
#             neterminal, PSP = zadaj_pravidla.split("->")
#             gramatika.pridaj_pravidlo(neterminal.strip(), PSP.strip())
#         except ValueError:
#             print("Nespravny format")

#     print("Zadaj zaciatocny netemrinal:")
#     start_symbol = input().strip()
#     gramatika.urci_start_symbol(start_symbol)

#     gramatika.zobraz()

#     print("\nKontrola typu gramatiky")
#     if Kontrola.kontrola_bezkontextovosti(gramatika):
#         print("Gramatika je bezkontextova.")
#     else:
#         print("Gramatika nie je bezkontextova.")

#     if Kontrola.kontrola_regularity(gramatika):
#         print("Gramatika je regularna.")
#         print("\nTvorba DKA")
#         dka = Vytvor_DKA(gramatika)
#         dka.zobraz_DKA()
#     else:
#         print("Gramatika nie je regularna netvori sa DKA.")

#     print("\nOdstranenie nadbytocnych symboklov")
#     gramatika.odstran_nadbytocne_symboly()
#     gramatika.zobraz()

#     print("\nTvorba First a Follow.")
#     ff = FF(gramatika)
#     ff.display_first_follow()

#     print("\nZadaj NKA pre transformaciu na DKA")
#     pridaj_automat = PridajAutomat()
#     pridaj_automat.input_nfa()
#     pridaj_automat.vyrob_DKA()


# if __name__ == "__main__":
#     main()



   
