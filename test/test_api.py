import requests
from hashlib import sha1
import time
import json

url = "http://localhost:5005/user/update?id=1&q=foo"
# url = "http://localhost:5005/user/update?q=foo"
s1 = sha1()
uri="/user/update"
app_id ="3S2a6b1E"
secret = "19e31d2e32a6619e"
timestamp = str(int(time.time()))

en_str = uri+app_id+timestamp+secret


s1.update(en_str.encode("utf-8"))
sign = s1.hexdigest()

print(timestamp,sign)
post_fields = {
  "ui": {
    "username": "string",
    "password": "string",
    "email": "user@example.com",
    "full_name": "string",
    "age": 10,
    "sex": 10
  },
  "uo": {
    "username": "string",
    "password": "string",
    "email": "user@example.com",
    "full_name": "string",
    "age": 11,
    "sex": 10,
    "menus": [
      {
        "name": "string",
        "uri": "string"
      }
    ]
  },
  "id2": 0
}
h = {"x-auth-appid":app_id,"x-auth-sign":sign,"x-auth-timestamp":timestamp,"Content-Type": "application/json"}
t1 = time.time()
result = requests.post(url, data=json.dumps(post_fields),headers=h)
# result = requests.post(url, data=post_fields,headers=h)
print(time.time()-t1)
print(result.status_code,result.text)

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTYzODI1ODc2Mn0.r_I0OLT1RWU2ifKVK2JBnfi-tM0wgJWZFdMG9RNqrKA"
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTYzODI2MTIyN30.Tgrvihr9yBUZSjFchVmMrcerq3MBHCftJNXoCWixMxU"
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTYzODI1OTA4MH0.l9m9swgA5UyLdph6yTz9ysl2dtyH-MRRBq6dkJcTvb0"
token = "e.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTYzODI1OTA4MH0.l9m9swgA5UyLdph6yTz9ysl2dtyH-MRRBq6dkJcTvb0"
h1 = {"x-auth-token":token}
r = requests.get("http://localhost:5005/user/user/?user_id=1&name=1&sex=1&age=0",headers=h1).json()
print(r)
print(time.time()-t1)


