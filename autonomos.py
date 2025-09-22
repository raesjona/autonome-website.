# === AUTONOMOS.PY VERSIE 2.0 (DEFINITIEF) ===
import openai
import os
import random
from datetime import datetime
import git

# --- CONFIGURATIE ---
openai.api_key = os.getenv('OPENAI_API_KEY')
REPO_PATH = '.' 
POSTS_PATH = '_posts' 

# --- LIJST VAN ONDERWERPEN ---
# Deze lijst kan in de toekomst worden uitgebreid met meer onderwerpen voor je niche
onderwerpen = [
    "5 manieren om plastic te verminderen in je appartement",
    "Hoe maak je een verticale kruidentuin op je balkon?",
    "De beste luchtzuiverende planten voor een kleine woonkamer",
    "Minimalistisch leven: opruimtips voor een klein appartement",
    "DIY: maak je eigen compostbak voor op het balkon",
    "Energie besparen in een huurappartement: een complete gids",
    "Zero-waste boodschappen doen: hoe begin je?",
    "Duurzame schoonmaakmiddelen die je zelf kunt maken",
    "Tips voor een tweedehands en vintage interieur",
    "Water besparen in de badkamer: simpele aanpassingen",
    "Een capsulegarderobe samenstellen: minder kleding, meer stijl",
    "Natuurlijke pesticiden voor je kamerplanten",
    "Upcycling: geef oude meubels een nieuw leven in je appartement"
]

# --- FUNCTIES ---

def genereer_artikel(onderwerp):
    """Genereert een artikel met het krachtige GPT-4o model."""
    try        
        prompt = f"""
        Schrijf een SEO-geoptimaliseerd, diepgaand en boeiend Nederlandstalig blogartikel van ongeveer 500 woorden over: '{onderwerp}'.
        Gebruik duidelijke koppen (markdown ##), korte alinea's en een deskundige, behulpzame toon.
        Geef praktische, unieke tips die direct toepasbaar zijn. Sluit af met een krachtige samenvatting.
        De schrijfstijl is vlot, inspirerend en gericht op millennials die in de stad wonen.
        """
        response = openai.chat.completions.create(
            model="gpt-4o", # Gebruikt het krachtigste, geüpgradede model
            messages=[
                {"role": "system", "content": "Jij bent een expert in duurzaam en bewust leven en schrijft inspirerende blogposts."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Fout bij het genereren van artikel: {e}")
        return None

def voeg_affiliate_links_in(tekst):
    """Voegt affiliate links in op basis van keywords."""
    if not os.path.exists(POSTS_PATH):
        os.makedirs(POSTS_PATH)
    affiliate_data = os.getenv('AFFILIATE_LINKS', '').split(';')
    if not affiliate_data or affiliate_data == ['']:
        return tekst
    links_map = {item.split(',')[0]: item.split(',')[1] for item in affiliate_data if ',' in item}
    
    for keyword, link in links_map.items():
        if keyword.lower() in tekst.lower():
            cta = f'\n\n> **Aanrader: Bekijk [relevante producten voor {keyword}]({link}) op Bol.com!**\n'
            tekst += cta
            # Stop na de eerste relevante link om het artikel natuurlijk te houden
            return tekst
    return tekst

def publiceer_naar_github(onderwerp, content):
    """Creëert een nieuw post-bestand en commit dit naar GitHub."""
    vandaag = datetime.now()
    # Maakt een URL-vriendelijke bestandsnaam
    slug = onderwerp.lower().replace(' ', '-').replace('?', '').replace(':', '').replace(',', '')[:40]
    bestandsnaam = f"{vandaag.strftime('%Y-%-m-%-d')}-{slug}.md"
    pad = os.path.join(POSTS_PATH, bestandsnaam)

    # Dit is het 'label' waar je eerder naar vroeg
    front_matter = f"""---
layout: post
title:  "{onderwerp.replace('"', "'")}"
date:   {vandaag.isoformat()}
---
"""
    volledige_content = front_matter + content

    with open(pad, 'w', encoding='utf-8') as f:
        f.write(volledige_content)

    try:
        repo = git.Repo(REPO_PATH)
        repo.config_writer().set_value("user", "name", "Autonomos Bot").release()
        repo.config_writer().set_value("user", "email", "bot@github.com").release()
        repo.index.add([pad])
        repo.index.commit(f"Nieuw artikel gepubliceerd: {onderwerp}")
        origin = repo.remote(name='origin')
        origin.push()
        print(f"Artikel '{bestandsnaam}' succesvol gepubliceerd.")
    except Exception as e:
        print(f"Fout bij het publiceren naar GitHub: {e}")

# --- HOOFDSCRIPT DAT ELKE DAG DRAAIT ---
if __name__ == "__main__":
    gekozen_onderwerp = random.choice(onderwerpen)
    print(f"Gekozen onderwerp: {gekozen_onderwerp}")
    
    artikel_tekst = genereer_artikel(gekozen_onderwerp)
    
    if artikel_tekst:
        artikel_met_links = voeg_affiliate_links_in(artikel_tekst)
        publiceer_naar_github(gekozen_onderwerp, artikel_met_links)
