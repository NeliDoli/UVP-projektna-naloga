import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re

url = "https://guitartuna.com/collections/top-chords"

glave = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    )
}

odziv = requests.get(url, headers=glave)

if odziv.status_code == 200:
    with open("top_chords.html", "w", encoding="utf-8") as dat:
        dat.write(odziv.text)
    print("\nStran je shranjena v top_chords.html.\n")
else:
    print("\nStrani ni bilo mogoče uspešno prenesti.\n")
    
    
    
############################################################################################################################################

soup = BeautifulSoup(odziv.text, "html.parser")

linki = soup.find_all("a") # poišči vse HTML elemente - povezave so <a href="...">

# Ista pesem je lahko prisotna v različnih delih strani. Zato shranimo v množico (množica ne upošteva ponovitev)
povezave_do_pesmi = set()
for link in linki:
    href = link.get("href")
    # link.get("href") iz <a href="/chords/perfect...">Perfect</a> vzame samo vrednost atributa href: /chords/perfect...
    # Uporabimo link.get("href") namesto link["href"], ker .get vrne None namesto napake, če oznaka <a> nima atributa href
    if href is not None and href.startswith("/chords/"):
        povezave_do_pesmi.add(href)

    
    
# Trenutno so povezave relativne: /chords/perfect-...
# Za prenos strani potrebujemo celoten URL: https://guitartuna.com/chords/perfect-...
# urljoin združi osnovni naslov in relativno povezavo   
osnovni_url = "https://guitartuna.com"

celotni_urlji = []
for href in povezave_do_pesmi:
    celotni_url = urljoin(osnovni_url, href)
    celotni_urlji.append(celotni_url)
    
celotni_urlji = sorted(celotni_urlji) # množico spremenimo v urejen seznam
    

######################################################################################################################3


