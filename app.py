import streamlit as st
import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import randint
from time import sleep

# Fonction pour obtenir le status code d'une URL avec gestion des erreurs
def fetch_status(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, timeout=3)  # Timeout réduit
        if response.status_code == 200:
            return url, response.status_code
        else:
            return url, f"Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return url, f"Error: {str(e)}"

# Fonction pour traiter les URLs avec multithreading et afficher la barre de progression
def process_urls(urls):
    results = []
    total_urls = len(urls)
    
    # Créer une barre de progression Streamlit
    progress_bar = st.progress(0)  # Commencer avec une barre vide

    # Augmenter max_workers pour un nombre élevé de requêtes simultanées
    with ThreadPoolExecutor(max_workers=500) as executor:  # 500 threads simultanés
        future_to_url = {executor.submit(fetch_status, url): url for url in urls}
        for i, future in enumerate(as_completed(future_to_url)):
            results.append(future.result())
            # Mise à jour de la barre de progression
            progress_bar.progress((i + 1) / total_urls)  # Mise à jour en fonction du nombre d'URLs traitées
            # Simulation d'un délai entre les requêtes pour éviter le blocage (0.5-1 sec)
            sleep(randint(1, 2))  # Attendre entre 1 et 2 secondes avant de faire la prochaine requête

    return results

st.title("URL Crawler - Status Code Checker")

uploaded_file = st.file_uploader("Importez un fichier d'URLs (CSV ou TXT)", type=["csv", "txt"])

if uploaded_file:
    # Lire le fichier et nettoyer les données (retirer les lignes mal formatées)
    raw_data = uploaded_file.read().decode('utf-8').splitlines()
    urls = [url.strip() for url in raw_data if url.strip() and len(url.split(',')) == 1]  # Filtrer les lignes mal formatées
    
    st.write(f"Total des URLs importées : {len(urls)}")
    
    if st.button("Lancer le crawl"):
        start_time = time.time()

        # Barre de progression
        with st.spinner("Crawl en cours..."):
            results = process_urls(urls)

        end_time = time.time()

        # Création du DataFrame pour afficher les résultats
        result_df = pd.DataFrame(results, columns=["URL", "Status Code"])
        st.dataframe(result_df)

        # Export des résultats
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger les résultats en CSV", data=csv, file_name="crawl_results.csv")

        st.success(f"Terminé en {end_time - start_time:.2f} secondes")
