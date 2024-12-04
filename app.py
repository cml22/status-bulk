import streamlit as st
import pandas as pd
import requests
import time

def fetch_status(url):
    try:
        response = requests.get(url, timeout=10)
        return url, response.status_code
    except requests.exceptions.RequestException as e:
        return url, f"Error: {str(e)}"

st.title("URL Crawler - Status Code Checker")

uploaded_file = st.file_uploader("Importez un fichier d'URLs (CSV ou TXT)", type=["csv", "txt"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, header=None, names=["URL"], dtype=str)
    urls = df["URL"].tolist()
    st.write(f"Total des URLs importées : {len(urls)}")
    
    if st.button("Lancer le crawl"):
        start_time = time.time()
        results = [fetch_status(url) for url in urls]
        end_time = time.time()
        
        result_df = pd.DataFrame(results, columns=["URL", "Status Code"])
        st.dataframe(result_df)
        
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger les résultats en CSV", data=csv, file_name="crawl_results.csv")
        
        st.write(f"Temps total : {end_time - start_time:.2f} secondes")
