import time

from funkcije import (
    preberi_pesem,
    ustvari_csv,
    dodaj_pesem_v_csv,
    zberi_vse_urlje_pesmi,
    stevilo_shranjenih_pesmi,
    dodaj_neuspelo_povezavo,
)


STEVILO_STRANI = 86
PREMOR_MED_STRANMI_ZBIRKE = 3
PREMOR_MED_PESMIMI = 1
IME_CSV_DATOTEKE = "pesmi.csv"
IME_DATOTEKE_NEUSPELIH = "neuspele_povezave.txt"


def main():
    
    ustvari_csv(IME_CSV_DATOTEKE)
    ze_shranjenih = stevilo_shranjenih_pesmi(IME_CSV_DATOTEKE)
    print(f"V CSV je že {ze_shranjenih} pesmi.")
    
    
    # Najprej z vseh 86 strani zbirke zberemo povezave do pesmi.
    celotni_urlji = zberi_vse_urlje_pesmi(
        stevilo_strani=STEVILO_STRANI,
        premor=PREMOR_MED_STRANMI_ZBIRKE
    )

    print("\nSkupno različnih povezav:", len(celotni_urlji))
    
    stevec_uspelih = 0
    stevec_neuspelih = 0
    

    for i, url in enumerate(celotni_urlji[ze_shranjenih:], start=ze_shranjenih + 1): # branje nadaljuje tam, kjer je prej zaključil
        print(f"Berem pesem {i}/{len(celotni_urlji)}")

        try:
            podatki = preberi_pesem(url)

            if podatki is not None:
                dodaj_pesem_v_csv(podatki, IME_CSV_DATOTEKE)
                print(f"Shranjena pesem {i}/{len(celotni_urlji)}")
                stevec_uspelih += 1
            else:
                dodaj_neuspelo_povezavo(url, IME_DATOTEKE_NEUSPELIH)  
                stevec_neuspelih += 1          

        except Exception as napaka:
            print("Napaka:", napaka)
            dodaj_neuspelo_povezavo(url, IME_DATOTEKE_NEUSPELIH)

        time.sleep(PREMOR_MED_PESMIMI)

    print("\nUspešnih:", stevec_uspelih)
    print("Neuspešnih:", stevec_neuspelih)


    print(f'Podatki so shranjeni v datoteko "{IME_CSV_DATOTEKE}".')


if __name__ == "__main__":
    main()