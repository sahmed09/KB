from scholarly import scholarly, ProxyGenerator
import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# --- Google Scholar Search ---
def search_google_scholar(query, max_results=100):
    # pg = ProxyGenerator()
    # pg.FreeProxies()
    # scholarly.use_proxy(pg)

    search_query = scholarly.search_pubs(query)
    results = []

    for i, paper in enumerate(search_query):
        if i >= max_results:
            break
        results.append({
            'title': paper['bib']['title'],
            'authors': paper['bib'].get('author', 'Unknown'),
            'year': paper['bib'].get('pub_year', 'Unknown'),
            'link': paper.get('pub_url', 'No URL')
        })

    return results


# --- CrossRef API Search ---
def search_crossref(query, max_results=100):
    url = f"https://api.crossref.org/works?query={query}&rows={max_results}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Error: {response.status_code}"

    data = response.json()
    articles = []

    for item in data['message']['items']:
        authors = (
            [author.get('family', 'Unknown') for author in item.get('author', [])]
            if 'author' in item else 'Unknown'
        )
        articles.append({
            'title': item.get('title', ['Unknown'])[0],
            'authors': authors,
            'year': item.get('published-print', {}).get('date-parts', [[None]])[0][0],
            'doi': item.get('DOI', 'No DOI'),
            'link': f"https://doi.org/{item.get('DOI', '')}"
        })

    return articles


# --- Semantic Scholar API Search ---
def search_semantic_scholar(query, max_results=100):
    # api_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    # params = {"query": "cyber deception", "limit": 5, "fields": "title,authors,year,url"}
    # response = requests.get(api_url, params=params)
    # papers = response.json()
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={max_results}&fields=title,authors,year,url"

    time.sleep(2)

    response = requests.get(url)

    if response.status_code == 429:
        print("Rate limit hit! Waiting before retrying...")
        time.sleep(5)  # Wait longer before retrying
        return search_semantic_scholar(query, max_results)

    if response.status_code != 200:
        return f"Error: {response.status_code}"

    data = response.json()
    articles = []

    for item in data.get('data', []):
        articles.append({
            'title': item.get('title', 'Unknown'),
            'authors': [author['name'] for author in item.get('authors', [])] if 'authors' in item else 'Unknown',
            'year': item.get('year', 'Unknown'),
            'link': item.get('url', 'No URL')
        })

    return articles


# --- ResearchGate Scraper using Selenium ---
# def search_researchgate(query, max_results=5):
#     """Search ResearchGate using Selenium."""
#     service = Service(ChromeDriverManager().install())
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")  # Run in headless mode
#     driver = webdriver.Chrome(service=service, options=options)
#
#     search_url = f"https://www.researchgate.net/search/publication?q={query}"
#     driver.get(search_url)
#     time.sleep(5)
#
#     results = []
#     articles = driver.find_elements(By.CLASS_NAME, "nova-legacy-v-publication-item__title")[:max_results]
#
#     for article in articles:
#         title = article.text
#         link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
#         results.append({"title": title, "link": link})
#
#     driver.quit()
#     return results


# --- Main Execution ---
def main():
    keywords = ['cyber deception', 'genai', 'cyber deception AND genai', '\"cyber deception\" AND \"LLM\"']

    for keyword in keywords:
        print(f"\n=== Google Scholar Results for '{keyword}' ===")
        gs_results = search_google_scholar(keyword)
        for res in gs_results:
            print(json.dumps(res, indent=4))

        print(f"\n=== CrossRef Results for '{keyword}' ===")
        cr_results = search_crossref(keyword)
        for res in cr_results:
            print(json.dumps(res, indent=4))

        print(f"\n=== Semantic Scholar Results for '{keyword}' ===")
        ss_results = search_semantic_scholar(keyword)
        for res in ss_results:
            print(json.dumps(res, indent=4))
        print("Number of Paper Scraped: ", len(ss_results))

        # print(f"\n=== ResearchGate Results for '{keyword}' ===")
        # rg_results = search_researchgate(keyword)
        # for res in rg_results:
        #     print(json.dumps(res, indent=4))


if __name__ == "__main__":
    main()
