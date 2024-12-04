import streamlit as st
import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fonction pour obtenir le status code d'une URL
def fetch_status(url):
    try:
        response = requests.get(url, timeout=10)
        return url, response.status_code
    except requests.exceptions.RequestException as e:
        return url, f"Error: {str(e)}"

# Fonction pour traiter les URLs avec multithreading
def process_urls(urls):
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:  # Ajustez max_workers pour équilibrer vitesse et charge
        future_to_url = {executor.submit(fetch_status, url): url for url in urls}
        for future in stqdm(as_completed(future_to_url), total=len(future_to_url)):
            results.append(future.result())
    return results

st.title("URL Crawler - Status Code Checker")

uploaded_file = st.file_uploader("Importez un fichier d'URLs (CSV ou TXT)", type=["csv", "txt"])

if uploaded_file:
    urls = uploaded_file.read().decode('utf-8').splitlines()
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
