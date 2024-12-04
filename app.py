import streamlit as st
import pandas as pd
import httpx
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import randint

# Fonction pour obtenir le status code d'une URL avec httpx
async def fetch_status(client, url):
    try:
        response = await client.get(url, timeout=3)  # Réduit le timeout pour un traitement rapide
        if response.status_code == 200:
            return url, response.status_code
        else:
            return url, f"Error: {response.status_code}"
    except httpx.RequestError as e:
        return url, f"Error: {str(e)}"

# Fonction pour traiter les URLs en utilisant httpx avec multithreading
def process_urls(urls):
    results = []
    total_urls = len(urls)
    
    # Créer une barre de progression Streamlit
    progress_bar = st.progress(0)  # Commencer avec une barre vide

    with ThreadPoolExecutor(max_workers=500) as executor:  # Ajustez max_workers pour atteindre la cible de 500/s
        with httpx.AsyncClient() as client:
            futures = [executor.submit(asyncio.run, fetch_status(client, url)) for url in urls]
            for i, future in enumerate(as_completed(futures)):
                results.append(future.result())
                # Mise à jour de la barre de progression
                progress_bar.progress((i + 1) / total_urls)  # Mise à jour en fonction du nombre d'URLs traitées

    return results

st.title("URL Crawler - Status Code Checker")

uploaded_file = st.file_uploader("Importez un fichier d'URLs (CSV ou TXT)", type=["csv", "txt"])

if uploaded_file:
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
