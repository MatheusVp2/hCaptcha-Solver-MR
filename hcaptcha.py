from selenium import webdriver  # Drive Selenium
from selenium.webdriver.chrome.options import Options  # Options do Chrome
from selenium.webdriver.support.ui import WebDriverWait  # Espera de carregamento

from imageai.Detection import ObjectDetection # Detecção dos Objetos

from my_logger import print_erro, print_fail, print_info, print_key, print_pass, print_time

import cv2
import numpy as np

import requests
import json
import time
import os

def saveJson(file, data):
    with open(file, 'w') as outfile:
        json.dump(data, outfile, indent=2)


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
    'content-type': 'application/json;charset=UTF-8',
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

        self.__has_save_image = True
        self.__remove_data_images = True

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
        self.__payload = None
        self.__c       = None
        self.__n       = None
        self.__key     = None

        # Response UUID do hCaptcha
        self.__uuid = None

        # Verificação do Tempo de Execução da Aplicação
        self.__start_time  = None
        self.__finish_time = None

    def config( self, saveImage=True, removeImage=True ):
        self.__has_save_image = saveImage
        self.__remove_data_images = removeImage

    # Funções auxiliares
    def __create_path_if_not_exists(self):
        if not os.path.exists( self.__path_images ):
            os.mkdir( self.__path_images )
        if not os.path.exists( self.__path_images_detections ):
            os.mkdir( self.__path_images_detections )

    def __save_images(self, url, taskkey):
        path_image = f"{ self.__path_images }{ taskkey }.jpg"
        response = SESSAO_REQUESTS.get(url)
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
            'v' : '8ac1d9d',
            'host': self.__site_host,
            'sitekey': self.__site_key,
            'hl'        : 'en',
            'motionData': '{}',
            
        }

        if self.__c != None:
            data['n'] = self.__n,
            data['c'] = json.dumps( self.__c ).replace("'", '"')

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

    def __is_correct_v1(self, obj, url, taskkey ):
        image = SESSAO_REQUESTS.get(url)
        nparr = np.frombuffer(image.content, np.uint8)
        im    = cv2.imdecode(nparr, flags=1)
        detected_image, detections = self.__detector.detectObjectsFromImage(input_image=im, input_type="array", output_type="array")
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

        print( response.json() )

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

        self.__builder['v']            = '8ac1d9d'
        self.__builder['job_mode']     = 'image_label_binary'
        self.__builder['answers']      = {}
        self.__builder['serverdomain'] = self.__site_host
        self.__builder['sitekey']      = self.__site_key
        self.__builder['motionData']   = '{"st":' + str(int(round(time.time() * 1000))) + ',"dct":' + str(int(round(time.time() * 1000))) + ',"mm": []}'
        # self.__builder['motionData']   = "{\"st\":1617512750983,\"dct\":1617512750983,\"mm\":[[1,306,1617512751670],[6,309,1617512751688],[10,312,1617512751705],[15,315,1617512751722],[19,317,1617512751739],[22,320,1617512751757],[28,324,1617512751789],[32,329,1617512751806],[35,332,1617512751822],[39,334,1617512751838],[42,334,1617512751855],[44,334,1617512751872],[47,335,1617512751889],[50,337,1617512751906],[53,338,1617512751922],[58,341,1617512751938],[65,344,1617512751955],[73,348,1617512751972],[82,354,1617512751989],[98,365,1617512752005],[109,374,1617512752022],[122,381,1617512752038],[135,386,1617512752055],[144,389,1617512752072],[149,391,1617512752089],[150,391,1617512752165],[155,391,1617512752189],[156,392,1617512752205],[154,393,1617512752222],[153,391,1617512752350],[154,385,1617512752373],[166,380,1617512752391],[189,378,1617512752422],[196,378,1617512752439],[200,376,1617512752456],[200,372,1617512752473],[200,366,1617512752489],[199,360,1617512752507],[196,353,1617512752539],[193,350,1617512752556],[190,347,1617512752573],[186,342,1617512752590],[183,338,1617512752606],[179,332,1617512752622],[173,326,1617512752639],[169,321,1617512752657],[160,313,1617512752689],[155,309,1617512752706],[149,305,1617512752723],[145,302,1617512752740],[141,300,1617512752756],[138,299,1617512752773],[136,298,1617512752790],[135,298,1617512752966],[134,298,1617512752989],[132,298,1617512753006],[130,300,1617512753023],[128,300,1617512753040],[126,301,1617512753056],[125,301,1617512753398],[123,301,1617512753423],[122,301,1617512753440],[120,301,1617512753457],[116,300,1617512753473],[113,299,1617512753490],[111,297,1617512753507],[108,296,1617512753523],[107,295,1617512753540],[103,292,1617512753557],[99,289,1617512753573],[95,286,1617512753590],[89,281,1617512753607],[83,275,1617512753623],[77,269,1617512753640],[71,261,1617512753657],[66,255,1617512753674],[63,249,1617512753690],[60,244,1617512753708],[59,242,1617512753725],[59,241,1617512753750],[59,240,1617512753773],[59,238,1617512753790],[59,236,1617512753807],[60,232,1617512753824],[60,230,1617512753840],[62,226,1617512753857],[62,225,1617512753874],[63,223,1617512753890],[64,225,1617512754692],[72,235,1617512754709],[78,239,1617512754725],[92,250,1617512754741],[117,269,1617512754758],[136,281,1617512754775],[158,294,1617512754791],[184,306,1617512754808],[213,317,1617512754825],[243,325,1617512754842],[272,331,1617512754860],[313,339,1617512754891],[325,342,1617512754909],[337,343,1617512754926],[345,343,1617512754958],[346,343,1617512754975],[347,342,1617512755134],[346,342,1617512755150],[338,339,1617512755176],[331,339,1617512755194],[312,339,1617512755227],[295,339,1617512755259],[289,339,1617512755276],[284,340,1617512755292],[276,341,1617512755309],[265,343,1617512755326],[255,343,1617512755342],[245,343,1617512755359],[238,343,1617512755376],[233,343,1617512755392],[228,343,1617512755409],[224,343,1617512755426],[222,344,1617512755442],[221,345,1617512755459],[219,346,1617512755476],[216,348,1617512755492],[211,353,1617512755509],[208,357,1617512755526],[203,363,1617512755542],[197,368,1617512755559],[192,373,1617512755576],[188,379,1617512755593],[185,385,1617512755609],[183,389,1617512755625],[183,391,1617512755642],[183,395,1617512755659],[183,399,1617512755675],[183,401,1617512755692],[182,404,1617512755709],[182,407,1617512755725],[183,412,1617512755742],[187,418,1617512755759],[192,424,1617512755776],[201,429,1617512755794],[235,436,1617512755826],[260,442,1617512755842],[286,446,1617512755859],[309,451,1617512755876],[325,455,1617512755892],[337,457,1617512755909],[341,458,1617512755926],[342,459,1617512755942],[342,458,1617512756046],[342,449,1617512756077],[343,434,1617512756094],[343,422,1617512756110],[343,408,1617512756126],[342,393,1617512756143],[342,381,1617512756161],[339,350,1617512756193],[335,333,1617512756210],[332,316,1617512756227],[330,302,1617512756243],[328,292,1617512756260],[326,283,1617512756277],[326,277,1617512756293],[325,272,1617512756310],[324,269,1617512756326],[324,266,1617512756343],[324,263,1617512756360],[324,261,1617512756378],[324,257,1617512756410],[324,254,1617512756427],[324,252,1617512756443],[323,242,1617512756460],[323,232,1617512756477],[323,227,1617512756494],[323,224,1617512756510],[323,223,1617512756527],[321,224,1617512756757],[319,227,1617512756776],[316,234,1617512756793],[311,241,1617512756810],[307,250,1617512756827],[300,260,1617512756844],[293,272,1617512756861],[281,289,1617512756878],[273,299,1617512756894],[266,306,1617512756910],[258,311,1617512756927],[251,315,1617512756943],[245,318,1617512756960],[238,318,1617512756977],[231,318,1617512756993],[223,318,1617512757010],[216,318,1617512757028],[210,318,1617512757044],[202,320,1617512757061],[194,322,1617512757078],[187,324,1617512757110],[186,325,1617512757357],[185,326,1617512757373],[185,328,1617512757389],[183,335,1617512757411],[182,343,1617512757428],[180,356,1617512757444],[175,373,1617512757461],[172,381,1617512757477],[167,389,1617512757494],[161,398,1617512757511],[155,406,1617512757528],[148,412,1617512757544],[141,418,1617512757562],[126,427,1617512757595],[117,431,1617512757613],[104,436,1617512757645],[102,437,1617512757661],[100,438,1617512757677],[100,441,1617512757694],[103,445,1617512757711],[109,449,1617512757728],[118,453,1617512757744],[131,459,1617512757761],[145,465,1617512757778],[160,473,1617512757794],[174,482,1617512757811],[190,490,1617512757828],[207,503,1617512757845],[213,520,1617512757862],[219,532,1617512757878],[221,540,1617512757894],[222,544,1617512757911],[222,547,1617512757928],[222,549,1617512757944],[222,552,1617512757961],[222,556,1617512757979],[222,562,1617512758011],[221,566,1617512758028],[221,569,1617512758045],[219,573,1617512758061],[219,575,1617512758078],[219,578,1617512758095],[218,579,1617512758126],[218,576,1617512758161],[219,567,1617512758178],[219,558,1617512758195],[219,550,1617512758212],[219,542,1617512758228],[219,527,1617512758245],[219,514,1617512758261],[218,498,1617512758278],[216,483,1617512758295],[213,473,1617512758311],[213,470,1617512758328],[213,469,1617512758345],[217,477,1617512758395],[226,487,1617512758412],[239,499,1617512758428],[262,517,1617512758445],[279,527,1617512758461],[292,534,1617512758478],[300,539,1617512758495],[304,542,1617512758511],[304,543,1617512758533],[303,546,1617512758562],[301,549,1617512758578],[299,550,1617512758596],[293,552,1617512758612],[278,555,1617512758629],[266,557,1617512758646],[255,559,1617512758662],[248,561,1617512758678],[244,561,1617512758695],[240,561,1617512758712],[234,559,1617512758729],[230,557,1617512758746],[228,555,1617512758762],[229,553,1617512758781],[230,552,1617512758797],[235,552,1617512758829],[253,554,1617512758846],[274,558,1617512758862],[299,563,1617512758879],[322,568,1617512758896],[338,571,1617512758912],[345,573,1617512758929],[346,573,1617512758946],[347,572,1617512758963],[347,571,1617512758979],[346,570,1617512758996]],\"mm-mp\":23.331210191082807,\"md\":[[63,223,1617512754590],[346,343,1617512755037],[323,223,1617512756638],[346,570,1617512759070]],\"md-mp\":1493.3333333333333,\"mu\":[[63,223,1617512754677],[346,343,1617512755109],[323,223,1617512756709],[346,570,1617512759157]],\"mu-mp\":1493.3333333333333,\"topLevel\":{\"inv\":false,\"st\":1617512743374,\"sc\":{\"availWidth\":1920,\"availHeight\":1040,\"width\":1920,\"height\":1080,\"colorDepth\":24,\"pixelDepth\":24,\"availLeft\":0,\"availTop\":0},\"nv\":{\"vendorSub\":\"\",\"productSub\":\"20030107\",\"vendor\":\"Google Inc.\",\"maxTouchPoints\":0,\"userActivation\":{},\"doNotTrack\":null,\"geolocation\":{},\"connection\":{},\"webkitTemporaryStorage\":{},\"webkitPersistentStorage\":{},\"hardwareConcurrency\":12,\"cookieEnabled\":true,\"appCodeName\":\"Mozilla\",\"appName\":\"Netscape\",\"appVersion\":\"5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36\",\"platform\":\"Win32\",\"product\":\"Gecko\",\"userAgent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36\",\"language\":\"pt-BR\",\"languages\":[\"pt-BR\",\"pt\",\"en-US\",\"en\"],\"onLine\":true,\"webdriver\":false,\"scheduling\":{},\"mediaCapabilities\":{},\"permissions\":{},\"mediaSession\":{},\"plugins\":[\"internal-pdf-viewer\",\"mhjfbmdgcfjbbpaeojofohoefgiehjai\",\"internal-nacl-plugin\"]},\"dr\":\"\",\"exec\":false,\"wn\":[],\"wn-mp\":0,\"xy\":[],\"xy-mp\":0,\"mm\":[[1823,120,1617512744165],[1849,105,1617512744182],[1864,94,1617512744198],[1874,86,1617512744215],[1881,81,1617512744232],[1888,76,1617512744248],[1898,68,1617512744265],[1904,62,1617512744281],[1905,61,1617512744298],[1907,62,1617512744374],[1909,66,1617512744398],[1918,78,1617512744422],[1908,51,1617512749910],[1860,71,1617512749937],[1815,88,1617512749955],[1696,117,1617512749988],[1549,152,1617512750020],[1474,171,1617512750037],[1359,200,1617512750053],[1283,218,1617512750070],[1209,237,1617512750087],[1146,252,1617512750103],[1095,263,1617512750122],[1015,280,1617512750154],[979,287,1617512750170],[943,293,1617512750187],[907,301,1617512750203],[873,308,1617512750221],[827,317,1617512750238],[554,332,1617512751582],[557,332,1617512751606],[563,335,1617512751638],[568,337,1617512751656],[572,340,1617512751674]],\"mm-mp\":112.7260273972603},\"v\":1}"
        
        if self.__c != None:
            self.__builder['n']            = self.__get_n_hsw_or_hsl( self.__c['type'], self.__c['req'] )
            self.__builder['c']            = json.dumps( self.__c ) .replace("'", '"')

        if self.__has_save_image:
            print_info(f'{ len( self.__payload["tasklist"] ) } Saving images...')
            for task in self.__payload['tasklist']:
                taskkey = task['task_key']
                url     = task['datapoint_uri']
                self.__save_images(url, taskkey)

        print_info("Analyzing images ...")
        for task in self.__payload['tasklist']:
            taskkey = task['task_key']
            url     = task['datapoint_uri']
            
            if self.__has_save_image:
                self.__is_correct_v2(obj, taskkey)
            else:
                self.__is_correct_v1(obj, url, taskkey)


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
            print_info( f'Response: { response_start }' )
        else:
            self.__c = response_start.get('c')
            type = self.__c.get('type')
            req  = self.__c.get('req')

            self.__n = self.__get_n_hsw_or_hsl( type, req )

        self.__payload = self.__get_payload()

        if 'success' in self.__payload and self.__payload.get('success') == False:
            print_erro( 'Houve algum erro ao requisitar o payload das imagens' )
            self.__finish_time = time.time()
            return { "UUID" : None, "error": self.__payload }

        if type == 'hsl':
            response_start = self.__start_req_hcaptcha()
            self.__c = response_start.get('c')
            type = self.__c.get('type')
            req  = self.__c.get('req')
            self.__n = self.__get_n_hsw_or_hsl( type, req )

        self.__detections_images()

        if self.__has_save_image == True and self.__remove_data_images == True:
            self.__remove_images_from_folder()

        self.submit()

        self.__finish_time = time.time()

        return { "UUID" : self.__uuid }

# 'f9630567-8bfa-4fc9-8ee5-9c91c6276dff', 'cfcaptcha.audiograb.net'

resolver = hCaptcha( '51829642-2cda-4b09-896c-594f89d700cc', 'democaptcha.com' )
resolver.config( saveImage=False )
UUID = resolver.ResolverCaptcha()
resolver.TimeExecutionToString()