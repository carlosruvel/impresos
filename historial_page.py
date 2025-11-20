import streamlit as st
import pandas as pd

from data_utils import (
    cargar_ventas_historicas,
    cargar_compras_historicas,
)


def historial_page():
    st.title("🗂️ Historial de registros")
    st.caption(
        "Vista interna con el detalle completo de todas las **ventas** y **compras** "
        "guardadas en el sistema."
    )

    ventas_hist = cargar_ventas_historicas()
    compras_hist = cargar_compras_historicas()

    if not ventas_hist and not compras_hist:
        st.info("Todavía no hay historial guardado. Captura ventas y compras primero.")
        return

    # Unificamos datos igual que en análisis
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

    # Filtros arriba para que lo puedas explorar tranquilo
    años_disp = sorted(df_all["Año"].unique())
    tipos_disp = sorted(df_all["Tipo"].unique())

    col1, col2, col3 = st.columns(3)
    with col1:
        año_sel = st.selectbox("Filtrar por año", ["Todos"] + años_disp, key="hist_año")

    with col2:
        tipo_sel = st.selectbox(
            "Filtrar por tipo", ["Todos"] + tipos_disp, key="hist_tipo"
        )

    with col3:
        mes_disp = sorted(df_all["Mes"].dropna().unique().tolist())
        mes_sel = st.selectbox(
            "Filtrar por mes", ["Todos"] + mes_disp, key="hist_mes"
        )

    df_f = df_all.copy()

    if año_sel != "Todos":
        df_f = df_f[df_f["Año"] == año_sel]

    if tipo_sel != "Todos":
        df_f = df_f[df_f["Tipo"] == tipo_sel]

    if mes_sel != "Todos":
        df_f = df_f[df_f["Mes"] == mes_sel]

    st.markdown("---")
    st.markdown("### Detalle histórico filtrado")

    if df_f.empty:
        st.warning("No hay registros que coincidan con los filtros seleccionados.")
        return

    st.dataframe(df_f, use_container_width=True)

    # Botón opcional para descargar todo el histórico
    st.markdown("")
    csv = df_f.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "💾 Descargar histórico filtrado (CSV)",
        data=csv,
        file_name="historial_impresos_mendieta.csv",
        mime="text/csv",
    )