import joblib
import numpy as np
from pathlib import Path
from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score


def engenharia_de_features(X: np.ndarray, colunas: list) -> np.ndarray:
    import pandas as pd
    df = pd.DataFrame(X, columns=colunas)
    df["alcool_acido"] = df["alcohol"] / (df["malic_acid"] + 1e-6)
    df["cor_por_alcool"] = df["color_intensity"] / (df["alcohol"] + 1e-6)
    df["indice_maturidade"] = df["flavanoids"] * df["total_phenols"]
    return df.values, df.columns.tolist()


def treinar() -> None:
    wine = load_wine()
    X, y = wine.data, wine.target
    colunas = wine.feature_names

    X_eng, colunas_final = engenharia_de_features(X, list(colunas))

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X_eng, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_treino_scaled = scaler.fit_transform(X_treino)
    X_teste_scaled = scaler.transform(X_teste)

    modelo = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    modelo.fit(X_treino_scaled, y_treino)

    acc = accuracy_score(y_teste, modelo.predict(X_teste_scaled))
    print(f"Accuracy no teste: {acc:.4f}")

    Path("modelo").mkdir(exist_ok=True)
    joblib.dump(modelo, "modelo/modelo.pkl")
    joblib.dump(scaler, "modelo/scaler.pkl")
    joblib.dump(colunas_final, "modelo/colunas.pkl")
    print("Modelo, scaler e colunas salvos em modelo/")


if __name__ == "__main__":
    treinar()
