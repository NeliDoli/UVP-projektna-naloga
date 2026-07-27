import csv
import json
import re
import time
from urllib.parse import urljoin
import os

import requests
from bs4 import BeautifulSoup

OSNOVNI_URL = "https://guitartuna.com"
URL_ZBIRKE = "https://guitartuna.com/collections/top-chords"

glave = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    )
}


def zajemi_html(url):
    """Prenese spletno stran in vrne njen HTML kot niz."""
    odziv = requests.get(url, headers=glave, timeout=20)
    
    if odziv.status_code == 403:
        print("Dostop je začasno zavrnjen. Program se ustavlja.")
        return None

    if odziv.status_code != 200:
        print("Napaka pri strani:", url, "- status:", odziv.status_code)
        return None

    return odziv.text

def naredi_soup(url):
    """Prenese spletno stran in vrne objekt BeautifulSoup."""
    html = zajemi_html(url)

    if html is None:
        return None

    return BeautifulSoup(html, "html.parser")


def url_strani_zbirke(stevilka_strani):
    """Vrne URL izbrane strani zbirke Top Chords."""
    if stevilka_strani == 1:
        return URL_ZBIRKE

    return f"{URL_ZBIRKE}/{stevilka_strani}"

def izlusci_urlje_pesmi(soup):
    """Iz glavne tabele ene strani izlušči URL-je pesmi."""
    tabela = soup.find(
        attrs={"data-testid": "collection-table-body"}
    )

    if tabela is None:
        return set()

    # Ker želimo ohraniti vrstni red kot na spletni strani, moramo uporabiti seznam in ne množice.
    # Morebitne podvojitve bomo odstranili v funkciji zberi_vse_urlje_pesmi z ze_videni.
    povezave_do_pesmi = []

    for povezava in tabela.find_all(
        "a",
        attrs={"data-testid": "collection-table-row"}
    ):
        href = povezava.get("href")

        # povezava.get("href") iz <a href="/chords/perfect...">Perfect</a>
        # vzame samo vrednost atributa href: /chords/perfect...
        # Uporabimo .get namesto povezava["href"], ker .get vrne None
        # namesto napake, če oznaka <a> nima atributa href.
        if href is not None:
            # Trenutno so povezave relativne: /chords/perfect-...
            # Za prenos strani potrebujemo celoten URL:
            # https://guitartuna.com/chords/perfect-...
            # urljoin združi osnovni naslov in relativno povezavo.
            celotni_url = urljoin(OSNOVNI_URL, href)
            povezave_do_pesmi.append(celotni_url)

    return povezave_do_pesmi

def zberi_vse_urlje_pesmi(stevilo_strani=86, premor=0.5):
    """Zbere URL-je pesmi z vseh strani zbirke Top Chords."""
    vsi_urlji_pesmi = []
    ze_videni = set()

    for stran in range(1, stevilo_strani + 1):
        print(f"Berem stran zbirke {stran}/{stevilo_strani}")

        url = url_strani_zbirke(stran)
        soup = naredi_soup(url)

        if soup is None:
            print("Strani zbirke ni bilo mogoče prebrati:", stran)
            continue

        urlji_na_strani = izlusci_urlje_pesmi(soup)
        
        for url in urlji_na_strani:
            if url not in ze_videni:
                vsi_urlji_pesmi.append(url)
                ze_videni.add(url)

        print("Trenutno zbranih URL-jev:", len(vsi_urlji_pesmi))
        time.sleep(premor)

    return vsi_urlji_pesmi

def izlusci_podatke_music_composition(soup_pesmi):
    """V JSON-LD poišče slovar tipa MusicComposition."""
    # V HTML-ju Perfect najdem, da so podatki o skladbi zapisani
    # v <script type="application/ld+json">.
    # To je zelo uporabno, ker so že urejeni kot slovar.
    json_skripte = soup_pesmi.find_all(
        "script",
        attrs={"type": "application/ld+json"}
    )

    for skripta in json_skripte:
        if skripta.string is None:
            continue

        try:
            podatki = json.loads(skripta.string)
        except json.JSONDecodeError:
            continue

        if isinstance(podatki, dict) and podatki.get("@type") == "MusicComposition":
            return podatki

    return None

