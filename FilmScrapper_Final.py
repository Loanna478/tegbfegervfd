import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures
import re

def get_movie_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    movies = soup.find_all('div', class_='short')

    movie_info = []

    for movie in movies:
        title = movie.find('a', class_='short-poster').get('alt')
        movie_link = movie.find('a', class_='short-poster').get('href')
        image_url = movie.find('a', class_='short-poster').find('img').get('data-src')

        # Ajouter les informations du film à la liste
        movie_info.append({'title': title, 'image': image_url, 'link': f"https://fs33.lol/{movie_link}", 'linkvideo': None, 'description': None})

    return movie_info

def get_french_movie_link(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', id='gGotop', href=True)
    french_link = None

    for link in links:
        if 'FRENCH' in link.text:
            if 'uqload' in link.get('href'):
                print(f"Le lien français du film {url} a été trouvé.")
                french_link = link.get('href')
                break

    return french_link

def get_movie_description(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    description_div = soup.find('div', class_='fdesc clearfix slice-this', id='s-desc')
    
    if description_div:
        description = description_div.get_text(strip=True)
        # Utiliser une expression régulière pour enlever la partie non désirée
        cleaned_description = re.sub(
            r"^regarder ou telecharger le film .+ en streaming complet hd vf et vostfr replay gratuit vod sans limite et sans inscrption compatible chrome cast sur mobile tablette pc console",
            "", 
            description
        ).strip()
        return cleaned_description

    return None

def main():
    num_pages = int(input("Combien de pages voulez-vous prendre ? "))

    # Extraction des informations des films
    base_url = "https://fs33.lol/films/page/"
    all_movie_info = []

    for page_num in range(1, num_pages + 1):
        url = base_url + str(page_num) + "/"
        print(f"Extraction des informations de la page {page_num}...")

        movie_info = get_movie_info(url)

        for movie in movie_info:
            # Utilisation de ThreadPoolExecutor pour obtenir la description et le lien vidéo en parallèle
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_description = executor.submit(get_movie_description, movie['link'])
                future_french_link = executor.submit(get_french_movie_link, movie['link'])

                movie['description'] = future_description.result()
                movie['linkvideo'] = future_french_link.result()

            # Ajouter les informations du film à la liste
            all_movie_info.append(movie)

    # Enregistrement des informations dans un fichier JSON
    with open('films.json', 'w', encoding='utf-8') as file:
        json.dump(all_movie_info, file, ensure_ascii=False, indent=4)

    print("Le script a terminé l'extraction des informations des films.")

if __name__ == "__main__":
    main()
