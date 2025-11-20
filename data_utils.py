# data_utils.py
import os
import pandas as pd

# Carpeta donde se guardan los CSV
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

VENTAS_FILE = os.path.join(DATA_DIR, "ventas_historico.csv")
COMPRAS_FILE = os.path.join(DATA_DIR, "compras_historico.csv")


def _append_row(file_path: str, row: dict):
    """
    Agrega un registro al CSV.
    - Si el archivo existe, concatena y elimina duplicados exactos.
    - Si no existe, lo crea con la primera fila.
    """
    df_new = pd.DataFrame([row])

    if os.path.exists(file_path):
        df = pd.read_csv(file_path, dtype=str)
        df = pd.concat([df, df_new], ignore_index=True).drop_duplicates()
    else:
        df = df_new

    df.to_csv(file_path, index=False)


# ------------ VENTAS ------------

def guardar_venta_historica(row: dict):
    _append_row(VENTAS_FILE, row)


def cargar_ventas_historicas() -> list[dict]:
    if not os.path.exists(VENTAS_FILE):
        return []
    df = pd.read_csv(VENTAS_FILE, dtype=str).fillna("")
    return df.to_dict(orient="records")


# ------------ COMPRAS ------------

def guardar_compra_historica(row: dict):
    _append_row(COMPRAS_FILE, row)


def cargar_compras_historicas() -> list[dict]:
    if not os.path.exists(COMPRAS_FILE):
        return []
    df = pd.read_csv(COMPRAS_FILE, dtype=str).fillna("")
    return df.to_dict(orient="records")