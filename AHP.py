from random import randint
import string

import numpy as np
from sklearn.preprocessing import normalize

import pandas as pd

from flask import Flask, Response, jsonify, request
from json import JSONEncoder
import json

import copy


#Variables Globales
CALORIAS_DESAYUNO        =   0
CALORIAS_MERIENDA_DIA    =   0
CALORIAS_ALMUERZO        =   0
CALORIAS_MERIENDA_TARDE  =   0
CALORIAS_CENA            =   0

#Variables de platos por horario
DESAYUNOS       = []
ALMUERZOS       = []
CENAS           = []
MERIENDAS_DIA   = []
MERIENDAS_TARDE = []

#Variables de platos por region
DESAYUNOS_REGION       = []
ALMUERZOS_REGION       = []
CENAS_REGION           = []
MERIENDAS_DIA_REGION   = []
MERIENDAS_TARDE_REGION = []


#Variables de platos por alergias
DESAYUNOS_ALERGIAS       = []
ALMUERZOS_ALERGIAS       = []
CENAS_ALERGIAS           = []
MERIENDAS_DIA_ALERGIAS   = []
MERIENDAS_TARDE_ALERGIAS = []

#Variables de platos por preferencias
DESAYUNOS_PREFERENCIAS       = []
ALMUERZOS_PREFERENCIAS       = []
CENAS_PREFERENCIAS           = []
MERIENDAS_DIA_PREFERENCIAS   = []
MERIENDAS_TARDE_PREFERENCIAS = []



#Matrices
MATRIZ_COMPARACION_CRITERIOS = []

#Valores de los pesos
PESO_UNO = 1
PESO_TRES = 3
PESO_CINCO = 5
PESO_SIETE = 7

#Valores NRI
N_RI  = {
        1 : 0,
        2 : 0,
        3 : 0.58,
        4 : 0.9,
        5 : 1.12,
}

#Datos nutricionales de las dietas generadas
DATOS_NUTRICIONALES_DIETAS = []

#INGREDIENTES
INGREDIENTES = set()

class DishesEnconder(JSONEncoder):
    def default(self, obj):
        return obj.__dict__  
        
class Dishes:
    nombre = "" 
    proteinas = 0.0  
    grasas = 0.0
    carbohidratos = 0.0
    ingredientes = []
    horario = []
    region = []
    calorias_totales = 0.0
    porcion_gramos = 100

    def __init__(self, nombre, proteinas, grasas, carbohidratos, ingredientes, calorias_totales, horario, region):
        self.nombre = nombre
        self.proteinas = proteinas
        self.grasas = grasas
        self.carbohidratos = carbohidratos
        self.ingredientes = ingredientes
        self.horario = horario
        self.region = region
        self.calorias_totales = calorias_totales
        self.porcion_gramos = 100
        
    def __iter__(self):
        yield from {
            "nombre": self.nombre,
            "proteinas": self.proteinas,
            "grasas": self.grasas,
            "carbohidratos": self.carbohidratos,
            "ingredientes": self.ingredientes,
            "horario": self.horario,
            "region": self.region,
            "calorias_totales": self.calorias_totales,
            "porcion_gramos": self.porcion_gramos
        }.items()
    
    def set_porcion_gramos(self, porcion_gramos):
        self.porcion_gramos = porcion_gramos

    def __str__(self):
        return json.dumps(dict(self), cls=DishesEnconder, ensure_ascii=False)

    def __repr__(self):
        return self.__str__()


class DishesResponse:
    nombre = "" 
    proteinas = 0.0  
    grasas = 0.0
    carbohidratos = 0.0
    ingredientes = []
    horario = ""
    region = ""
    calorias_totales = 0.0
    porcion_gramos = 100
    
    def __init__(self, nombre,proteinas, grasas,carbohidratos, ingredientes, calorias_totales, horario, region):
        self.nombre = nombre
        self.proteinas = proteinas
        self.grasas = grasas
        self.carbohidratos = carbohidratos
        self.ingredientes = ingredientes
        self.horario = horario
        self.region = region
        self.calorias_totales = calorias_totales
        self.porcion_gramos = 100
  
