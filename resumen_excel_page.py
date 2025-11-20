import streamlit as st
import pandas as pd
import io

# =========================================
# Helpers de estado para la pestaña Resumen
# =========================================
def init_state_resumen():
    ss = st.session_state
    ss.setdefault("resumen_mes_prev", None)
    ss.setdefault("resumen_año_prev", None)
    ss.setdefault("resumen_ocultar_tablas", False)

    # Listas donde guardaremos el histórico para la pestaña Análisis
    ss.setdefault("ventas_historicas", [])   # registros ya enviados a Análisis
    ss.setdefault("compras_historicas", [])


# =========================================
# Construir archivo Excel en memoria
# =========================================
def construir_excel(mes_sel, año_sel, df_v_mes, df_c_mes):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        # Formatos
        formato_titulo = workbook.add_format(
            {"bold": True, "font_size": 16, "align": "left"}
        )
        formato_sub = workbook.add_format(
            {"bold": True, "font_size": 12, "align": "left"}
        )
        formato_header = workbook.add_format(
            {"bold": True, "bg_color": "#D9D9D9", "border": 1}
        )
        formato_normal = workbook.add_format({"border": 1})

        # ===== Hoja principal =====
        hoja = workbook.add_worksheet("Resumen")

        # Título
        titulo = f"Impresos / {mes_sel} {año_sel}"
        hoja.write(0, 0, titulo, formato_titulo)

        # ===== Bloque INGRESOS =====
        fila_inicio_ing = 2
        hoja.write(fila_inicio_ing, 0, "INGRESOS", formato_sub)

        if not df_v_mes.empty:
            df_v_mes_excel = df_v_mes.copy()
            df_v_mes_excel.to_excel(
                writer,
                sheet_name="Resumen",
                startrow=fila_inicio_ing + 2,
                startcol=0,
                index=False,
                header=False
            )

            # Encabezados
            for col, nombre_col in enumerate(df_v_mes.columns):
                hoja.write(fila_inicio_ing + 1, col, nombre_col, formato_header)

            filas_v = len(df_v_mes)
            for fila in range(fila_inicio_ing + 2, fila_inicio_ing + 2 + filas_v):
                for col in range(len(df_v_mes.columns)):
                    hoja.write(
                        fila,
                        col,
                        df_v_mes.iloc[fila - (fila_inicio_ing + 2), col],
                        formato_normal,
                    )

        # ===== Bloque EGRESOS =====
        fila_inicio_egr = fila_inicio_ing + 4 + max(len(df_v_mes), 1)
        hoja.write(fila_inicio_egr, 0, "EGRESOS", formato_sub)

        if not df_c_mes.empty:
            df_c_mes_excel = df_c_mes.copy()
            df_c_mes_excel.to_excel(
                writer,
                sheet_name="Resumen",
                startrow=fila_inicio_egr + 2,
                startcol=0,
                index=False,
                header=False
            )

            # Encabezados
            for col, nombre_col in enumerate(df_c_mes.columns):
                hoja.write(fila_inicio_egr + 1, col, nombre_col, formato_header)

            filas_c = len(df_c_mes)
            for fila in range(fila_inicio_egr + 2, fila_inicio_egr + 2 + filas_c):
                for col in range(len(df_c_mes.columns)):
                    hoja.write(
                        fila,
                        col,
                        df_c_mes.iloc[fila - (fila_inicio_egr + 2), col],
                        formato_normal,
                    )

        # Ajustar ancho de columnas
        for col in range(0, 8):
            hoja.set_column(col, col, 15)

    output.seek(0)
    return output.getvalue()


