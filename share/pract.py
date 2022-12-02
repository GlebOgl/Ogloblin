import requests

url ='https://api.github.com/search/repositories?q=private:C#&sort=stars'
res = requests.get(url)
r_dict = res.json()
#print("сколько репозиториев",r_dict['total_count'])

items = r_dict["items"]
print("Всего - ", len(items))
for i in items:
    print(f"{i['id']} - {i['full_name']}")

for i in items:
    if i["has_wiki"] and i["has_downloads"] and i["allow_forking"]:
        print("Login:", i["owner"]["login"])
        print("URL:", i["url"])
        print("forks:", i["forks"])
        print(" ")
        #ищет репозитории на языке С# с документацией и загрузками, который можно скопировать
        #и возвращает логин владельца и количество форков
