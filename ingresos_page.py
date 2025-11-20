import streamlit as st
import pandas as pd
from datetime import date

from data_utils import guardar_venta_historica, cargar_ventas_historicas


# =========================
# Inicializar / asegurar estado de Ventas
# =========================
def init_state_ventas():
    ss = st.session_state

    ss.setdefault("ingresos", [])          # lista de dicts (ventas capturadas)
    ss.setdefault("monto_mxn", "$")
    ss.setdefault("numero_factura", "")
    ss.setdefault("cliente", "")
    ss.setdefault("fecha_emision", None)   # para que se vea DD/MM/YYYY
    ss.setdefault("fecha_pago", None)
    ss.setdefault("year", 2025)
    ss.setdefault("month", "Selecciona mes")
    ss.setdefault("metodo_pago", "TRANSFERENCIA")

    # histórico (se rellenará desde CSV en análisis, pero por si quieres usarlo aquí)
    ss.setdefault("ventas_historicas", [])


# =========================
# Formatear monto con $ + miles + punto decimal
# =========================
def formatear_monto():
    init_state_ventas()  # por si el callback se llama muy pronto
    ss = st.session_state
    texto = ss["monto_mxn"].strip()

    # Si está vacío, dejamos solo el signo $
    if texto == "" or texto == "$":
        ss["monto_mxn"] = "$"
        return

    # quitar símbolo $, comas y espacios
    limpio = (
        texto.replace("$", "")
        .replace(",", "")
        .strip()
    )

    try:
        valor = float(limpio)
    except ValueError:
        # error de formato → lo marcamos pero no reventamos
        ss["form_error"] = "Revisa el formato del monto. Ejemplo válido: 18015.74 o 18,015.74"
        return

    # volvemos a escribirlo ya formateado, con $
    ss["monto_mxn"] = f"${valor:,.2f}"  # ej: $18,015.74


# =========================
# Callback: guardar factura + resetear campos
# =========================
def guardar_factura():
    init_state_ventas()
    ss = st.session_state

    año = ss["year"]
    mes = ss["month"]
    numero_factura = ss["numero_factura"]
    cliente = ss["cliente"]
    fecha_emision = ss["fecha_emision"]
    fecha_pago = ss["fecha_pago"]
    metodo_pago = ss["metodo_pago"]
    monto_texto = ss["monto_mxn"].strip()

    # ---- LIMPIAMOS mensajes previos ----
    for key in ["form_warning", "form_error", "mensaje_ok"]:
        if key in ss:
            del ss[key]

    # ---- VALIDACIONES (warnings) ----
    if mes == "Selecciona mes":
        ss["form_warning"] = "Falta seleccionar el **mes** de la venta."
        return

    if not numero_factura:
        ss["form_warning"] = "Falta el **número de factura**."
        return

    if not cliente:
        ss["form_warning"] = "Falta el **cliente** de la factura."
        return

    if fecha_emision is None or fecha_pago is None:
        ss["form_warning"] = "Faltan la **fecha de emisión** y/o la **fecha de pago**."
        return

    monto_limpio = (
        monto_texto.replace("$", "")
        .replace(",", "")
        .strip()
    )

    if monto_limpio == "":
        ss["form_warning"] = "Falta capturar el **monto** de la factura."
        return

    try:
        monto_float = float(monto_limpio)
    except ValueError:
        ss["form_error"] = "Formato de monto inválido. Ejemplo válido: 18015.74 o 18,015.74"
        return

    # ---- Construimos el registro ----
    fecha_emision_str = fecha_emision.strftime("%d/%m/%Y")
    fecha_pago_str = fecha_pago.strftime("%d/%m/%Y")
    monto_formateado = f"${monto_float:,.2f}"

    nuevo_registro = {
        "Año": año,
        "Mes": mes,
        "Número factura": numero_factura,
        "Fecha emisión": fecha_emision_str,
        "Cliente": cliente,
        "Monto MXN": monto_formateado,
        "Fecha pago": fecha_pago_str,
        "Método pago": metodo_pago,
    }

    # 1) Guardar en la sesión (para mostrar en la tabla de la página Ventas)
    ss["ingresos"].append(nuevo_registro)

    # 2) Guardar en el histórico (CSV permanente)
    guardar_venta_historica(nuevo_registro)

    # 3) Actualizar histórico en memoria (por si lo quieres usar en otro lado)
    ss["ventas_historicas"] = cargar_ventas_historicas()

    # ===== reset para la siguiente factura =====
    ss["month"] = "Selecciona mes"
    ss["numero_factura"] = ""
    ss["cliente"] = ""
    ss["monto_mxn"] = "$"      # solo el signo $
    ss["fecha_emision"] = None
    ss["fecha_pago"] = None
    # método de pago se mantiene por comodidad

    ss["mensaje_ok"] = "Factura de venta guardada en el resumen ✅"


