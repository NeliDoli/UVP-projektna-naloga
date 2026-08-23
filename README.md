# Analiza akordov in harmonskih progresij v priljubljenih pesmih
Projektna naloga pri predmetu Uvod v programiranje.

## Opis
V projektni nalogi analiziram **17.106 pesmi**, ki sem jih zajela s spletne strani [Guitar Tuna](https://guitartuna.com/collections/top-chords). Tam so pesmi objavljene z akordi in ključem, v katerem so napisane, tako da sem z nekaj znanja glasbene teorije lahko analizirala njihove harmonske značilnosti ter jih primerjala med seboj.

## Zbrani podatki
Za vsako pesem zberemo naslednje podatke:
- naslov
- izvajalec
- ključ (tonaliteta)
- capo (položaj kapodastra)
- leto
- žanr
- vsi uporabljeni akordi
- celotno zaporedje akordov skozi pesem
Iz tega nato izračunamo še število različnih akordov in dolžino zaporedja akordov.
V nadaljnji obravnavi iz teh zajetih podatkov pridobimo kompleksnejše podatke, ki jih uporabimo pri analizi.

## Zgradba in delovanje
Projekt je razdeljen na tri dele: zajem podatkov, priprava podatkov in analiza.

- `funkcije.py` vsebuje funkcije za zajem podatkov s spletne strani. Funkcije zbirajo povezave do pesmi in iz posameznih strani pridobijo zgoraj naštete podatke.
- `main.py` je glavni program za zajem podatkov. Uporablja funkcije iz `funkcije.py`, zbere podatke o pesmih in jih shrani v `pesmi.csv`. Zajem lahko ob ponovnem zagonu nadaljuje pri že shranjenih podatkih (to je pri tako veliki zbirki pomembno).
- `pesmi.csv` vsebuje zajete podatke.
- `priprava.py` pripravi podatke za nadaljnjo obravnavo. Zapise akordov pretvori v sezname, poenoti in poenostavi različne zapise akordov ter izračuna nekatere dodatne podatke. Pripravljeni podatki se shranijo v `pesmi.ociscene.csv`.
- `pesmi_ociscene.csv` vsebuje očiščene in pripravljene podatke za končno analizo.
- `analiza.ipynb` je Jupiter Notebook z glavno analizo podatkov, grafi in interpretacijo rezultatov.

Potek projekta je torej:

`funkcije.py` + `main.py` → `pesmi.csv` → `priprava.py` → `pesmi_ociscene.csv` → `analiza.ipynb`

## Ogled rezultatov

Končni rezultati so predstavljeni v datoteki `analiza.ipynb`.

Za sam ogled rezultatov **ni treba ponovno izvajati zajema podatkov**.
Notebook je mogoče odpreti neposredno na GitHubu, kjer so prikazani
koda, razlage, tabele, grafi in shranjeni rezultati analize.

Notebook uporablja že pripravljeno datoteko `pesmi_ociscene.csv`, zato
ponoven zagon `main.py` in s tem ponoven zajem podatkov s spletne strani
ni potreben.

**OPOMBA:** `pesmi_ociscene.csv` vsebuje podatke, ki smo jih preuredili s `priprava.py` in jih nato uvozili v analizi. `pesmi.csv` pa vsebuje prvotne podatke, direktno izluščene iz spletne strani in je v repozitoriju zgolj za primerjavo, kaj naredi `priprava.py`.

## Uporabljene knjižnice

Za zajem, pripravo in analizo podatkov so uporabljene predvsem knjižnice:

- `requests`
- `BeautifulSoup` (`bs4`)
- `pandas`
- `matplotlib`

Uporabljene so tudi nekatere knjižnice iz Pythonove standardne knjižnice,
med drugim `csv`, `json`, `re` in `ast`.