def leer_platos(platos: list):
    global INGREDIENTES

    url = "https://res.cloudinary.com/hv3n04p6e/raw/upload/v1647405791/platos_zk8i5u.csv"
    #url = "platos.csv"

    df = pd.read_csv(url, sep=';',encoding='utf8')

    for i in range(len(df)):
            p_nombre            = df.iat[i,0]
            p_proteinas         = float(df.iat[i,1])
            p_grasa             = float(df.iat[i,2])
            p_carbohidratos     = float(df.iat[i,3])
            p_ingredientes      = list(df.iat[i,4].split("-"))
            p_horario           = list(df.iat[i,5].split("-"))
            p_region            = list(df.iat[i,6].split("-"))
            p_calorias_totales  =  (p_proteinas * 4) + (p_grasa * 9) + (p_carbohidratos * 4)
            platos.append(Dishes(p_nombre, p_proteinas, p_grasa, p_carbohidratos, p_ingredientes , round(p_calorias_totales), p_horario, p_region))
            for item in p_ingredientes:
                INGREDIENTES.add(item)
               

def seccionar_tipos_de_platos(platos: list):
    global DESAYUNOS
    global ALMUERZOS
    global CENAS
    global MERIENDAS_DIA
    global MERIENDAS_TARDE

    DESAYUNOS = []
    ALMUERZOS = []
    CENAS = []
    MERIENDAS_DIA = []
    MERIENDAS_TARDE = []

    for item in platos:
        aux = copy.deepcopy(item)
        if('DESAYUNO' in item.horario):
            aux.horario = "DESAYUNO"
            DESAYUNOS.append(copy.deepcopy(aux))
        if('MERIENDA_DIA' in item.horario):
            aux.horario = "MERIENDA_DIA"
            MERIENDAS_DIA.append(copy.deepcopy(aux))
        if('ALMUERZO' in item.horario):
            aux.horario = "ALMUERZO"
            ALMUERZOS.append(copy.deepcopy(aux))
        if('MERIENDA_TARDE' in item.horario):
            aux.horario = "MERIENDA_TARDE"
            MERIENDAS_TARDE.append(copy.deepcopy(aux))
        if('CENA' in item.horario):
            aux.horario = "CENA"
            CENAS.append(copy.deepcopy(aux))

def obtener_platos_de_region(region: string):
    global DESAYUNOS_REGION
    global ALMUERZOS_REGION
    global CENAS_REGION
    global MERIENDAS_DIA_REGION
    global MERIENDAS_TARDE_REGION

    DESAYUNOS_REGION = []
    ALMUERZOS_REGION = []
    CENAS_REGION = []
    MERIENDAS_DIA_REGION = []
    MERIENDAS_TARDE_REGION = []

    for item in DESAYUNOS:
        if(region in item.region):
            DESAYUNOS_REGION.append(item)
    for item in MERIENDAS_DIA:
        if(region in item.region):
            MERIENDAS_DIA_REGION.append(item)
    for item in ALMUERZOS:
        if(region in item.region):
            ALMUERZOS_REGION.append(item)
    for item in MERIENDAS_TARDE:
        if(region in item.region):
            MERIENDAS_TARDE_REGION.append(item)
    for item in CENAS:
        if(region in item.region):
            CENAS_REGION.append(item)
    return

def quitar_alergias(alergias: list):
    global DESAYUNOS_ALERGIAS
    global ALMUERZOS_ALERGIAS
    global CENAS_ALERGIAS
    global MERIENDAS_DIA_ALERGIAS
    global MERIENDAS_TARDE_ALERGIAS

    DESAYUNOS_ALERGIAS       = []
    ALMUERZOS_ALERGIAS       = []
    CENAS_ALERGIAS           = []
    MERIENDAS_DIA_ALERGIAS   = []
    MERIENDAS_TARDE_ALERGIAS = []

    for alergia in alergias:
        for plato in DESAYUNOS_REGION:
            if(alergia not in plato.ingredientes):
                DESAYUNOS_PREFERENCIAS.append(plato)
        for plato in ALMUERZOS_REGION:
            if(alergia not in plato.ingredientes):
                ALMUERZOS_ALERGIAS.append(plato)
        for plato in CENAS_REGION:
            if(alergia not in plato.ingredientes):
                CENAS_ALERGIAS.append(plato)
        for plato in MERIENDAS_DIA_REGION:
            if(alergia not in plato.ingredientes):
                MERIENDAS_DIA_ALERGIAS.append(plato)
        for plato in MERIENDAS_TARDE_REGION:
            if(alergia not in plato.ingredientes):
                MERIENDAS_TARDE_ALERGIAS.append(plato)

