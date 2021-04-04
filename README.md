# hCaptcha-Solver-MR

- ByPass do hCaptcha, feito apartir da analise das rotas do servidor do hCaptcha !

### Necessario
```python
pip install -r requirements.txt
```

- Baixar o Yolo.h5 => https://imageai.readthedocs.io/en/latest/detection/
- Baixar o Chrome Driver => https://chromedriver.chromium.org/downloads

### Codigo

```python
site_key  = "51829642-2cda-4b09-896c-594f89d700cc"
site_host = "democaptcha.com"


resolver = hCaptcha( 'f9630567-8bfa-4fc9-8ee5-9c91c6276dff', 'cfcaptcha.audiograb.net' )
resolver.config( saveImage=False ) # Algumas imagens vem com caminha com /, utilizando save image False ele requisita sem salvar a imagem
UUID = resolver.ResolverCaptcha() # Retorna um Json com o UUID caso consiga resolver  e tambem e printado no console
print( UUID )
resolver.TimeExecutionToString()

```

### Atualizações

[x] Adicionado a função de cofiguração
    [x] config: saveImage [True ou False], para utilizar o detection pela imagem salva ou diretamente por requisição => Padão = True
    [x] config: removeImage [True ou False], para apagar ou não as imagens detectadas da pasta, removeImage somente para saveImage True => Padão = True

### Codigo de Referência
- https://github.com/backslash/hCaptcha-Solver-2.0