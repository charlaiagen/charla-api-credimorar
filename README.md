### Sequência de comandos para dar push na imagem no artifact registry

1) buildar a imagem localmente

```bash
docker build -t credimorar .
```

2) certifique-se de instalar o gcloud na sua maquina e se autenticar fazendo

```bash
gcloud init
```
 
3) Upload no googlecoud artifact registry

```bash
gcloud auth configure-docker us-east4-docker.pkg.dev
```

4) Tagueie a imagme local

```bash
docker tag credimorar us-east4-docker.pkg.dev/credimorar-poc/credimorar-poc/credimorar:latest
```

5) Push para o artifact registry

```bash
docker push us-east4-docker.pkg.dev/credimorar-poc/credimorar-poc/credimorar:latest
```