def filtrar_preferencias(preferencias: list):
    global DESAYUNOS_PREFERENCIAS
    global ALMUERZOS_PREFERENCIAS
    global CENAS_PREFERENCIAS
    global MERIENDAS_DIA_PREFERENCIAS
    global MERIENDAS_TARDE_PREFERENCIAS

    for preferencia in preferencias:
        for plato in DESAYUNOS_ALERGIAS:
            if(preferencia in plato.ingredientes):
                DESAYUNOS_PREFERENCIAS.append(plato)
        for plato in ALMUERZOS_ALERGIAS:
            if(preferencia in plato.ingredientes):
                ALMUERZOS_PREFERENCIAS.append(plato)
        for plato in CENAS_ALERGIAS:
            if(preferencia in plato.ingredientes):
                CENAS_PREFERENCIAS.append(plato)
        for plato in MERIENDAS_DIA_ALERGIAS:
            if(preferencia in plato.ingredientes):
                MERIENDAS_DIA_PREFERENCIAS.append(plato)
        for plato in MERIENDAS_TARDE_ALERGIAS:
            if(preferencia in plato.ingredientes):
                MERIENDAS_TARDE_PREFERENCIAS.append(plato)


def generar_dieta():
    dieta = []
    if(len(DESAYUNOS_PREFERENCIAS) > 4):
        print("Mas de 4 DESAYUNOS_PREFERENCIAS\n")
        dieta.append(DESAYUNOS_PREFERENCIAS[randint(0, len(DESAYUNOS_PREFERENCIAS)-1)])
    elif(len(DESAYUNOS_ALERGIAS) > 4):
        print("Menos de 4 DESAYUNOS_PREFERENCIAS\n")
        dieta.append(DESAYUNOS_ALERGIAS[randint(0, len(DESAYUNOS_ALERGIAS)-1)])
    elif(len(DESAYUNOS_REGION) > 4):
        print("Menos de 4 DESAYUNOS_ALERGIAS\n")
        dieta.append(DESAYUNOS_REGION[randint(0, len(DESAYUNOS_REGION)-1)])
    else:
        print("Menos de 4 DESAYUNOS_REGION\n")
        dieta.append(DESAYUNOS[randint(0, len(DESAYUNOS)-1)])

    if(len(MERIENDAS_DIA_PREFERENCIAS) > 4):
        print("Mas de 4 MERIENDAS_DIA_PREFERENCIAS\n")
        dieta.append(MERIENDAS_DIA_PREFERENCIAS[randint(0, len(MERIENDAS_DIA_PREFERENCIAS)-1)])
    elif(len(MERIENDAS_DIA_ALERGIAS) > 4):
        print("Menos de 4 MERIENDAS_DIA_PREFERENCIAS\n")
        dieta.append(MERIENDAS_DIA_ALERGIAS[randint(0, len(MERIENDAS_DIA_ALERGIAS)-1)])
    elif(len(MERIENDAS_DIA_REGION) > 4):
        print("Menos de 4 MERIENDAS_DIA_ALERGIAS\n")
        dieta.append(MERIENDAS_DIA_REGION[randint(0, len(MERIENDAS_DIA_REGION)-1)])
    else:
        print("Menos de 4 MERIENDAS_DIA_REGION\n")
        dieta.append(MERIENDAS_DIA[randint(0, len(MERIENDAS_DIA)-1)])


    if(len(ALMUERZOS_PREFERENCIAS) > 4):
        print("Mas de 4 ALMUERZOS_PREFERENCIAS\n")
        dieta.append(ALMUERZOS_PREFERENCIAS[randint(0, len(ALMUERZOS_PREFERENCIAS)-1)])
    elif(len(ALMUERZOS_ALERGIAS) > 4):
        print("Menos de 4 ALMUERZOS_PREFERENCIAS\n")
        dieta.append(ALMUERZOS_ALERGIAS[randint(0, len(ALMUERZOS_ALERGIAS)-1)])
    elif(len(ALMUERZOS_REGION) > 4):
        print("Menos de 4 ALMUERZOS_ALERGIAS\n")
        dieta.append(ALMUERZOS_REGION[randint(0, len(ALMUERZOS_REGION)-1)])
    else:
        print("Menos de 4 ALMUERZOS_REGION\n")
        dieta.append(ALMUERZOS[randint(0, len(ALMUERZOS)-1)])

    if(len(MERIENDAS_TARDE_PREFERENCIAS) > 4):
        print("Mas de 4 MERIENDAS_TARDE_PREFERENCIAS\n")
        dieta.append(MERIENDAS_TARDE_PREFERENCIAS[randint(0, len(MERIENDAS_TARDE_PREFERENCIAS)-1)])
    elif(len(MERIENDAS_TARDE_ALERGIAS) > 4):
        print("Menos de 4 MERIENDAS_TARDE_PREFERENCIAS\n")
        dieta.append(MERIENDAS_TARDE_ALERGIAS[randint(0, len(MERIENDAS_TARDE_ALERGIAS)-1)])
    elif(len(MERIENDAS_TARDE_REGION) > 4):
        print("Menos de 4 MERIENDAS_TARDE_REGION\n")
        dieta.append(MERIENDAS_TARDE_REGION[randint(0, len(MERIENDAS_TARDE_REGION)-1)])
    else:
        print("Menos de 4 MERIENDAS_TARDE_REGION\n")
        dieta.append(MERIENDAS_TARDE[randint(0, len(MERIENDAS_TARDE)-1)])


    if(len(CENAS_PREFERENCIAS) > 4):
        print("Mas de 4 CENAS_PREFERENCIAS\n")
        dieta.append(CENAS_PREFERENCIAS[randint(0, len(CENAS_PREFERENCIAS)-1)])
    elif(len(CENAS_ALERGIAS) > 4):
        print("Menos de 4 CENAS_PREFERENCIAS\n")
        dieta.append(CENAS_ALERGIAS[randint(0, len(CENAS_ALERGIAS)-1)])
    elif(len(CENAS_REGION) > 4):
        print("Menos de 4 CENAS_ALERGIAS\n")
        dieta.append(CENAS_REGION[randint(0, len(CENAS_REGION)-1)])
    else:
        print("Menos de 4 CENAS_REGION\n")
        dieta.append(CENAS[randint(0, len(CENAS)-1)])


    return dieta
 
