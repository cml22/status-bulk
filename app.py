import streamlit as st
import aiohttp
import asyncio
import pandas as pd
import time

# Fonction asynchrone pour obtenir le status code d'une URL
async def fetch_status(session, url):
    try:
        async with session.get(url) as response:
            return url, response.status
    except Exception as e:
        return url, f"Error: {str(e)}"

# Fonction principale pour crawler les URLs
async def crawl_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return results

# Interface Streamlit
st.title("URL Crawler - Status Code Checker")

# Upload de fichier CSV ou TXT contenant les URLs
uploaded_file = st.file_uploader("Importez un fichier d'URLs (CSV ou TXT)", type=["csv", "txt"])

if uploaded_file:
    # Lecture des URLs
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, header=None)
    else:
        df = pd.read_csv(uploaded_file, header=None, sep="\n")
    
    urls = df[0].tolist()
    st.write(f"Total des URLs importées : {len(urls)}")
    
    if st.button("Lancer le crawl"):
        start_time = time.time()
        results = asyncio.run(crawl_urls(urls))
        end_time = time.time()
        
        # Création du DataFrame pour afficher les résultats
        result_df = pd.DataFrame(results, columns=["URL", "Status Code"])
        st.dataframe(result_df)
        
        # Export des résultats
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger les résultats en CSV", data=csv, file_name="crawl_results.csv")
        
        st.write(f"Temps total : {end_time - start_time:.2f} secondes")
