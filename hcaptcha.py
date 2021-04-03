
from selenium import webdriver  # Drive Selenium
from selenium.webdriver.chrome.options import Options  # Options do Chrome
from selenium.webdriver.support.ui import WebDriverWait  # Espera de carregamento

from imageai.Detection import ObjectDetection # Detecção dos Objetos

from my_logger import print_erro, print_fail, print_info, print_key, print_pass, print_time

import requests
import json
import time
import os


# Variaveis Globais
HEADERS = {
    'authority': 'hcaptcha.com',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://assets.hcaptcha.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9'
}

HEADERS_SUBMIT = {
    'authority': 'hcaptcha.com',
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://assets.hcaptcha.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9'
}

requests.packages.urllib3.disable_warnings()
SESSAO_REQUESTS = requests.session()
SESSAO_REQUESTS.verify  = False
SESSAO_REQUESTS.headers = HEADERS

# Classe do Script
class hCaptcha():

    def __init__(self, site_key, site_host):
        # Variaveis Privadas
        
        # Pastas da Imagens, função analisando com as imagens baixadas
        self.__path_images = './img/'
        self.__path_images_detections = './img_detections/'

        # Cria pasta se não existir / Breve refatorado para função sem baixar as imagens
        self.__create_path_if_not_exists()

        # Inicialização para a API do hcaptcha
        self.__site_key  = site_key
        self.__site_host = site_host
        
        # Reaproveitamento de Codigo
        self.__reset_init()

        # Inicia a Lib de Detecção de Imagens
        self.__detector = ObjectDetection()
        self.__detector.setModelTypeAsYOLOv3()
        self.__detector.setModelPath( "yolo.h5" )
        self.__detector.loadModel(detection_speed="flash")
    

    def __reset_init(self):
        # Variaveis para resposta do hCaptcha
        self.__builder = {}
        self.__payload   = None
        self.__c       = None
        self.__n       = None
        self.__key     = None
        
        # Response UUID do hCaptcha
        self.__uuid = None

        # Verificação do Tempo de Execução da Aplicação
        self.__start_time  = None
        self.__finish_time = None

    # Funções auxiliares
    def __create_path_if_not_exists(self):
        if not os.path.exists( self.__path_images ):
            os.mkdir( self.__path_images )
        if not os.path.exists( self.__path_images_detections ):
            os.mkdir( self.__path_images_detections )

    def __save_images(self, url, taskkey):
        path_image = f"{ self.__path_images }{ taskkey }.jpg"
        response = requests.get(url)
        with open( path_image, 'wb' ) as fs:
            fs.write(response.content)
    
    def __remove_images_from_folder(self):
        print_info( 'Removendo imagens das pastas ...' )
        for imagens in os.listdir( self.__path_images ):
            os.remove(self.__path_images + imagens)
        path_nova = "./nova/"
        for detections in os.listdir( self.__path_images_detections ):
            os.remove(self.__path_images_detections + detections)

    def __get_n_hsw_or_hsl(self, type, req):
        options = Options()
        options.headless = True
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=options)

        file = "hsw.js" if type == "hsw" else "hsl.js"
        function = f"hsw('{ req }')" if type == "hsw" else f"hsl('{ req }')"

        with open(file, "r") as f:
            return driver.execute_script(f.read() + f"return { function };")

    def __start_req_hcaptcha(self):
        url = 'https://hcaptcha.com/checksiteconfig'
        params = {
            'host': self.__site_host,
            'sitekey': self.__site_key,
            'sc': '1',
            'swa': '1'
        }
        response = SESSAO_REQUESTS.get(url, params=params)
        return response.json()

    def __get_payload(self):
        url  = 'https://hcaptcha.com/getcaptcha'
        data = {
            'host': self.__site_host,
            'sitekey': self.__site_key,
            'hl'        : 'en',
            'motionData': '{}',
            'n': self.__n,
            'c': json.dumps( self.__c ).replace("'", '"')
        }
        response = SESSAO_REQUESTS.post( url , data=data )
        return response.json()
    
    def __is_correct_v2( self, obj, taskkey ):

        path_image     = f"{self.__path_images}{taskkey}.jpg"
        path_detection = f"{self.__path_images_detections}{taskkey}.jpg"

        detections = self.__detector.detectObjectsFromImage( input_image=path_image, output_image_path=path_detection)
        list_name_detections = list(map(lambda x: x['name'], detections))

        if obj.lower() in list_name_detections:
            print_info( f'{taskkey}.jpg is a {obj}' )
            self.__builder['answers'][taskkey] = 'true'
            return
        else:
            print_info( f'{taskkey}.jpg is not a {obj}' )
            self.__builder['answers'][taskkey] = 'false'
            return
    
    def submit(self):
        url      = f'https://hcaptcha.com/checkcaptcha/{self.__key}'

        params={
            's' : self.__site_key
        }

        response = SESSAO_REQUESTS.post( url, data=json.dumps( self.__builder ), params=params, headers=HEADERS_SUBMIT )

        if response.json()['pass']:
            print_pass("hCaptcha has been solved...")
            self.__uuid = response.json()['generated_pass_UUID']
            print_key(self.__uuid)
        else:
            print_fail("Retrying...")
            return
            return self.ResolverCaptcha()

    def __detections_images(self):
        print_info("Received Images ...")
        print_info(f'{ len( self.__payload["tasklist"] ) } images retrieved ...')

        self.__key = self.__payload['key']
        obj = self.__payload['requester_question']['en'].split(' ')[-1].replace("motorbus", "bus")
        print_info(f'Object Analyzing [{obj.upper()}]')

        # self.__builder['v']            = "8ac1d9d"
        self.__builder['job_mode']     = 'image_label_binary'
        self.__builder['answers']      = {}
        self.__builder['serverdomain'] = self.__site_host
        self.__builder['sitekey']      = self.__site_key
        self.__builder['motionData']   = '{"st":' + str(int(round(time.time() * 1000))) + ',"dct":' + str(int(round(time.time() * 1000))) + ',"mm": []}'
        self.__builder['n']            = self.__get_n_hsw_or_hsl( self.__c['type'], self.__c['req'] )
        self.__builder['c']            = json.dumps( self.__c ) .replace("'", '"')


        print_info(f'{ len( self.__payload["tasklist"] ) } Saving images...')
        for task in self.__payload['tasklist']:
            taskkey = task['task_key']
            url     = task['datapoint_uri']
            self.__save_images(url, taskkey)

        print_info("Analyzing images ...")
        for task in self.__payload['tasklist']:
            taskkey = task['task_key']
            self.__is_correct_v2(obj, taskkey)
        

    def TimeExecution(self):
        return round(self.__finish_time - self.__start_time)

    def TimeExecutionToString(self):
        print_time( f"Finish: {self.TimeExecution()}" )

    def ResolverCaptcha(self):
        self.__reset_init()
        self.__start_time = time.time()

        response_start = self.__start_req_hcaptcha()

        # Verifica se tem o C na resposta da requisição inicial
        if 'c' not in response_start:
            print_erro( 'Response value C não encontrado' )
            self.__finish_time = time.time()
            return { "UUID" : None, "error" : response_start }
            
        self.__c = response_start.get('c')
        type = self.__c.get('type')
        req  = self.__c.get('req')
        
        self.__n = self.__get_n_hsw_or_hsl( type, req )

        self.__payload = self.__get_payload()

        if 'success' in self.__payload and self.__payload.get('success') == False:
            print_erro( 'Houve algum erro ao requisitar o payload das imagens' )
            self.__finish_time = time.time()
            return { "UUID" : None, "error": self.__payload }

        self.__detections_images()

        # self.__remove_images_from_folder()

        self.submit()

        self.__finish_time = time.time()

        return { "UUID" : self.__uuid }

