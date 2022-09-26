import requests

end_url = "https://api.themoviedb.org/3/search/movie?"

parameters = {
    'api_key': 'dd38301a9d19bf8e75c76d23824358b6',
    'query': 'The matrix'
}

url_path = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"
response = requests.get(f'https://api.themoviedb.org/3/movie/500?api_key=dd38301a9d19bf8e75c76d23824358b6').json()
print(response["title"])
year = response["release_date"][0:4]
print(response["overview"])
url = url_path + response["poster_path"]
print(url)

