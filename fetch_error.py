import urllib.error
import urllib.request

try:
    urllib.request.urlopen("http://127.0.0.1:8001/accounts/login/")
except urllib.error.HTTPError as e:
    with open("error.html", "w", encoding="utf-8") as f:
        f.write(e.read().decode())
