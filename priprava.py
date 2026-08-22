import pandas as pd
import ast # za pretvarjanje akordov iz nizov v sezname

pesmi = pd.read_csv("pesmi.csv")

#   print(pesmi.head())
#   print()
#   pesmi.info()
#   print()
#   print(pesmi.columns)
#   print()
#   print(f"Število pesmi: {len(pesmi)}")
#   
#   print("Manjkajoče vrednosti:")
#   print(pesmi.isna().sum())
#   
#   print()
#   print(f"Število popolnoma podvojenih vrstic: {pesmi.duplicated().sum()}")


pesmi["zanr"] = pesmi["zanr"].fillna("Neznano") # Ker smo ugotovili, da pri eni pesmi manjka vrednost žanr.

# PRETVORBA AKORDOV V SEZNAME:
# Stolpca uporabljeni_akordi in zaporedje_akordov sta trenutno niza, čeprav sta videti kot seznama. Za analizo pa potrebujemo seznam.
# ast.literal_eval niz '["G", "Em", "C", "D"]' pretvori v seznam ["G", "Em", "C", "D"].
pesmi["uporabljeni_akordi"] = pesmi["uporabljeni_akordi"].apply(ast.literal_eval)
pesmi["zaporedje_akordov"] = pesmi["zaporedje_akordov"].apply(ast.literal_eval)

# preverimo tip podatka: prej bi dobili <class 'str'>, zdaj pa dobimo <class 'list>:
#       print(type(pesmi.loc[0, "uporabljeni_akordi"]))
#       print(pesmi.loc[0, "uporabljeni_akordi"]) 



# ZAPIS AKORDOV: preverim, kako so zapisani akordi:
#       vsi_akordi = set()
#       
#       for seznam in pesmi["uporabljeni_akordi"]:
#           vsi_akordi.update(seznam)
#       
#       print(sorted(vsi_akordi))
#       print(len(vsi_akordi))


def poenostavi_akord(akord):
    """Funkcija iz akordov odstrani morebitne okraske in poenoti enharmonične tone,
    da dobimo le osnovne akorde: ohranimo osnovni ton, m(mol), #, b."""
    
    # Odstranimo morebitne presledke.
    akord = akord.strip()
    
    # Pri akordu z dodanim basom obdržimo samo del pred poševnico.
    # C/E -> C
    # Am/G -> Am
    akord = akord.split("/")[0]
    
    # Prvi znak je ime tona.
    osnovni_ton = akord[0]
    
    # Če je drugi znak # ali b, je del osnovnega tona.
    if len(akord) >= 2 and akord[1] in ("#", "b"):
        osnovni_ton += akord[1]
        
    # Preostanek akorda brez osnovnega tona.
    ostanek = akord[len(osnovni_ton):]
    
    # Akord je molski, če se preostanek začne z m,
    # vendar ne z maj, saj maj pomeni major (dur) in ga ne upoštevamo, saj je isto C = Cmaj.
    je_mol = ostanek.startswith("m") and not ostanek.startswith("maj")
    
    # Poenotili bomo dva različna zapisa enharmoničnih tonov v en zapis, npr. F# = Gb
    enharmonicni_toni = {
            "Bb": "A#",
            "Db": "C#",
            "Eb": "D#",
            "Gb": "F#",
            "Ab": "G#",
            "B#": "C",
            "E#": "F",
    }
    
    osnovni_ton = enharmonicni_toni.get(osnovni_ton, osnovni_ton)
    
    if je_mol:
        return osnovni_ton + "m"
    
    return osnovni_ton
    
    
# S to funkcijo poenostavimo akorde v obeh stolpcih:
pesmi["uporabljeni_akordi"] = pesmi["uporabljeni_akordi"].apply(
    lambda akordi: list(dict.fromkeys(
        poenostavi_akord(akord) for akord in akordi
    ))
)

pesmi["zaporedje_akordov"] = pesmi["zaporedje_akordov"].apply(
    lambda akordi: [poenostavi_akord(akord) for akord in akordi]
)


# NOVA STOLPCA: dodamo stevilo_razlicnih_akordov in dolzina_zaporedja, ker bosta praktična pri analizah,
# da ju v Notebooku ne bo treba vedno znova računati.
pesmi["stevilo_razlicnih_akordov"] = pesmi["uporabljeni_akordi"].apply(len)
pesmi["dolzina_zaporedja"] = pesmi["zaporedje_akordov"].apply(len)


# Preverim, katere različne poenostavljene okorde imam (moralo bi jih biti 24):
#       vsi_akordi = set()
#       
#       for akordi in pesmi["uporabljeni_akordi"]:
#           vsi_akordi.update(akordi)
#       
#       print(sorted(vsi_akordi))
#       print(f"Število različnih poenostavljenih akordov: {len(vsi_akordi)}")

pesmi.to_csv("pesmi_ociscene.csv", index=False)