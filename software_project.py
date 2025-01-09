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