def izlusci_osnovne_podatke(podatki_skladbe):
    """Iz slovarja MusicComposition izlušči naslov, izvajalca, URL in ključ."""
    naslov = podatki_skladbe.get("name")
    if naslov is not None:
        naslov = naslov.removesuffix(" (chords)")

    # Zapis podatki_skladbe.get("composer", {}).get("name") pomeni:
    # Iz glavnega slovarja vzemi vrednost pri ključu "composer".
    # To je nov slovar, iz njega vzemi "name".
    # Prazen slovar {} uporabimo zato, da program ne javi napake,
    # če podatka "composer" slučajno ni.
    izvajalec = podatki_skladbe.get("composer", {}).get("name")

    url_pesmi = podatki_skladbe.get("url")
    kljuc = podatki_skladbe.get("musicalKey")

    return naslov, izvajalec, url_pesmi, kljuc


def izlusci_bpm_in_capo(podatki_skladbe):
    """Iz opisa skladbe izlušči tempo in položaj kapodastra."""
    # opis_skladbe je niz:
    # "Tuning: E A D G B E Key: Ab major Capo: fret 1 Tempo: 95 BPM"
    # BPM pridobimo z regularnim izrazom iz tega niza.
    opis_skladbe = podatki_skladbe.get("text", "")

    ujemanje_bpm = re.search(
        r"Tempo:\s*(\d+)\s*BPM",
        opis_skladbe,
        flags=re.IGNORECASE
    )

    if ujemanje_bpm is not None:
        bpm = int(ujemanje_bpm.group(1))
    else:
        bpm = None

    ujemanje_capo = re.search(
        r"Capo:\s*fret\s*(\d+)",
        opis_skladbe,
        flags=re.IGNORECASE
    )

    if ujemanje_capo is not None:
        capo = int(ujemanje_capo.group(1))
    # Če piše "no capo", izraz ne najde številke in vrne 0:
    # ni kapodastra.
    elif re.search(
        r"Capo:\s*no capo",
        opis_skladbe,
        flags=re.IGNORECASE
    ):
        capo = 0
    else:
        capo = 0

    return bpm, capo

def izlusci_leto_in_zanr(soup_pesmi):
    """Iz HTML-ja izlušči leto izida in žanr."""
    # Leto in žanr:
    # V HTML Perfect najdem oznaki:
    # <span data-testid="song-release-year">2017</span>
    # <a data-testid="song-genre">Pop</a>
    leto_oznaka = soup_pesmi.find(
        "span",
        attrs={"data-testid": "song-release-year"}
    )

    if leto_oznaka is not None:
        besedilo_leta = leto_oznaka.get_text(strip=True)

        try:
            leto = int(besedilo_leta)
        except ValueError:
            leto = None
    else:
        leto = None

    zanr_oznaka = soup_pesmi.find(
        "a",
        attrs={"data-testid": "song-genre"}
    )

    if zanr_oznaka is not None:
        zanr = zanr_oznaka.get_text(strip=True)
    else:
        zanr = None

    return leto, zanr


def izlusci_uporabljene_akorde(soup_pesmi):
    """Vrne seznam različnih akordov, navedenih pri pesmi."""
    # Seznam uporabljenih akordov.
    seznam_akordov = soup_pesmi.find(
        attrs={"data-testid": "song-chords"}
    )

    if seznam_akordov is None:
        return []

    uporabljeni_akordi = []

    for akord in seznam_akordov.find_all("p"):
        ime_akorda = akord.get_text(strip=True)

        if ime_akorda:
            uporabljeni_akordi.append(ime_akorda)

    return uporabljeni_akordi


def izlusci_zaporedje_akordov(soup_pesmi):
    """Vrne akorde po vrstnem redu, kakor se pojavijo v pesmi."""
    # Želimo najti zaporedje akordov skozi pesem:
    # V besedilu pesmi je vsak akord v elementu:
    #       <span class="chordLabel" data-chord="G">
    #           G
    #       </span>
    # Atribut data-chord vsebuje točno ime akorda.
    besedilo_pesmi = soup_pesmi.find(
        attrs={"data-testid": "song-lyrics"}
    )

    if besedilo_pesmi is None:
        return []

    oznake_akordov = besedilo_pesmi.find_all(
        "span",
        class_="chordLabel"
    )

    zaporedje_akordov = []

    for oznaka in oznake_akordov:
        akord = oznaka.get("data-chord")

        if akord is not None:
            zaporedje_akordov.append(akord.strip())

    return zaporedje_akordov