def redonderADiez(x, base):
    return int(base * round(float(x)/base))

def redonderAEnteros(x):
    return int(round(float(x)))

def actualizar_data_por_porcion(dieta:list):
    porcion_g = CALORIAS_DESAYUNO / dieta[0].calorias_totales
    dieta[0].set_porcion_gramos (redonderADiez(porcion_g * dieta[0].porcion_gramos, 10))
    dieta[0].proteinas =        (redonderADiez(porcion_g * dieta[0].proteinas, 10))
    dieta[0].grasas =           (redonderADiez(porcion_g * dieta[0].grasas, 10))
    dieta[0].carbohidratos =    (redonderADiez(porcion_g * dieta[0].carbohidratos, 10))
    dieta[0].calorias_totales = (redonderADiez(porcion_g * dieta[0].calorias_totales, 10))
    print("Plato desayuno:")
    print(dieta[0])

    porcion_g = CALORIAS_MERIENDA_DIA / dieta[1].calorias_totales
    dieta[1].set_porcion_gramos (redonderADiez(porcion_g * dieta[1].porcion_gramos, 10))
    dieta[1].proteinas =        (redonderADiez(porcion_g * dieta[1].proteinas, 10))
    dieta[1].grasas =           (redonderADiez(porcion_g * dieta[1].grasas, 10))
    dieta[1].carbohidratos =    (redonderADiez(porcion_g * dieta[1].carbohidratos, 10))
    dieta[1].calorias_totales = (redonderADiez(porcion_g * dieta[1].calorias_totales, 10))
    print("Plato merienda día:")
    print(dieta[1])

    porcion_g = CALORIAS_ALMUERZO / dieta[2].calorias_totales
    dieta[2].set_porcion_gramos(redonderADiez(porcion_g * dieta[2].porcion_gramos, 10))
    dieta[2].proteinas =        (redonderADiez(porcion_g * dieta[2].proteinas, 10))
    dieta[2].grasas =           (redonderADiez(porcion_g * dieta[2].grasas, 10))
    dieta[2].carbohidratos =    (redonderADiez(porcion_g * dieta[2].carbohidratos, 10))
    dieta[2].calorias_totales = (redonderADiez(porcion_g * dieta[2].calorias_totales, 10))
    print("Plato almuerzo:")
    print(dieta[2])

    porcion_g = CALORIAS_MERIENDA_TARDE / dieta[3].calorias_totales
    dieta[3].set_porcion_gramos(redonderADiez(porcion_g * dieta[3].porcion_gramos, 10))
    dieta[3].proteinas =        (redonderADiez(porcion_g * dieta[3].proteinas, 10))
    dieta[3].grasas =           (redonderADiez(porcion_g * dieta[3].grasas, 10))
    dieta[3].carbohidratos =    (redonderADiez(porcion_g * dieta[3].carbohidratos, 10))
    dieta[3].calorias_totales = (redonderADiez(porcion_g * dieta[3].calorias_totales, 10))
    print("Plato merienda tarde:")
    print(dieta[3])

    porcion_g = CALORIAS_CENA / dieta[4].calorias_totales
    dieta[4].set_porcion_gramos(redonderADiez(porcion_g * dieta[4].porcion_gramos, 10))
    dieta[4].proteinas =        (redonderADiez(porcion_g * dieta[4].proteinas, 10))
    dieta[4].grasas =           (redonderADiez(porcion_g * dieta[4].grasas, 10))
    dieta[4].carbohidratos =    (redonderADiez(porcion_g * dieta[4].carbohidratos, 10))
    dieta[4].calorias_totales = (redonderADiez(porcion_g * dieta[4].calorias_totales, 10))
    print("Plato cena:")
    print(dieta[4])
    return ""

