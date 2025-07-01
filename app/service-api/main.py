import random
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from service API"

@app.route("/name")
def random_name ():

    list1 = ['a', 'e', 'y', 'u', 'o', 'a', 'i', 'o']
    list2 = ['w', 'r','t','p','s','d','f','g','h','m','v','k','n']

    renge_num = random.randint(2, 7)

    name = ''

    flag = random.randint(0, 1)

    for i in range(renge_num):
        if flag:
            later = random.randint(0, len(list1) - 1)
            name += list1[later]

            flag = random.randint(0, 10)
            if flag > 4:
                flag=0 

        else:
            later = random.randint(0, len(list2) - 1)
            name += list2[later]

            flag = random.randint(0, 10)
            if flag > 4:
                flag=1

    return name[0].upper() + name[0::]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)