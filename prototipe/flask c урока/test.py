from requests import get, post, delete

print(delete('http://localhost:8080/api/news/8').json())