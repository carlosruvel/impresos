# ============================
#  LOGIN / AUTH IMPRESOS
# ============================
import json
import hashlib
from pathlib import Path

import streamlit as st

# Archivo JSON de usuarios
USERS_FILE = Path("data/usuarios.json")
USERS_FILE.parent.mkdir(parents=True, exist_ok=True)


# ---------- utils de storage ----------

def _load_users() -> dict:
    """Carga usuarios desde el JSON."""
    if not USERS_FILE.exists():
        return {}

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}

    # Normalizamos estructura:
    # username -> {password, role, nombre, apellidos, email, telefono, pais}
    users = {}
    for user, info in data.items():
        if isinstance(info, str):
            users[user] = {
                "password": info,
                "role": "user",
                "nombre": "",
                "apellidos": "",
                "email": "",
                "telefono": "",
                "pais": "",
            }
        elif isinstance(info, dict):
            pwd_hash = (
                info.get("password_hash")
                or info.get("password")
                or ""
            )
            users[user] = {
                "password": pwd_hash,
                "role": info.get("role", "user"),
                "nombre": info.get("nombre", ""),
                "apellidos": info.get("apellidos", ""),
                "email": info.get("email", ""),
                "telefono": info.get("telefono", ""),
                "pais": info.get("pais", ""),
            }
    return users


