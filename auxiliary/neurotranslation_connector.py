import requests

DEBUG = True

try:
    while True:
        r = requests.post("https://api.tartunlp.ai/translation/v2",
                          json={"text": input("Sisesta sõnum: "),
                                "tgt": "eng",
                                "src": "est"})

        translated_msg = r.json()['result']
        if DEBUG:
            print("----- DEBUG-TRANSLATED_MSG:", translated_msg)
        # print("Translation: ", translated_msg)

        r2 = requests.post(url="http://127.0.0.1:8080/webhook",
                           json={"message": translated_msg,
                                 "sender": 1337})

        for response in eval(r2.content.decode("utf-8")):
            if DEBUG:
                print("----- DEBUG-RESPONSE:", response["text"])
            r3 = requests.post("https://api.tartunlp.ai/translation/v2",
                               json={"text": response["text"],
                                     "tgt": "est",
                                     "src": "eng"})
            print(r3.json()["result"])


except KeyboardInterrupt:
    print("Edu!")
