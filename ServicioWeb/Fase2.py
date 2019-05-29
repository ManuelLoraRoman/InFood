
import requests

import os

#export keyprueba=lUgddO70hhfm4CCp5WycOz1IdhUbfcbjI7vZ1iEA
#key=os.environ["keyprueba"]

constante = "raw"
lista=[]
k = 1
parames = ""
nutrientes = ""
traduct = ""
textotraductor = ""
textotraducido = ""

alimento = str(input("¿Qué alimento deseas añadir a tu lista de la compra?"))
lista.append(alimento)
opcion = str(input("¿Deseas incluir otro producto?('S/N')"))

while opcion == "S" or opcion == "s":

    alimento = str(input("¿Qué alimento deseas añadir a tu lista de la compra?"))
    lista.append(alimento)
    opcion = str(input("¿Deseas incluir otro producto?('S/N')"))
    if opcion == "N" or opcion == "n":
        break;

cadena = "Tu lista de la compra es:"
for i in lista:
    cadena = cadena + "\n" + str(k) + ". " + str(i)
    k = k + 1
print(cadena)

print("\nTRADUCTOR")
print("---------")

for i in lista:
    if lista.index(i) == (len(lista) - 1):
        parames = parames + str(i)
    else:
        parames = parames + str(i) + "/"

payloadtraductor = {'lang':'es-en','key':'trnsl.1.1.20190513T121145Z.b8e8808123ec0a8c.e500bffc714ef1e8544f1eb7f8a452ed56379c23','text':cadena}
apitraductor = "https://translate.yandex.net/api/v1.5/tr.json/translate?"
r=requests.get(apitraductor,params=payloadtraductor)

if r.status_code == 200:
    doc=r.json()
    for i in doc["text"]:
        textotraductor = textotraductor + i
    print(textotraductor)

payloadtraductor['text'] = parames
t=requests.get(apitraductor,params=payloadtraductor)

if t.status_code == 200:
    doc2 = t.json()
    for i in doc2["text"]:
        for j in i.split("/"):
            print("\nNUTRIENTES DE " + j.upper())
            print("-----------------------------------")
            j = j + " " + constante
            payloadid = {'format':'json','ds':'Standard Reference','sort':'r','max':5,'offset':0,'api_key':'lUgddO70hhfm4CCp5WycOz1IdhUbfcbjI7vZ1iEA','q':j}
            v=requests.get('https://api.nal.usda.gov/ndb/search/?',params=payloadid)
            if v.status_code == 200:
                doc3 = v.json()
                id = doc3["list"]["item"][0]["ndbno"]
                payloaddatos = {'type':'b','format':'json','api_key':'lUgddO70hhfm4CCp5WycOz1IdhUbfcbjI7vZ1iEA','ndbno':id}
                u=requests.get('https://api.nal.usda.gov/ndb/V2/reports?',params=payloaddatos)
                if u.status_code == 200:
                    doc4 = u.json()
                    for i in doc4["foods"][0]["food"]["nutrients"]:
                        traduct = i["name"] + "/" + i["value"] + "/" + i["unit"]
                        payloadtraductor['text'] = traduct
                        payloadtraductor['lang'] = 'en-es'
                        x = requests.get(apitraductor,params=payloadtraductor)
                        if x.status_code == 200:
                            doc5 = x.json()
                            for i in doc5["text"]:
                                print("\nNombre: " + i.split("/")[0].replace("El ","").replace("De ","").replace("La ","").capitalize() + "\nValor: " + i.split("/")[1] + " " + i.split("/")[2] + "\n")




    opcion = str(input("¿Quieres algunas recetas para dichos alimentos?('S'/'N')"))
    if opcion == "S" or opcion == "s":
        urlrecipe = "http://www.recipepuppy.com/api/?"
        recipe = ""
        for i in doc2["text"]:
            for j in i.split("/"):
                if i.split("/").index(j) == (len(i.split("/")) - 1):
                    recipe = recipe + str(j)
                else:
                    recipe = recipe + str(j) + ","


                    
        payloadrecipe = {'p':'5','i':recipe}
        rec = requests.get(urlrecipe,params = payloadrecipe)
        doc6 = rec.json()
        print("RECETAS")
        print("-----------")
        for i in doc6["results"]:
            payloadtraductor['lang'] = 'en-es'
            payloadtraductor['text'] = str(i["title"])
            re = requests.get(apitraductor,params=payloadtraductor)
            if re.status_code == 200:
                doc7 = re.json()
                for j in doc7["text"]:
                    print("Nombre: " + str(j))
                payloadtraductor['text'] = str(i["ingredients"])
                re = requests.get(apitraductor,params=payloadtraductor)
                if re.status_code == 200:
                    doc7 = re.json()
                    for j in doc7["text"]:
                        print("Ingredientes: " + str(j))
                print("Pasos a seguir: " + str(i["href"] + "\n"))