def hallar_diccionario(dieta:Dishes):
    datos = {}
    datos["proteinas"] = 0 
    datos["grasas"] = 0
    datos["carbohidratos"] = 0
    datos["calorias"] = 0
    for item in dieta:
        datos["proteinas"] = datos["proteinas"] + item.proteinas
        datos["grasas"] = datos["grasas"] + item.grasas
        datos["carbohidratos"] = datos["carbohidratos"] + item.carbohidratos
        datos["calorias"] = datos["calorias"] + item.calorias_totales
    #print(datos)
    return datos

#------------------------------------------------------------------------#
def validar_matriz_comparacion_criterios():
    global MATRIZ_COMPARACION_CRITERIOS
    MATRIZ_COMPARACION_CRITERIOS = np.array([[1      , 3               , 7  ],
                                            [1/3    , 1               , 5 ],
                                            [1/7    , 1/5             , 1  ]])


    normalizada = normalize(MATRIZ_COMPARACION_CRITERIOS, axis=0, norm='l1')

    global PONDERADO_MATRIZ_COMPARACION_CRITERIOS
    PONDERADO_MATRIZ_COMPARACION_CRITERIOS = np.mean(normalizada, axis=1)
    PONDERADO_MATRIZ_COMPARACION_CRITERIOS = PONDERADO_MATRIZ_COMPARACION_CRITERIOS.reshape(3,1)

    AxP_M = np.dot(MATRIZ_COMPARACION_CRITERIOS,PONDERADO_MATRIZ_COMPARACION_CRITERIOS)

    nmax = np.sum(AxP_M)
    n = np.shape(MATRIZ_COMPARACION_CRITERIOS)[0]

    ci = (nmax - n) / (n - 1)
    ri = N_RI[n]
    cr = ci / ri

    print("Matriz de comparación de criterios: \n", MATRIZ_COMPARACION_CRITERIOS, "\n")
    print("Matriz normalizada: \n", normalizada, "\n")
    print("Ponderado: \n", PONDERADO_MATRIZ_COMPARACION_CRITERIOS, "\n")
    print("AXP_M_: \n", AxP_M, "\n")
    print(np.sum(AxP_M))

    if(cr < 0,1):
        print("OK")   