def pesem_v_slovar(soup_pesmi, url):
    """Iz že prenesene strani sestavi slovar s podatki o eni pesmi."""
    podatki_skladbe = izlusci_podatke_music_composition(soup_pesmi)

    if podatki_skladbe is None:
        print("Ni podatkov MusicComposition:", url)
        return None

    naslov, izvajalec, url_pesmi, kljuc = izlusci_osnovne_podatke(
        podatki_skladbe
    )
    bpm, capo = izlusci_bpm_in_capo(podatki_skladbe)
    leto, zanr = izlusci_leto_in_zanr(soup_pesmi)
    uporabljeni_akordi = izlusci_uporabljene_akorde(soup_pesmi)
    zaporedje_akordov = izlusci_zaporedje_akordov(soup_pesmi)

    # Funkcija vrne slovar.
    return {
        "naslov": naslov,
        "izvajalec": izvajalec,
        "url": url_pesmi,
        "kljuc": kljuc,
        "bpm": bpm,
        "capo": capo,
        "leto": leto,
        "zanr": zanr,
        "uporabljeni_akordi": uporabljeni_akordi,
        "zaporedje_akordov": zaporedje_akordov
    }


def preberi_pesem(url):
    """Prenese stran ene pesmi in vrne slovar z njenimi podatki."""
    if url.startswith("/"):  # če bi bil link relativen
        url = urljoin(OSNOVNI_URL, url)

    soup_pesmi = naredi_soup(url)

    if soup_pesmi is None:
        return None

    return pesem_v_slovar(soup_pesmi, url)


def ustvari_csv(ime_datoteke="pesmi.csv"):
    """Ustvari novo CSV datoteko in zapiše glavo. (Če CSV še ne obstaja, sicer bi le nadaljeval zapis vanjo)"""

    if os.path.exists(ime_datoteke):
        return
    
    imena_stolpcev = [
        "naslov",
        "izvajalec",
        "url",
        "kljuc",
        "bpm",
        "capo",
        "leto",
        "zanr",
        "uporabljeni_akordi",
        "zaporedje_akordov"
    ]

    with open(
        ime_datoteke,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as datoteka:

        pisatelj = csv.DictWriter(
            datoteka,
            fieldnames=imena_stolpcev
        )

        pisatelj.writeheader()
        
        
def stevilo_shranjenih_pesmi(ime_datoteke="pesmi.csv"):
    """Vrne število že shranjenih pesmi."""
    
    if not os.path.exists(ime_datoteke):
        return 0
    
    with open(
        ime_datoteke,
        "r",
        encoding="utf-8-sig"
    ) as datoteka:

        # Prva vrstica je glava - je ne štejemo.
        return max(0, sum(1 for _ in datoteka) - 1)
        
def dodaj_pesem_v_csv(pesem, ime_datoteke="pesmi.csv"):
    """Doda eno pesem na konec CSV datoteke."""

    vrstica = pesem.copy()

    # Seznama pretvorimo v JSON zapis,
    # da se akordi v CSV-ju ohranijo kot seznama.
    vrstica["uporabljeni_akordi"] = json.dumps(
        vrstica["uporabljeni_akordi"],
        ensure_ascii=False
    )

    vrstica["zaporedje_akordov"] = json.dumps(
        vrstica["zaporedje_akordov"],
        ensure_ascii=False
    )

    with open(
        ime_datoteke,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as datoteka:

        pisatelj = csv.DictWriter(
            datoteka,
            fieldnames=vrstica.keys()
        )

        pisatelj.writerow(vrstica)
        

def dodaj_neuspelo_povezavo(url, ime_datoteke="neuspele_povezave.txt"):
    """Doda URL neuspele pesmi na konec besedilne datoteke."""

    with open(
        ime_datoteke,
        "a",
        encoding="utf-8"
    ) as datoteka:
        datoteka.write(url + "\n")
        
        
        