def _save_users(users: dict) -> None:
    """Guarda usuarios en el JSON."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _verify_password(password: str, stored_hash: str) -> bool:
    return _hash_password(password) == (stored_hash or "")


# ---------- helpers públicos ----------

def get_user_role(username: str) -> str:
    """Devuelve el rol del usuario leyendo directo del JSON."""
    if not username:
        return "user"
    users = _load_users()
    return users.get(username, {}).get("role", "user")


# ---------- PANTALLA DE LOGIN / REGISTRO ----------

def login_page():
    """
    Pantalla de acceso.

    - Si NO hay usuarios → crea el primer admin.
    - Si ya hay usuarios → muestra login normal.
    - Desde login se puede ir a:
        * Crear cuenta (registro)
        * "¿Olvidaste tu contraseña?" (info para resetearla manualmente)
    """
    ss = st.session_state
    if "auth_mode" not in ss:
        ss["auth_mode"] = "login"  # "primer_usuario", "login", "registro", "forgot"

    users = _load_users()
    hay_usuarios = len(users) > 0

    # Si no hay usuarios → forzamos modo "primer usuario admin"
    if not hay_usuarios:
        ss["auth_mode"] = "primer_usuario"

    # Sidebar mini
    st.sidebar.title("Acceso")
    st.sidebar.write("Ingresa con tu usuario para usar el panel.")

    st.markdown("")
    st.markdown("")

    col_left, col_center, col_right = st.columns([1, 1.3, 1])

    with col_center:
        # ---------- tarjeta principal ----------
        st.markdown(
            """
            <div style="
                border-radius: 20px;
                padding: 2.2rem 2.4rem;
                background: rgba(15,23,42,0.95);
                border: 1px solid rgba(148,163,184,0.35);
                box-shadow: 0 18px 45px rgba(15,23,42,0.85);
            ">
            """,
            unsafe_allow_html=True,
        )

        # avatar + título
        st.markdown(
            """
            <div style="text-align:center; margin-bottom: 1.5rem;">
                <div style="
                    width: 90px; height: 90px;
                    border-radius: 999px;
                    background: radial-gradient(circle at 30% 20%, #38bdf8, #1f2937);
                    display:flex; align-items:center; justify-content:center;
                    margin: 0 auto 0.8rem auto;
                    font-size: 2.6rem;
                ">🔐</div>
                <div style="font-size: 1.8rem; font-weight: 800;">
                    Acceso a Impresos
                </div>
                <div style="font-size: 0.9rem; color: #9ca3af; margin-top: 0.25rem;">
                    Inicia sesión para ver ventas, compras y reportes.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ---------- CREAR PRIMER USUARIO ADMIN ----------
        if ss["auth_mode"] == "primer_usuario":
            # Este mensaje solo aparece la PRIMERA vez (cuando no hay usuarios)
            st.info(
                "No hay usuarios registrados todavía. "
                "Crea el **primer usuario administrador** para empezar a usar el sistema."
            )

            username = st.text_input("Usuario administrador")
            pwd = st.text_input("Contraseña", type="password")
            pwd2 = st.text_input("Confirmar contraseña", type="password")

            error_msg = None

            if st.button("Crear usuario y entrar", use_container_width=True):
                if not username or not pwd or not pwd2:
                    error_msg = "Usuario y contraseña son obligatorios."
                elif pwd != pwd2:
                    error_msg = "Las contraseñas no coinciden."
                elif username in users:
                    error_msg = "Ese usuario ya existe. Elige otro."
                else:
                    users[username] = {
                        "password": _hash_password(pwd),
                        "role": "admin",
                        "nombre": "",
                        "apellidos": "",
                        "email": "",
                        "telefono": "",
                        "pais": "",
                    }
                    _save_users(users)
                    ss["logged_in"] = True
                    ss["authenticated"] = True
                    ss["current_user"] = username
                    ss["current_role"] = "admin"
                    st.success("Usuario creado. Redirigiendo al panel...")
                    st.rerun()

            if error_msg:
                st.error(error_msg)

        # ---------- MODOS NORMALES: LOGIN / REGISTRO / FORGOT ----------
        else:
            mode = ss["auth_mode"]

            # ----- LOGIN -----
            if mode == "login":
                usuario = st.text_input("Usuario")
                pwd = st.text_input("Contraseña", type="password")

                error_msg = None

                if st.button("Entrar al panel", use_container_width=True):
                    if not usuario or not pwd:
                        error_msg = "Usuario y contraseña son obligatorios."
                    elif usuario not in users:
                        error_msg = "Usuario no encontrado."
                    else:
                        stored = users[usuario]["password"]
                        if not _verify_password(pwd, stored):
                            error_msg = "Contraseña incorrecta."
                        else:
                            ss["logged_in"] = True
                            ss["authenticated"] = True
                            ss["current_user"] = usuario
                            ss["current_role"] = users[usuario].get("role", "user")
                            st.success("Bienvenido. Cargando el panel…")
                            st.rerun()

                if error_msg:
                    st.error(error_msg)

                # Links de crear cuenta / olvidaste contraseña
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Crear cuenta nueva", use_container_width=True):
                        ss["auth_mode"] = "registro"
                        st.rerun()
                with c2:
                    if st.button("¿Olvidaste tu contraseña?", use_container_width=True):
                        ss["auth_mode"] = "forgot"
                        st.rerun()

            # ----- REGISTRO -----
            elif mode == "registro":
                st.markdown(
                    "<div style='font-size:0.9rem; color:#9ca3af; margin-bottom:0.6rem;'>"
                    "Completa tus datos para crear una cuenta."
                    "</div>",
                    unsafe_allow_html=True,
                )

                new_user = st.text_input("Usuario")
                nombre = st.text_input("Nombre(s)")
                apellidos = st.text_input("Apellidos")
                email = st.text_input("Correo electrónico")
                telefono = st.text_input("Número de celular")
                pais = st.text_input("País")

                new_pwd = st.text_input("Contraseña", type="password")
                new_pwd2 = st.text_input("Confirmar contraseña", type="password")

                error_msg = None
                if st.button("Crear cuenta", use_container_width=True):
                    if not new_user or not new_pwd or not new_pwd2:
                        error_msg = "Usuario y contraseña son obligatorios."
                    elif new_pwd != new_pwd2:
                        error_msg = "Las contraseñas no coinciden."
                    elif new_user in users:
                        error_msg = "Ese usuario ya existe. Elige otro."
                    else:
                        users[new_user] = {
                            "password": _hash_password(new_pwd),
                            "role": "user",
                            "nombre": nombre,
                            "apellidos": apellidos,
                            "email": email,
                            "telefono": telefono,
                            "pais": pais,
                        }
                        _save_users(users)
                        st.success(
                            "Cuenta creada. Ahora inicia sesión con tu nuevo usuario."
                        )
                        ss["auth_mode"] = "login"
                        st.rerun()

                if error_msg:
                    st.error(error_msg)

                if st.button("← Ya tengo cuenta, ir al login", use_container_width=True):
                    ss["auth_mode"] = "login"
                    st.rerun()

            # ----- FORGOT PASSWORD (info) -----
            elif mode == "forgot":
                st.markdown(
                    """
                    <div style="font-size:0.9rem; color:#e5e7eb; margin-bottom:0.6rem;">
                        <strong>Recuperar acceso</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.write(
                    "Por seguridad, la contraseña se reinicia sólo por el administrador "
                    "del sistema. Escribe tu usuario y un medio de contacto para que "
                    "te apoyen a resetearla."
                )
                _u = st.text_input("Tu usuario")
                _contact = st.text_area("Correo o número de teléfono de contacto")

                st.info(
                    "Cuando haya un flujo formal, el administrador puede cambiar tu "
                    "contraseña directamente en el archivo de usuarios."
                )

                if st.button("← Regresar al login", use_container_width=True):
                    ss["auth_mode"] = "login"
                    st.rerun()

        # cierre tarjeta
        st.markdown("</div>", unsafe_allow_html=True)