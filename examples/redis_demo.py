import redis


r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

r.set("name","koko")

print(r.get("name"))

r.set(
    "code",
    "123456",
    ex=60,
)

print(r.get("code"))
print(r.ttl("code"))