def preberi_pesem(url):
    if url.startswith("/"): # če bi bil link relativen
        url = "https://guitartuna.com" + url
        
    odziv = requests.get(url, headers=glave)

    if odziv.status_code != 200:
        print("Napaka pri strani:", url)
        return None

    soup_pesmi = BeautifulSoup(odziv.text, "html.parser")
    
    
    # V HTML-ju Perfect najdem, da so podatki o skladbi zapisani v <script type="application/ld+json">.
    # To je zelo uporabno, ker so že urejeni kot slovar.
    json_skripte = soup_pesmi.find_all(
        "script",
        attrs={"type": "application/ld+json"}
    )

    podatki_skladbe = None

    for skripta in json_skripte:
        podatki = json.loads(skripta.string)

        if podatki.get("@type") == "MusicComposition":
            podatki_skladbe = podatki
            break

    if podatki_skladbe is None:
        print("Ni podatkov MusicComposition:", url)
        return None
    
    
    # Zapis "podatki_skladbe.get("composer", {}).get("name")" pomeni:
    # Iz glavnega slovarja vzemi vrednost pri ključu "composer". To je nov slovar, iz njega vzemi "name".
    # Prazen slovar {} uporabimo zato, da program ne javi napake, če podatka "composer" slučajno ni.
    naslov = podatki_skladbe.get("name")
    if naslov is not None:
        naslov = naslov.removesuffix(" (chords)")
        
        
    izvajalec = podatki_skladbe.get("composer", {}).get("name")
    
    
    url_pesmi = podatki_skladbe.get("url")
    
    
    kljuc = podatki_skladbe.get("musicalKey")
    
    
    # opis_skladbe je niz "Tuning: E A D G B E Key: Ab major Capo: fret 1 Tempo: 95 BPM"
    # BPM pridobimo z regularnim izrazom iz niza "Tuning: E A D G B E Key: Ab major Capo: fret 1 Tempo: 95 BPM"
    
    opis_skladbe = podatki_skladbe.get("text", "") 
    
    ujemanje_bpm = re.search(r"Tempo:\s*(\d+)\s*BPM", opis_skladbe, flags=re.IGNORECASE) 
    if ujemanje_bpm is not None:
        bpm = int(ujemanje_bpm.group(1))
    else:
        bpm = None
        
        
    ujemanje_capo = re.search(r"Capo:\s*fret\s*(\d+)", opis_skladbe, flags=re.IGNORECASE)
    if ujemanje_capo is not None:
        capo = int(ujemanje_capo.group(1))
    # če piše "no capo", izraz ne najde številke in vrne 0 - ni kapodastra
    elif re.search(r"Capo:\s*no capo", opis_skladbe, flags=re.IGNORECASE):
        capo = 0
    else:
        capo = 0 



    # Leto in žanr:
    # V HTML Perfect najdem oznaki:
    # <span data-testid="song-release-year">2017</span>
    # <a data-testid="song-genre">Pop</a>
    leto_oznaka = soup_pesmi.find("span", attrs={"data-testid": "song-release-year"})
    if leto_oznaka is not None:
        leto = int(leto_oznaka.get_text(strip=True))
    else:
        leto = None

    zanr_oznaka = soup_pesmi.find("a", attrs={"data-testid": "song-genre"})
    if zanr_oznaka is not None:
        zanr = zanr_oznaka.get_text(strip=True)
    else:
        zanr = None
        
        
    # Seznam uporabljenih akordov
    seznam_akordov = soup_pesmi.find(
        attrs={"data-testid": "song-chords"}
    )

    uporabljeni_akordi = []

    for akord in seznam_akordov.find_all("p"):
        uporabljeni_akordi.append(
            akord.get_text(strip=True)
        )
    
    
    # Zaporedje skozi pesem:
    # Želimo najti zaporedje akordov v besedilu pesmi.
    # V besedilu pesmi je vsak akord v elementu:
    #       <span class="chordLabel" data-chord="G">
    #           G
    #       </span>
    # Atribut data-chord vsebuje točno ime akorda
    besedilo_pesmi = soup_pesmi.find(
        attrs={"data-testid": "song-lyrics"}
    )

    if besedilo_pesmi is not None:
        oznake_akordov = besedilo_pesmi.find_all(
            "span",
            class_="chordLabel"
        )

        zaporedje_akordov = []

        for oznaka in oznake_akordov:
            akord = oznaka.get("data-chord").strip()
            zaporedje_akordov.append(akord)
    else:
        zaporedje_akordov = []


    # funkcija vrne slovar
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

    
################################################################################
#   import time
#   
#   vse_pesmi = []
#   neuspele_povezave = []
#   
#   for i, url in enumerate(celotni_urlji, start=1):
#       print(f"Berem pesem {i}/{len(celotni_urlji)}")
#   
#       try:
#           podatki = preberi_pesem(url)
#   
#           if podatki is not None:
#               vse_pesmi.append(podatki)
#           else:
#               neuspele_povezave.append(url)
#   
#       except Exception as napaka:
#           print("Napaka:", napaka)
#           neuspele_povezave.append(url)
#   
#       time.sleep(1)
#       
#   print("Uspešnih:", len(vse_pesmi))
#   print("Neuspešnih:", len(neuspele_povezave))

for povezava in soup.find_all("a"):
    besedilo = povezava.get_text(" ", strip=True)

    if besedilo in {"2", "3", "4"}:
        print(
            "Besedilo:", besedilo,
            "href:", povezava.get("href")
        )


url_druge_strani = "https://guitartuna.com/collections/top-chords/2"

odziv_2 = requests.get(url_druge_strani, headers=glave)


soup_2 = BeautifulSoup(odziv_2.text, "html.parser")
tabela_2 = soup_2.find(
    attrs={"data-testid": "collection-table-body"}
)

povezave_2 = set()

for povezava in tabela_2.find_all(
    "a",
    attrs={"data-testid": "collection-table-row"}
):
    href = povezava.get("href")

    if href is not None:
        povezave_2.add("https://guitartuna.com" + href)

print("Število povezav na drugi strani:", len(povezave_2))



for url in list(povezave_2)[:5]:
    print(url)
    
    
    
skupne_povezave = set(celotni_urlji).intersection(povezave_2)
print("Skupnih povezav:", len(skupne_povezave))