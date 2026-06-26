# imagem base: Python 3.11 em versao minima (slim = sem pacotes desnecessarios)
FROM python:3.11-slim

# define o diretorio de trabalho dentro do container
WORKDIR /app

# copia primeiro so o requirements.txt
# isso aproveita o cache do Docker: se as deps nao mudaram, nao reinstala
COPY requirements.txt .

# instala as dependencias sem cache local (economiza espaco na imagem)
RUN pip install --no-cache-dir -r requirements.txt

# agora copia o restante do codigo
COPY src/ ./src/
COPY modelo/ ./modelo/

# documenta que a aplicacao escuta na porta 8000
EXPOSE 8000

# comando executado quando o container inicia
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