def devolver_pesos(pesos:list): 
    nuevos_pesos = [0,0,0]
    i = 0
    while i < 3:
        menor = 999999
        idx = 0
        for item in pesos:
            if item < menor:
                menor = item
        if menor != 999999:
            idx = pesos.index(menor)
            pesos[idx] = 999999
            nuevos_pesos[idx] = PESO_SIETE - 2*i
            i = i + 1
    return nuevos_pesos    

def devolver_dieta_recomedada():

    matrices = []
    grasas = []
    carbohidratos = []
    proteinas = []

    for i in DATOS_NUTRICIONALES_DIETAS:
        grasas.append(i["grasas"])
        carbohidratos.append(i["carbohidratos"])
        proteinas.append(i["proteinas"])

    pesos_grasas = []
    for item in grasas:
        pesos_grasas.append(abs(GRASAS_RECOMENDADAS - item))
    print(pesos_grasas)

    nuevos_pesos_grasas = devolver_pesos(pesos_grasas)
    peso_2_a_1 = definir_pesos(nuevos_pesos_grasas[1], nuevos_pesos_grasas[0])
    peso_3_a_1 = definir_pesos(nuevos_pesos_grasas[2], nuevos_pesos_grasas[0])
    peso_3_a_2 = definir_pesos(nuevos_pesos_grasas[2], nuevos_pesos_grasas[1])


    matriz_criterio1 = np.array([[1              ,  peso_2_a_1        , peso_3_a_1  ],
                                [1/peso_2_a_1   , 1                  , peso_3_a_2 ],
                                [1/peso_3_a_1   , 1/peso_3_a_2       , 1  ]])

    print("-----------------Criterio 1: Grasas - Matriz----------------")
    print(matriz_criterio1)

    normalizada = normalize(matriz_criterio1,axis=0, norm='l1')
    matrices.append(normalizada)

    ponderado_grasas = np.mean(normalizada, axis=1)
    ponderado_grasas = ponderado_grasas.reshape(3,1)
    print("Ponderoado grasas: \n", ponderado_grasas, "\n")

    AxP_M = np.dot(matriz_criterio1, ponderado_grasas)

    nmax = np.sum(AxP_M)
    n = np.shape(MATRIZ_COMPARACION_CRITERIOS )[0]

    ci = ( nmax - n )/ (n - 1)
    ri = N_RI[n]
    cr = ci / ri
    if(cr < 0,1):
        print("Criterio grasas - OK")


    pesos_carbohidratos = []
    for item in carbohidratos:
        pesos_carbohidratos.append(abs(CARBOHIDRATOS_RECOMENDADOS - item))
    print(pesos_carbohidratos)
    nuevos_pesos_carbohidratos = devolver_pesos(pesos_carbohidratos)
    peso_2_a_1 = definir_pesos(nuevos_pesos_carbohidratos[1], nuevos_pesos_carbohidratos[0])
    peso_3_a_1 = definir_pesos(nuevos_pesos_carbohidratos[2], nuevos_pesos_carbohidratos[0])
    peso_3_a_2 = definir_pesos(nuevos_pesos_carbohidratos[2], nuevos_pesos_carbohidratos[1])


    matriz_criterio2 = np.array([[1              ,  peso_2_a_1        , peso_3_a_1  ],
                                [1/peso_2_a_1   , 1                  , peso_3_a_2 ],
                                [1/peso_3_a_1   , 1/peso_3_a_2       , 1  ]])

    print("-----------------Criterio 2: Carbohidratos - Matriz----------------")
    print(matriz_criterio2)


    normalizada = normalize(matriz_criterio2,axis=0, norm='l1')
    matrices.append(normalizada)


    ponderado_carbohidratos = np.mean(normalizada, axis=1)
    ponderado_carbohidratos = ponderado_carbohidratos.reshape(3,1)
    print("Ponderoado carbohidratos: \n", ponderado_carbohidratos, "\n")

    AxP_M = np.dot(matriz_criterio2, ponderado_carbohidratos)

    nmax = np.sum(AxP_M)
    n = np.shape(MATRIZ_COMPARACION_CRITERIOS)[0]

    ci = ( nmax - n )/ (n - 1)
    ri = N_RI[n]
    cr = ci / ri
    if(cr < 0,1):
        print("Criterio carbohidratos - OK")



    pesos_proteinas = []
    for item in proteinas:
        pesos_proteinas.append(abs(PROTEINAS_RECOMEDADAS - item))
    print(pesos_proteinas)
    nuevos_pesos_proteinas = devolver_pesos(pesos_proteinas)
    peso_2_a_1 = definir_pesos(nuevos_pesos_proteinas[1], nuevos_pesos_proteinas[0])
    peso_3_a_1 = definir_pesos(nuevos_pesos_proteinas[2], nuevos_pesos_proteinas[0])
    peso_3_a_2 = definir_pesos(nuevos_pesos_proteinas[2], nuevos_pesos_proteinas[1])

    matriz_criterio3 = np.array([[1              ,  peso_2_a_1        , peso_3_a_1  ],
                                [1/peso_2_a_1   , 1                  , peso_3_a_2 ],
                                [1/peso_3_a_1   , 1/peso_3_a_2       , 1  ]])

    print("-----------------Criterio 3: Proteinas - Matriz----------------")
    print(matriz_criterio3)


    normalizada = normalize(matriz_criterio3,axis=0, norm='l1')
    matrices.append(normalizada)


    ponderado_proteinas = np.mean(normalizada, axis=1)
    ponderado_proteinas = ponderado_proteinas.reshape(3,1)
    print("Ponderoado proteinas: \n", ponderado_proteinas, "\n")
    AxP_M = np.dot(matriz_criterio3, ponderado_proteinas)
    #print(AxP_M)
    nmax = np.sum(AxP_M)
    n = np.shape(MATRIZ_COMPARACION_CRITERIOS )[0]

    ci = ( nmax - n )/ (n - 1)
    ri = N_RI[n]
    cr = ci / ri
    if(cr < 0,1):
        print("Criterio proteinas - OK")

    matriz_final = np.hstack((ponderado_grasas, ponderado_carbohidratos, ponderado_proteinas))
    print(PONDERADO_MATRIZ_COMPARACION_CRITERIOS.reshape(1,3))
    print(matriz_final)


    dietas_recomedadas = []
    dieta_recomedada = 0

    for item in matriz_final:
        dietas_recomedadas.append(np.dot(PONDERADO_MATRIZ_COMPARACION_CRITERIOS.reshape(1,3), item))
    
    dietas_recomedadas = np.array(dietas_recomedadas)
    print(dietas_recomedadas)
    
    dieta_recomedada = np.where(dietas_recomedadas == dietas_recomedadas.max())[0][0]
    print("La mejor dieta es la dieta: " , dieta_recomedada + 1)
    print("Con un total de: ", dietas_recomedadas.max())

    return dieta_recomedada