# =========================================
# Página de Resumen Excel
# =========================================
def resumen_excel_page():
    init_state_resumen()
    ss = st.session_state

    st.title("📄 Resumen Excel")
    st.caption("Genera un archivo Excel con el resumen mensual de **ventas** y **compras**.")

    # Dropdowns de año y mes
    años_disponibles = list(range(2025, 2036))
    meses_lista = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]

    col1, col2 = st.columns(2)
    with col1:
        año_sel = st.selectbox("Año", años_disponibles, key="resumen_año")
    with col2:
        mes_sel = st.selectbox("Mes", meses_lista, key="resumen_mes")

    # Si cambian año o mes, volvemos a mostrar tablas
    if ss["resumen_año_prev"] != año_sel or ss["resumen_mes_prev"] != mes_sel:
        ss["resumen_ocultar_tablas"] = False
        ss["resumen_año_prev"] = año_sel
        ss["resumen_mes_prev"] = mes_sel

    st.markdown(f"## Resumen para: **{mes_sel} {año_sel}** 🔁")

    # ===== DataFrames a partir de lo capturado en la sesión =====
    ingresos_lista = ss.get("ingresos", [])
    compras_lista = ss.get("compras", [])

    df_ventas = pd.DataFrame(ingresos_lista) if ingresos_lista else pd.DataFrame()
    df_compras = pd.DataFrame(compras_lista) if compras_lista else pd.DataFrame()

    # Filtrar por año + mes seleccionados
    if not df_ventas.empty:
        df_v_mes = df_ventas[(df_ventas["Año"] == año_sel) & (df_ventas["Mes"] == mes_sel)]
    else:
        df_v_mes = pd.DataFrame(columns=["Año", "Mes", "Número factura",
                                         "Fecha emisión", "Cliente",
                                         "Monto MXN", "Fecha pago", "Método pago"])

    if not df_compras.empty:
        df_c_mes = df_compras[(df_compras["Año"] == año_sel) & (df_compras["Mes"] == mes_sel)]
    else:
        df_c_mes = pd.DataFrame(columns=["Año", "Mes", "Número factura",
                                         "Fecha emisión", "Proveedor",
                                         "Monto MXN", "Fecha pago", "Método pago"])

    # ===== Mostrar tablas sólo si no se han “limpiado” tras acciones =====
    col_v, col_c = st.columns(2)

    if not ss.get("resumen_ocultar_tablas", False):
        with col_v:
            st.markdown("### Ventas (Ingresos)")
            if not df_v_mes.empty:
                st.dataframe(df_v_mes, use_container_width=True)
            else:
                st.info("No hay ventas capturadas para este mes/año.")

        with col_c:
            st.markdown("### Compras (Egresos)")
            if not df_c_mes.empty:
                st.dataframe(df_c_mes, use_container_width=True)
            else:
                st.info("No hay compras capturadas para este mes/año.")
    else:
        st.info(
            "El resumen de este mes ya fue enviado. "
            "Si cambias el **mes** o el **año**, verás de nuevo las tablas para ese periodo. 😉"
        )

    st.markdown("---")

    # Si no hay datos, no mostramos botones
    if df_v_mes.empty and df_c_mes.empty:
        st.warning("No hay datos de ventas ni compras para este mes/año. Captura primero en las pestañas correspondientes.")
        return

    # ===== Botón: Descargar Excel =====
    excel_bytes = construir_excel(mes_sel, año_sel, df_v_mes, df_c_mes)
    nombre_archivo = f"Resumen_Impresos_{mes_sel}_{año_sel}.xlsx"

    descargado = st.download_button(
        label="⬇️ Descargar Excel",
        data=excel_bytes,
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    # Si quieres que solo el download oculte tablas, deja esto.
    if descargado:
        ss["resumen_ocultar_tablas"] = True

    st.markdown("")

    # ===== Botón: mandar info a Análisis y limpiar tablas =====
    if st.button("➡️ Ir a Análisis", use_container_width=True):
        # Nos aseguramos de que existan las listas históricas
        ss.setdefault("ventas_historicas", [])
        ss.setdefault("compras_historicas", [])

        # 1) Pasar registros del mes actual a histórico (Análisis)
        if not df_v_mes.empty:
            ss["ventas_historicas"].extend(df_v_mes.to_dict(orient="records"))

        if not df_c_mes.empty:
            ss["compras_historicas"].extend(df_c_mes.to_dict(orient="records"))

        # 2) Quitar esas filas de las listas principales (ingresos/compras)
        ss["ingresos"] = [
            r for r in ss.get("ingresos", [])
            if not (r.get("Año") == año_sel and r.get("Mes") == mes_sel)
        ]
        ss["compras"] = [
            r for r in ss.get("compras", [])
            if not (r.get("Año") == año_sel and r.get("Mes") == mes_sel)
        ]

        # 3) Marcar tablas como ocultas para dejar el resumen “limpio”
        ss["resumen_ocultar_tablas"] = True

        # 4) Redirigir a la pestaña de Análisis
        ss["page"] = "Análisis"