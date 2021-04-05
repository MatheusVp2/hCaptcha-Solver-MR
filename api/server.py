from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from imageai.Detection import ObjectDetection # Detecção dos Objetos
import cv2
import numpy as np


from controller import saveImage, randomName
import json
import os
import requests



app   = Flask(__name__)
CORS(app, resources={ r"/*": { "origins" : "*" } })

# Inicia a Lib de Detecção de Imagens
DETECTOR = ObjectDetection()
DETECTOR.setModelTypeAsYOLOv3()
DETECTOR.setModelPath( "../yolo.h5" )
DETECTOR.loadModel(detection_speed="flash")


@app.route( '/v1/detection', methods = ['POST'] )
def v1_detection():

    url_image = request.json.get('url')

    if not url_image:
        json_resp = {
            'ok' : False,
            'msg' : 'Não encontrado url',
            'data' : None
        }
        return Response( response=json.dumps(json_resp), mimetype='application/json', status=200 )

    
    name = randomName()
    path_image = saveImage(url_image, name)

    detections = DETECTOR.detectObjectsFromImage(input_image=path_image, output_image_path='./nova/teste.jpg')
    list_name_detections = list(map(lambda x: x['name'], detections))

    os.remove(path_image)
    

    json_resp = {
        'ok' : True,
        'msg': 'Analise',
        'data' : list_name_detections
    }
    return Response( response=json.dumps(json_resp), mimetype='application/json', status=200 )






@app.route( '/v2/detection', methods = ['POST'] )
def v2_detection():
    url_image = request.json.get('url')

    if not url_image:
        json_resp = {
            'ok' : False,
            'msg' : 'Não encontrado url',
            'data' : None
        }
        return Response( response=json.dumps(json_resp), mimetype='application/json', status=200 )

    image = requests.get(url_image)
    nparr = np.frombuffer(image.content, np.uint8)
    im    = cv2.imdecode(nparr, flags=1)
    detected_image, detections = DETECTOR.detectObjectsFromImage(input_image=im, input_type="array", output_type="array")
    list_name_detections = list(map(lambda x: x['name'], detections))

    json_resp = {
        'ok' : True,
        'msg': 'Analise',
        'data' : list_name_detections
    }
    return Response( response=json.dumps(json_resp), mimetype='application/json', status=200 )


if __name__ == '__main__':
    app.run( debug=False )