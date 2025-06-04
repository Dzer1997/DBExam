import redis

r = redis.Redis(host='localhost', port=6379, db=0)

r.set("mykey", "hej")
print(r.get("mykey"))  # Skal printe: b'hej'
