import streamlit as st
import pandas as pd  # por si lo usas en las otras páginas

# Páginas de la app
from ingresos_page import ingresos_page
from compras_page import compras_page
from resumen_excel_page import resumen_excel_page
from analisis_page import analisis_page
from historial_page import historial_page

# Login / roles
from loginpassword import login_page, get_user_role


# -------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Impresos Mendieta - Panel interno",
    layout="wide",
    page_icon="🧾",
)

# -------------------------------------------------------------------
# CSS GLOBAL
# -------------------------------------------------------------------
st.markdown(
    """
<style>
/* Fondo general oscuro en gradient */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #1f2937 0, #020617 55%, #000 100%);
    color: #e5e7eb;
}

/* Quitar barra blanca de arriba */
[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid rgba(148, 163, 184, 0.2);
}

/* Títulos/ayuda sidebar */
.sidebar-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #e5e7eb;
}
.sidebar-help {
    font-size: 0.8rem;
    color: #9ca3af;
}

/* Radio en sidebar como píldoras */
div[data-baseweb="radio"] > div {
    gap: 0.4rem;
}
div[data-baseweb="radio"] label {
    border-radius: 999px;
    padding: 0.3rem 0.9rem !important;
    border: 1px solid rgba(148,163,184,0.4);
    background: #020617;
    color: #e5e7eb;
    font-size: 0.9rem;
}
div[data-baseweb="radio"] label[data-selected="true"] {
    background: linear-gradient(135deg, #0ea5e9, #22c55e);
    border-color: transparent;
    color: white !important;
}

/* Tarjetas */
.card {
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    background: radial-gradient(circle at top left, #111827 0, #020617 65%);
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.75);
}
.card-soft {
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(55, 65, 81, 0.7);
}

/* Dots tipo ventana */
.dots-wrapper {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.8rem;
}
.dot {
    width: 11px;
    height: 11px;
    border-radius: 999px;
}
.dot.red { background: #f97373; }
.dot.yellow { background: #facc15; }
.dot.green { background: #4ade80; }

/* Título principal */
.app-title {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: 0.03em;
    margin-bottom: 0.2rem;
}
.app-title span.brand {
    font-family: "SF Pro Display", system-ui, -apple-system, BlinkMacSystemFont;
    font-weight: 800;
    color: #38bdf8;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.22rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    color: #e5e7eb;
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.7);
}
</style>
""",
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# PÁGINA HOME
# -------------------------------------------------------------------
def home_page():
    # Dots tipo ventana
    st.markdown(
        "<div class='dots-wrapper'><span class='dot red'></span>"
        "<span class='dot yellow'></span><span class='dot green'></span></div>",
        unsafe_allow_html=True,
    )

    # Título principal
    col_logo, col_title = st.columns([0.15, 1])
    with col_logo:
        st.markdown("🧾", unsafe_allow_html=True)
    with col_title:
        st.markdown(
            "<div class='app-title'>Home - "
            "<span class='brand'>Impresos</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "Panel principal para controlar tus **ventas** y **compras** "
            "del negocio de impresión y papelería."
        )

    st.markdown("")
    st.markdown("")

    # Bloque superior
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<span class='badge'>📌 Flujo del mes</span>", unsafe_allow_html=True)
        st.markdown("## Resumen operativo en un solo lugar")
        st.write(
            """
Captura facturas de **ventas**, registra **compras** de papel, tintas e insumos,
genera tu **Excel mensual** y revisa el comportamiento del negocio con el módulo
de **análisis**.

Usa el menú de la izquierda como si fuera el “índice” de la carpeta mensual de
Impresos Mendieta.
"""
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='card-soft'>", unsafe_allow_html=True)
        st.markdown("<span class='badge'>🧭 Atajos rápidos</span>", unsafe_allow_html=True)
        st.markdown("#### ¿Qué quieres hacer ahora?")

        col_b1, col_b2 = st.columns(2)

        with col_b1:
            if st.button("🧾 Capturar ventas", use_container_width=True):
                st.session_state["page"] = "Ventas"
                st.rerun()

        with col_b2:
            if st.button("📦 Registrar compras", use_container_width=True):
                st.session_state["page"] = "Compras"
                st.rerun()

        st.markdown("")
        if st.button("📊 Ir a resumen contable (Excel)", use_container_width=True):
            st.session_state["page"] = "Resumen Excel"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("---")

    # Bloque inferior
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='card-soft'>", unsafe_allow_html=True)
        st.markdown("<span class='badge'>📈 Ventas</span>", unsafe_allow_html=True)
        st.markdown("### Control de facturas de ingreso")
        st.write(
            "Registra las facturas emitidas a **escuelas, empresas y clientes** "
            "para saber cuánto se facturó cada mes."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card-soft'>", unsafe_allow_html=True)
        st.markdown("<span class='badge'>📉 Compras</span>", unsafe_allow_html=True)
        st.markdown("### Insumos, material y egresos")
        st.write(
            "Captura las compras de **papel, tintas, placas, insumos** y servicios. "
            "Así ves cuánto cuesta sostener la operación."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='card-soft'>", unsafe_allow_html=True)
        st.markdown("<span class='badge'>📊 Excel & Análisis</span>", unsafe_allow_html=True)
        st.markdown("### Resumen y visualización")
        st.write(
            "En **Resumen Excel** generas el archivo mensual, y en **Análisis** "
            "ves los totales por mes y por año."
        )
        st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# ROUTER PRINCIPAL + AUTH
# -------------------------------------------------------------------
def main():
    ss = st.session_state

    # Estado de autenticación base
    if "logged_in" not in ss:
        ss["logged_in"] = False
        ss["current_user"] = None
        ss["current_role"] = "user"

    # Si NO está logueado → solo pantalla de login
    if not ss["logged_in"]:
        with st.sidebar:
            st.markdown("<div class='sidebar-title'>Acceso</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='sidebar-help'>Ingresa con tu usuario para usar el panel.</div>",
                unsafe_allow_html=True,
            )
        login_page()
        return

    # Ya autenticado → determinamos rol real
    username = ss.get("current_user")
    role_code = get_user_role(username)
    ss["current_role"] = role_code

    role_label = "Dueño / Admin" if role_code == "admin" else "Operación"

    # Páginas según rol
    pages_admin = ["Home", "Ventas", "Compras", "Resumen Excel", "Análisis", "Histórico"]
    pages_user = ["Home", "Ventas", "Compras", "Resumen Excel"]

    pages = pages_admin if role_code == "admin" else pages_user

    if "page" not in ss or ss["page"] not in pages:
        ss["page"] = "Home"

    # Callback del radio
    def on_nav_change():
        ss["page"] = ss["nav_radio"]

    # Sidebar completo
    with st.sidebar:
        st.markdown(
            f"<div class='sidebar-title'>Hola, {username} 👋</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='sidebar-help'>Rol: {role_label}</div>",
            unsafe_allow_html=True,
        )

        # Botón cerrar sesión
        if st.button("Cerrar sesión"):
            for k in ["logged_in", "authenticated", "current_user", "current_role", "page"]:
                ss.pop(k, None)
            st.rerun()

        st.markdown("---", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-title'>Navegación</div>", unsafe_allow_html=True)

        current_page = ss["page"]
        if current_page not in pages:
            current_page = "Home"
        default_index = pages.index(current_page)

        st.radio(
            "Ir a:",
            pages,
            index=default_index,
            key="nav_radio",
            on_change=on_nav_change,
            label_visibility="collapsed",
        )
        st.markdown(
            "<div class='sidebar-help'>Selecciona la sección que quieras trabajar este mes.</div>",
            unsafe_allow_html=True,
        )

    # Router según page
    page = ss["page"]
    if page == "Home":
        home_page()
    elif page == "Ventas":
        ingresos_page()
    elif page == "Compras":
        compras_page()
    elif page == "Resumen Excel":
        resumen_excel_page()
    elif page == "Análisis" and role_code == "admin":
        analisis_page()
    elif page == "Histórico" and role_code == "admin":
        historial_page()
    else:
        # por si alguien intenta forzar URL a una página que no debería ver
        st.error("No tienes permisos para ver esta sección.")


if __name__ == "__main__":
    main()