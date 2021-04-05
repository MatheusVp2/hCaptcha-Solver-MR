import requests
from random import randrange
import os

def saveImage(url, nome):
    path = './img/'
    path_image = path + nome + '.jpg'
    response = requests.get(url, verify=False)
    with open(path_image, 'wb') as fs:
        fs.write(response.content)
    return path_image


def randomName():
    rand = ""
    numeros = "0123456789"
    tamNumeros = len(numeros)
    for i in range(tamNumeros):
        num_rand = randrange(0, tamNumeros)
        rand += numeros[num_rand]
    return rand