def definir_pesos(peso1, peso2):
    peso = peso1 - peso2
    if peso < 0:
        peso = 1 / (abs(peso)+1)
    else:
        peso = peso + 1
    return peso

def calcular_valores_dieta(max_calorias: int, peso: int):
    global CALORIAS_DESAYUNO
    global CALORIAS_MERIENDA_DIA
    global CALORIAS_ALMUERZO
    global CALORIAS_MERIENDA_TARDE
    global CALORIAS_CENA

    CALORIAS_DESAYUNO        =   max_calorias * 0.30
    CALORIAS_MERIENDA_DIA    =   max_calorias * 0.05
    CALORIAS_ALMUERZO        =   max_calorias * 0.35
    CALORIAS_MERIENDA_TARDE  =   max_calorias * 0.05
    CALORIAS_CENA            =   max_calorias * 0.25

    
    global PROTEINAS_RECOMEDADAS
    global GRASAS_RECOMENDADAS
    global CARBOHIDRATOS_RECOMENDADOS

    PROTEINAS_RECOMEDADAS       = 0.9 * peso
    GRASAS_RECOMENDADAS         =  0.30 * max_calorias / 9
    CARBOHIDRATOS_RECOMENDADOS  = randint(100,150)

    print("Proteinas recomendadas: "        + str(PROTEINAS_RECOMEDADAS))
    print("Grasas recomendadas: "           + str(GRASAS_RECOMENDADAS))
    print("Carbohidratos recomendadas: "    + str(CARBOHIDRATOS_RECOMENDADOS) + "\n")