# =========================
# Página de Ventas
# =========================
def ingresos_page():
    init_state_ventas()
    ss = st.session_state

    st.title("📥 Ventas")
    st.caption("Captura de facturas de **ventas** para el resumen mensual.")

    # Mensajes del callback
    if "form_warning" in ss:
        st.warning(ss["form_warning"])
        del ss["form_warning"]

    if "form_error" in ss:
        st.error(ss["form_error"])
        del ss["form_error"]

    if "mensaje_ok" in ss:
        st.success(ss["mensaje_ok"])
        del ss["mensaje_ok"]

    st.markdown("### Captura de nueva factura de venta")

    # ===== Layout en columnas =====
    col1, col2, col3 = st.columns(3)

    años_disponibles = list(range(2025, 2036))
    meses_lista = [
        "Selecciona mes",  # placeholder
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]
    metodos_pago_lista = ["TRANSFERENCIA", "EFECTIVO", "DEPÓSITO", "TARJETA", "OTRO"]

    with col1:
        st.selectbox(
            "Año",
            años_disponibles,
            key="year",
        )
        st.text_input(
            "Número de factura",
            placeholder="Ej. 65",
            key="numero_factura",
        )

    with col2:
        st.selectbox(
            "Mes",
            meses_lista,
            key="month",
        )
        st.date_input(
            "Fecha de emisión (dd/mm/aaaa)",
            format="DD/MM/YYYY",
            key="fecha_emision",
        )

    with col3:
        st.text_input(
            "Cliente",
            placeholder="Ej. CUCEA, DIAGMEX, PREPA 9",
            key="cliente",
        )
        st.text_input(
            "Monto MXN",
            key="monto_mxn",
            help="Escribe el monto y se formatea solo. Ejemplo final: $18,015.74",
            on_change=formatear_monto,
        )

    col4, col5 = st.columns(2)

    with col4:
        st.date_input(
            "Fecha de pago (dd/mm/aaaa)",
            format="DD/MM/YYYY",
            key="fecha_pago",
        )

    with col5:
        st.selectbox(
            "Método de pago",
            metodos_pago_lista,
            key="metodo_pago",
        )

    st.markdown("---")

    # Botones: guardar y eliminar última factura
    col_guardar, col_eliminar = st.columns([3, 2])

    with col_guardar:
        st.button(
            "💾 Guardar factura de venta",
            on_click=guardar_factura,
            use_container_width=True
        )

    with col_eliminar:
        if st.button("🗑️ Eliminar última factura", use_container_width=True):
            if st.session_state["ingresos"]:
                st.session_state["ingresos"].pop()
                st.success("Última factura de venta eliminada 🗑️")
            else:
                st.info("No hay facturas de venta para eliminar.")

    # ===== Tabla con lo capturado =====
    st.markdown("### Facturas de venta capturadas en esta sesión")

    if ss["ingresos"]:
        df_ingresos = pd.DataFrame(ss["ingresos"])
        st.dataframe(df_ingresos, use_container_width=True)
    else:
        st.info("Todavía no has registrado ninguna factura de venta. Captura la primera arriba ☝️")