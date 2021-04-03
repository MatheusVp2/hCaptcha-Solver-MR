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

resolver = hCaptcha( site_key, site_host )
resolver.ResolverCaptcha() # Retorna um Json com o UUID caso consiga resolver  e tambem e printado no console
resolver.TimeExecutionToString()
```

### Codigo de Referência
- https://github.com/backslash/hCaptcha-Solver-2.0