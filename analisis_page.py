import streamlit as st
import pandas as pd
import altair as alt

from data_utils import (
    cargar_ventas_historicas,
    cargar_compras_historicas,
)


def analisis_page():
    st.title("📊 Análisis")
    st.caption("Visualización dinámica de **ventas** y **compras** por mes y por año.")

    # =========================
    # 1) Cargar histórico desde CSV
    # =========================
    ventas_hist = cargar_ventas_historicas()
    compras_hist = cargar_compras_historicas()

    if not ventas_hist and not compras_hist:
        st.info(
            "Todavía no hay datos para analizar. "
            "Primero captura ventas y compras en las pestañas correspondientes."
        )
        return

    # =========================
    # 2) Unificar datos
    # =========================
    def parse_monto(texto):
        if texto is None or texto == "":
            return 0.0
        txt = str(texto).replace("$", "").replace(",", "").strip()
        try:
            return float(txt)
        except ValueError:
            return 0.0

    df_list = []

    if ventas_hist:
        df_v = pd.DataFrame(ventas_hist).copy()
        df_v["Tipo"] = "Ventas"
        df_list.append(df_v)

    if compras_hist:
        df_c = pd.DataFrame(compras_hist).copy()
        df_c["Tipo"] = "Compras"
        df_list.append(df_c)

    df_all = pd.concat(df_list, ignore_index=True)

    df_all["Monto_num"] = df_all["Monto MXN"].apply(parse_monto)

    meses_order = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]
    df_all["Mes"] = pd.Categorical(df_all["Mes"], categories=meses_order, ordered=True)

    # =========================
    # 3) Filtros
    # =========================
    años_disp = sorted(df_all["Año"].unique())

    col1, col2 = st.columns(2)
    with col1:
        año_sel = st.selectbox("Año a analizar", años_disp, key="analisis_año")

    with col2:
        tipo_sel = st.radio(
            "¿Qué quieres ver?",
            ["Ventas y Compras", "Solo ventas", "Solo compras"],
            horizontal=True,
            key="analisis_tipo",
        )

    df_f = df_all[df_all["Año"] == año_sel]

    if tipo_sel == "Solo ventas":
        df_f = df_f[df_f["Tipo"] == "Ventas"]
    elif tipo_sel == "Solo compras":
        df_f = df_f[df_f["Tipo"] == "Compras"]

    if df_f.empty:
        st.warning(
            f"No hay datos para {año_sel} con el filtro seleccionado. "
            "Prueba con otro año o tipo."
        )
        return

    # =========================
    # 4) Gráfica mensual
    # =========================
    df_m = (
        df_f.groupby(["Mes", "Tipo"], as_index=False)["Monto_num"]
        .sum()
        .sort_values("Mes")
    )

    st.markdown("### Totales mensuales")

    chart_m = (
        alt.Chart(df_m)
        .mark_bar()
        .encode(
            x=alt.X("Mes:N", sort=meses_order, title="Mes"),
            y=alt.Y("Monto_num:Q", title="Monto MXN"),
            color="Tipo:N",
            tooltip=["Mes", "Tipo", alt.Tooltip("Monto_num:Q", format=",.2f")],
        )
        .properties(
            width="container",
            height=350,
            title=f"Totales mensuales {año_sel}",
        )
    )

    st.altair_chart(chart_m, use_container_width=True)

    # =========================
    # 5) Gráfica anual (histórico)
    # =========================
    st.markdown("---")
    st.markdown("### Totales anuales (histórico)")

    df_y = (
        df_all.groupby(["Año", "Tipo"], as_index=False)["Monto_num"]
        .sum()
        .sort_values("Año")
    )

    chart_y = (
        alt.Chart(df_y)
        .mark_bar()
        .encode(
            x=alt.X("Año:O", title="Año"),
            y=alt.Y("Monto_num:Q", title="Monto MXN"),
            color="Tipo:N",
            tooltip=["Año", "Tipo", alt.Tooltip("Monto_num:Q", format=",.2f")],
        )
        .properties(
            width="container",
            height=300,
            title="Totales anuales de ventas y compras",
        )
    )

    st.altair_chart(chart_y, use_container_width=True)

    # 👀 IMPORTANTE:
    # Ya no mostramos la tabla de detalle aquí.
    # El detalle completo se moverá a la nueva página "Histórico".