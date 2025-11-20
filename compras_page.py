import streamlit as st
import pandas as pd
from datetime import date

from data_utils import guardar_compra_historica, cargar_compras_historicas


# =========================
# Inicializar / asegurar estado de Compras
# =========================
def init_state_compras():
    ss = st.session_state

    ss.setdefault("compras", [])             # lista de dicts (compras capturadas)
    ss.setdefault("c_monto_mxn", "$")
    ss.setdefault("c_numero_factura", "")
    ss.setdefault("c_proveedor", "")
    ss.setdefault("c_fecha_emision", None)
    ss.setdefault("c_fecha_pago", None)
    ss.setdefault("c_year", 2025)
    ss.setdefault("c_month", "Selecciona mes")
    ss.setdefault("c_metodo_pago", "TRANSFERENCIA")

    ss.setdefault("compras_historicas", [])


# =========================
# Formatear monto con $ + miles + punto decimal
# =========================
def formatear_monto_compras():
    init_state_compras()
    ss = st.session_state
    texto = ss["c_monto_mxn"].strip()

    if texto == "" or texto == "$":
        ss["c_monto_mxn"] = "$"
        return

    limpio = (
        texto.replace("$", "")
        .replace(",", "")
        .strip()
    )

    try:
        valor = float(limpio)
    except ValueError:
        ss["c_error"] = "Revisa el formato del monto. Ejemplo válido: 18015.74 o 18,015.74"
        return

    ss["c_monto_mxn"] = f"${valor:,.2f}"  # ej: $18,015.74


# =========================
# Callback: guardar compra + resetear campos
# =========================
def guardar_compra():
    init_state_compras()
    ss = st.session_state

    año = ss["c_year"]
    mes = ss["c_month"]
    numero_factura = ss["c_numero_factura"]
    proveedor = ss["c_proveedor"]
    fecha_emision = ss["c_fecha_emision"]
    fecha_pago = ss["c_fecha_pago"]
    metodo_pago = ss["c_metodo_pago"]
    monto_texto = ss["c_monto_mxn"].strip()

    # limpiar mensajes previos
    for key in ["c_warning", "c_error", "c_ok"]:
        if key in ss:
            del ss[key]

    # ---- VALIDACIONES (warnings) ----
    if mes == "Selecciona mes":
        ss["c_warning"] = "Falta seleccionar el **mes** de la compra."
        return

    if not numero_factura:
        ss["c_warning"] = "Falta el **número de factura** de la compra."
        return

    if not proveedor:
        ss["c_warning"] = "Falta el **proveedor** de la compra."
        return

    if fecha_emision is None or fecha_pago is None:
        ss["c_warning"] = "Faltan la **fecha de emisión** y/o la **fecha de pago**."
        return

    monto_limpio = (
        monto_texto.replace("$", "")
        .replace(",", "")
        .strip()
    )

    if monto_limpio == "":
        ss["c_warning"] = "Falta capturar el **monto** de la compra."
        return

    try:
        monto_float = float(monto_limpio)
    except ValueError:
        ss["c_error"] = "Formato de monto inválido. Ejemplo válido: 18015.74 o 18,015.74"
        return

    fecha_emision_str = fecha_emision.strftime("%d/%m/%Y")
    fecha_pago_str = fecha_pago.strftime("%d/%m/%Y")
    monto_formateado = f"${monto_float:,.2f}"

    nuevo_registro = {
        "Año": año,
        "Mes": mes,
        "Número factura": numero_factura,
        "Fecha emisión": fecha_emision_str,
        "Proveedor": proveedor,
        "Monto MXN": monto_formateado,
        "Fecha pago": fecha_pago_str,
        "Método pago": metodo_pago,
    }

    # 1) Guardar en la sesión (para mostrar tabla en la página)
    ss["compras"].append(nuevo_registro)

    # 2) Guardar en histórico CSV
    guardar_compra_historica(nuevo_registro)

    # 3) Actualizar histórico en memoria
    ss["compras_historicas"] = cargar_compras_historicas()

    # Reset para la siguiente compra (solo dejamos el año)
    ss["c_month"] = "Selecciona mes"
    ss["c_numero_factura"] = ""
    ss["c_proveedor"] = ""
    ss["c_monto_mxn"] = "$"
    ss["c_fecha_emision"] = None
    ss["c_fecha_pago"] = None

    ss["c_ok"] = "Factura de compra guardada en el resumen ✅"


# =========================
# Página de Compras
# =========================
def compras_page():
    init_state_compras()
    ss = st.session_state

    st.title("🧾 Compras")
    st.caption("Captura de facturas de **compras/egresos** para el resumen mensual.")

    # Mensajes del callback
    if "c_warning" in ss:
        st.warning(ss["c_warning"])
        del ss["c_warning"]

    if "c_error" in ss:
        st.error(ss["c_error"])
        del ss["c_error"]

    if "c_ok" in ss:
        st.success(ss["c_ok"])
        del ss["c_ok"]

    st.markdown("### Captura de nueva factura de compra")

    col1, col2, col3 = st.columns(3)

    años_disponibles = list(range(2025, 2036))
    meses_lista = [
        "Selecciona mes",
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]
    metodos_pago_lista = ["TRANSFERENCIA", "EFECTIVO", "DEPÓSITO", "TARJETA", "OTRO"]

    with col1:
        st.selectbox(
            "Año",
            años_disponibles,
            key="c_year",
        )
        st.text_input(
            "Número de factura",
            placeholder="Ej. 120",
            key="c_numero_factura",
        )

    with col2:
        st.selectbox(
            "Mes",
            meses_lista,
            key="c_month",
        )
        st.date_input(
            "Fecha de emisión (dd/mm/aaaa)",
            format="DD/MM/YYYY",
            key="c_fecha_emision",
        )

    with col3:
        st.text_input(
            "Proveedor",
            placeholder="Ej. Papelera, Imprenta X",
            key="c_proveedor",
        )
        st.text_input(
            "Monto MXN",
            key="c_monto_mxn",
            help="Escribe el monto y se formatea solo. Ejemplo final: $18,015.74",
            on_change=formatear_monto_compras,
        )

    col4, col5 = st.columns(2)

    with col4:
        st.date_input(
            "Fecha de pago (dd/mm/aaaa)",
            format="DD/MM/YYYY",
            key="c_fecha_pago",
        )

    with col5:
        st.selectbox(
            "Método de pago",
            metodos_pago_lista,
            key="c_metodo_pago",
        )

    st.markdown("---")

    # Botones: guardar y eliminar última compra
    col_guardar, col_eliminar = st.columns([3, 2])

    with col_guardar:
        st.button(
            "💾 Guardar factura de compra",
            on_click=guardar_compra,
            use_container_width=True
        )

    with col_eliminar:
        if st.button("🗑️ Eliminar última factura", use_container_width=True):
            if st.session_state["compras"]:
                st.session_state["compras"].pop()
                st.success("Última factura de compra eliminada 🗑️")
            else:
                st.info("No hay facturas de compra para eliminar.")

    # ===== Tabla con lo capturado =====
    st.markdown("### Facturas de compra capturadas en esta sesión")

    if ss["compras"]:
        df_compras = pd.DataFrame(ss["compras"])
        st.dataframe(df_compras, use_container_width=True)
    else:
        st.info("Todavía no has registrado ninguna factura de compra. Captura la primera arriba ☝️")