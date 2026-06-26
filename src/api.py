import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Wine Classifier API",
    description="Classifica vinhos em 3 categorias usando Random Forest",
    version="1.0.0",
)

# carrega os artefatos uma vez na inicializacao
try:
    modelo = joblib.load("modelo/modelo.pkl")
    scaler = joblib.load("modelo/scaler.pkl")
    colunas = joblib.load("modelo/colunas.pkl")
except FileNotFoundError:
    raise RuntimeError("Artefatos nao encontrados. Execute src/treinar.py primeiro.")

CLASSES = {0: "Classe 1 (premium)", 1: "Classe 2 (medio)", 2: "Classe 3 (entrada)"}


class EntradaVinho(BaseModel):
    alcohol: float = Field(..., description="Teor alcoolico", json_schema_extra={"example": 13.2})
    malic_acid: float = Field(..., description="Acido malico", json_schema_extra={"example": 1.78})
    ash: float = Field(..., description="Cinzas", json_schema_extra={"example": 2.14})
    alcalinity_of_ash: float = Field(..., description="Alcalinidade das cinzas", json_schema_extra={"example": 11.2})
    magnesium: float = Field(..., description="Magnesio", json_schema_extra={"example": 100.0})
    total_phenols: float = Field(..., description="Fenois totais", json_schema_extra={"example": 2.65})
    flavanoids: float = Field(..., description="Flavonoides", json_schema_extra={"example": 2.76})
    nonflavanoid_phenols: float = Field(..., description="Fenois nao flavonoides", json_schema_extra={"example": 0.26})
    proanthocyanins: float = Field(..., description="Proantocianinas", json_schema_extra={"example": 1.28})
    color_intensity: float = Field(..., description="Intensidade de cor", json_schema_extra={"example": 4.38})
    hue: float = Field(..., description="Matiz", json_schema_extra={"example": 1.05})
    od280_od315: float = Field(..., description="OD280/OD315", json_schema_extra={"example": 3.40})
    proline: float = Field(..., description="Prolina", json_schema_extra={"example": 1050.0})


class SaidaPredicao(BaseModel):
    classe: int
    descricao: str
    probabilidades: dict[str, float]


@app.get("/")
def status():
    return {"status": "online", "modelo": "RandomForest - Wine Classifier v1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/classificar", response_model=SaidaPredicao)
def classificar(entrada: EntradaVinho):
    try:
        dados = np.array([[
            entrada.alcohol, entrada.malic_acid, entrada.ash,
            entrada.alcalinity_of_ash, entrada.magnesium, entrada.total_phenols,
            entrada.flavanoids, entrada.nonflavanoid_phenols, entrada.proanthocyanins,
            entrada.color_intensity, entrada.hue, entrada.od280_od315, entrada.proline,
            entrada.alcohol / (entrada.malic_acid + 1e-6),
            entrada.color_intensity / (entrada.alcohol + 1e-6),
            entrada.flavanoids * entrada.total_phenols,
        ]])

        dados_scaled = scaler.transform(dados)
        classe = int(modelo.predict(dados_scaled)[0])
        probs = modelo.predict_proba(dados_scaled)[0]

        return SaidaPredicao(
            classe=classe,
            descricao=CLASSES[classe],
            probabilidades={CLASSES[i]: round(float(p), 4) for i, p in enumerate(probs)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