def recomendar_dieta(calorias_max, peso, region:string, alergias: list, preferencias: list):

    calcular_valores_dieta(calorias_max, peso)
    obtener_platos_de_region(region)
    if(len(alergias) > 0):
        quitar_alergias(alergias)

    if(len(preferencias) > 0):
        filtrar_preferencias(preferencias)
    

    dieta_generada  = generar_dieta()
    dieta_generada2 = generar_dieta()
    dieta_generada3 = generar_dieta()

    print("----------------Dieta 1:--------------------")
    actualizar_data_por_porcion(dieta_generada)
    print("----------------Dieta 2:--------------------")
    actualizar_data_por_porcion(dieta_generada2)
    print(":---------------Dieta 3:--------------------")
    actualizar_data_por_porcion(dieta_generada3)

    dietas = []
    dietas.append(dieta_generada)
    dietas.append(dieta_generada2)
    dietas.append(dieta_generada3)

    global DATOS_NUTRICIONALES_DIETAS
    DATOS_NUTRICIONALES_DIETAS = []

    DATOS_NUTRICIONALES_DIETAS.append(hallar_diccionario(dieta_generada))
    DATOS_NUTRICIONALES_DIETAS.append(hallar_diccionario(dieta_generada2))
    DATOS_NUTRICIONALES_DIETAS.append(hallar_diccionario(dieta_generada3))

    validar_matriz_comparacion_criterios()

    return dietas[devolver_dieta_recomedada()]

def get_platos_alternativos(calorias: int, horario: string):
    platos =  []
    for i in range(3):
        if(horario == "DESAYUNO"):
            platos.append(convertir_valores_por_calorias_especificas(DESAYUNOS[randint(0, len(DESAYUNOS)-1)], calorias))
        elif(horario == "MERIENDA_DIA"):
            platos.append(convertir_valores_por_calorias_especificas(MERIENDAS_DIA[randint(0, len(MERIENDAS_DIA)-1)], calorias))
        elif(horario == "ALMUERZO"):
            platos.append(convertir_valores_por_calorias_especificas(ALMUERZOS[randint(0, len(ALMUERZOS)-1)], calorias))   
        elif(horario == "MERIENDA_TARDE"):
            platos.append(convertir_valores_por_calorias_especificas(MERIENDAS_TARDE[randint(0, len(MERIENDAS_TARDE)-1)], calorias))
        elif(horario == "CENA"):
            platos.append(convertir_valores_por_calorias_especificas(CENAS[randint(0, len(CENAS)-1)], calorias))   
    return platos
    
def convertir_valores_por_calorias_especificas(dish:Dishes, calorias: int):
    newDish = dish
    factor = calorias / newDish.calorias_totales
    newDish.carbohidratos       = redonderAEnteros(newDish.carbohidratos * factor)
    newDish.grasas              = redonderAEnteros(newDish.grasas * factor)
    newDish.proteinas           = redonderAEnteros(newDish.proteinas * factor)
    newDish.calorias_totales    = redonderAEnteros(newDish.calorias_totales * factor)
    newDish.porcion_gramos      = redonderAEnteros(newDish.porcion_gramos * factor)
    return newDish


app = Flask(__name__)


@app.route('/diet-month', methods=['POST'])
def get_diet2():
    dietas = []
    request_data = request.get_json()
    calories = request_data['calories']
    weight =  request_data['weight']
    region = request_data['region']
    allergies = request_data['allergies']
    favorites = request_data['favorites']
    for i in range(30):
        dietas.append(recomendar_dieta(calories, weight, region, allergies, favorites))
    response =  dietas
    return Response(DishesEnconder().encode(response), mimetype='application/json')

@app.route("/alternatives", methods=['POST'])
def obtener_alternativas():
    request_data = request.get_json()
    calorias = request_data['calories']
    horario =  request_data['schedule']
    response = get_platos_alternativos(calorias, horario)
    return Response(DishesEnconder().encode(response), mimetype='application/json')

@app.route("/", methods=['GET'])
def hello():
    return Response("Hola...", mimetype='text/plain')

platos = []
leer_platos(platos)
seccionar_tipos_de_platos(platos)

if __name__  == '__main__':
    #1g de prote = 4kcal
    #1g de grasa = 9kcal
    #1g carbo = 4kcalc
    #Son porciones de 100g
    #print(sorted(INGREDIENTES))
    app.run()

