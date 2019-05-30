from flask import Flask
from flask import render_template,request,redirect,session,abort

import requests
import json
import os
app = Flask(__name__, template_folder = "templates")

## VARIABLES ##
keytraductor=os.environ['keytraductor']
keynutrientes=os.environ['keynutrientes']
constante = "raw"
lista = []
lista2 = []
traduct = ""
apitraductor = "https://translate.yandex.net/api/v1.5/tr.json/translate?"
apiid = 'https://api.nal.usda.gov/ndb/search/?'
apinutrientes = 'https://api.nal.usda.gov/ndb/V2/reports?'
urlrecipe = "http://www.recipepuppy.com/api/?"
lista_recetas = []
lista_ingredientes = []
lista_urls = []
lista_imagenes = []

## FUNCIONES ##

@app.route('/',methods=["GET","POST"])
def inicio():
    return render_template("index.html", error=None)

@app.route("/procesar", methods=["POST"])
def procesar_formulario():
    datos = request.form.get("mensaje")
    lista = datos.split("\r\n")
    parames = ""
    nutrientes = []
    lista1 = []
    # abcdario = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','Y','Z']
    for productos in lista:
        parames = parames + str(productos) + "/"

#########    REQUEST 1ª TRADUCCIÓN   ########
    payloadtraductor = {'lang':'es-en','key':keytraductor,'text':parames}
    r = requests.get(apitraductor,params = payloadtraductor)
#############################################

    if r.status_code == 200:
        traduccionprimera = r.json()
        for i in traduccionprimera['text']:
            for j in i.split("/"):
                j = j + " " + constante

#########    REQUEST BUSCAR ID ALIMENTO   ########
                payloadid = {'format':'json','ds':'Standard Reference','sort':'r','max':5,'offset':0,'api_key':keynutrientes,'q':j}
                v = requests.get(apiid,params=payloadid)
##################################################

                if v.status_code == 200:
                    identificadores = v.json()
                    id = identificadores["list"]["item"][0]["ndbno"]

#########    REQUEST BUSCAR ID ALIMENTO   ########

                    payloaddatos = {'type':'b','format':'json','api_key':keynutrientes,'ndbno':id}
                    u = requests.get(apinutrientes,params = payloaddatos)
##################################################

                    if u.status_code == 200:
                        documento = u.json()
                        for i in documento['foods'][0]['food']['nutrients']:

                            traduct = i['name'] + '/' + i['value'] + '/' + i['unit']

#########    REQUEST TRADUCIR DATOS NUTRIENTES   ########

                            payloadtraductor['text'] = traduct
                            payloadtraductor['lang'] = 'en-es'
                            x = requests.get(apitraductor,params = payloadtraductor)

#########################################################

                            if x.status_code == 200:
                                result = x.json()
                                for i in result['text']:
                                    nutrientes.append(i.split("/")[0].replace("El ","").replace("De ","").replace("La ","").upper() + "/" + i.split("/")[1] + "/" + i.split("/")[2])
                            else:
                                abort(404)

                        lista2.append(nutrientes)
                        nutrientes = []
                    else:
                        abort(404)
                else:
                    abort(404)
        return render_template("resultado.html", lista = lista, lista2 = lista2)

    else:
        abort(404)



@app.route("/recetas", methods=['POST'])
def procesar_recetas():

# LISTA DE COMPRA BIEN PUESTA
    lsin = []
    quitar = ["de ","la ","el ","las ","los"]
    recipe = ""
    receta = ""
    lista_recetas = []
    lista_ingredientes = []
    lista_urls = []
    lista_imagenes = []
    lista = request.form.get("recipes")
    lista = lista.replace("[","").replace("]","").replace(" ","").replace("'","")
    for i in lista.split(","):
        if lista.split(",").index(i) == (len(lista.split(",")) -1):
            receta = receta + str(i)
        else:
            receta = receta + str(i) + ","

#########    REQUEST TRADUCIR LISTA DE LA COMPRA  ###########

    payloadtraductor = payloadtraductor = {'lang':'es-en','key':keytraductor,'text':receta}
    trad = requests.get(apitraductor,params = payloadtraductor)

    if trad.status_code == 200:
        doc7 = trad.json()
        for j in doc7["text"]:
            recipe = str(j)

#########    REQUEST RECETAS CON LOS INGREDIENTES  ############

            payloadrecipe = {'p':'5','i':recipe}
            rec = requests.get(urlrecipe, params = payloadrecipe)

            if rec.status_code == 200:
                doc6 = rec.json()
                for i in doc6["results"]:

                    lista_recetas.append(str(i["title"]))

                    lista_urls.append(str(i["href"]))

                    lista_imagenes.append(str(i["thumbnail"]))

                    payloadtraductor['lang'] = "en-es"
                    payloadtraductor['text'] = str(i["ingredients"])

                    trad = requests.get(apitraductor,params = payloadtraductor)

                    if trad.status_code == 200:

                        doc7 = trad.json()

                        for ing in doc7["text"]:
                            for palabra in quitar:
                                if ing.startswith(palabra):
                                    lsin.append(ing[len(palabra):])
                                else:
                                    lsin.append(ing)

                            #append(str(j).title().replace("La ","").replace("El ","").replace("Las ","").replace("Los ",""))
                    else:
                        abort(404)
            else:
                abort(404)
        return render_template("recetas.html", lista_urls = lista_urls, lista_recetas = lista_recetas, lista_ingredientes = lsin, lista_imagenes = lista_imagenes)
    else:
        abort(404)


if __name__=='__main__':	
    app.run(debug = True)
