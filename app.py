import uuid
import os
import re
import base64
import json
from pathlib import Path
from datetime import date, datetime, timedelta
from collections import Counter
from io import StringIO
from urllib.parse import quote, urlparse

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import altair as alt
from supabase import Client, create_client

st.set_page_config(
    page_title="Méthamorphoz",
    page_icon="🏭",
    layout="centered",
    initial_sidebar_state="collapsed",
)


BRAND_PRIMARY = "#8F5AA8"
BRAND_PRIMARY_DARK = "#6F3F86"
BRAND_TEXT = "#2E2A36"
BRAND_MUTED = "#7A7288"
BRAND_BG = "#F7F4FA"
BRAND_BORDER = "#E4DDED"
BRAND_SURFACE = "#FFFFFF"


def apply_brand_theme() -> None:
    st.markdown(
        f"""
        <style>
            .stApp {{
                background: linear-gradient(180deg, #FFFFFF 0%, {BRAND_BG} 100%);
                color: {BRAND_TEXT};
            }}

            [data-testid="stHeader"] {{
                background: rgba(255, 255, 255, 0.85);
                border-bottom: 1px solid {BRAND_BORDER};
                backdrop-filter: blur(8px);
            }}

            [data-testid="block-container"] {{
                padding-top: 1.4rem;
                padding-bottom: 2rem;
            }}

            h1, h2, h3, h4, h5, h6 {{
                color: {BRAND_TEXT};
            }}

            div.stButton > button {{
                min-height: 48px;
                font-weight: 600;
                border-radius: 12px;
                border: 1px solid {BRAND_BORDER};
                background: {BRAND_SURFACE};
                color: {BRAND_TEXT};
                box-shadow: 0 8px 20px rgba(111, 63, 134, 0.06);
            }}

            div.stButton > button:hover {{
                border-color: {BRAND_PRIMARY};
                color: {BRAND_PRIMARY_DARK};
            }}

            div.stButton > button[kind="primary"] {{
                background: linear-gradient(135deg, {BRAND_PRIMARY_DARK} 0%, {BRAND_PRIMARY} 100%);
                color: #FFFFFF;
                border-color: {BRAND_PRIMARY_DARK};
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.5rem;
            }}

            .stTabs [data-baseweb="tab"] {{
                background: #FFFFFF;
                border: 1px solid {BRAND_BORDER};
                border-radius: 10px;
                padding: 0.35rem 0.8rem;
            }}

            .stTabs [aria-selected="true"] {{
                border-color: {BRAND_PRIMARY};
                color: {BRAND_PRIMARY_DARK};
                font-weight: 700;
            }}

            [data-testid="stMetric"] {{
                background: {BRAND_SURFACE};
                border: 1px solid {BRAND_BORDER};
                border-radius: 12px;
                padding: 0.6rem;
                box-shadow: 0 6px 16px rgba(111, 63, 134, 0.06);
            }}

            [data-testid="stAlert"] {{
                border-radius: 12px;
            }}

            [data-testid="stTextInputRootElement"] > div,
            [data-testid="stNumberInput"] > div,
            [data-baseweb="select"] > div,
            [data-testid="stDateInput"] > div,
            [data-testid="stTextArea"] textarea,
            [data-testid="stDataFrame"] {{
                border-radius: 12px !important;
                border: 1px solid {BRAND_BORDER} !important;
                background: {BRAND_SURFACE} !important;
            }}

            [data-testid="stDataFrame"] {{
                box-shadow: 0 6px 16px rgba(111, 63, 134, 0.05);
            }}

            .brand-hero {{
                background: linear-gradient(135deg, rgba(143, 90, 168, 0.12) 0%, rgba(255, 255, 255, 0.95) 65%);
                border: 1px solid {BRAND_BORDER};
                border-radius: 18px;
                padding: 1rem 1.1rem 0.8rem 1.1rem;
                box-shadow: 0 10px 28px rgba(111, 63, 134, 0.08);
                margin-bottom: 0.9rem;
            }}

            .brand-badge {{
                display: inline-block;
                margin-top: 0.4rem;
                padding: 0.22rem 0.55rem;
                border-radius: 999px;
                border: 1px solid {BRAND_BORDER};
                color: {BRAND_PRIMARY_DARK};
                background: rgba(255, 255, 255, 0.92);
                font-size: 0.78rem;
                font-weight: 600;
            }}

            .brand-title {{
                margin: 0.1rem 0 0 0;
                color: {BRAND_PRIMARY_DARK};
                letter-spacing: 0.04em;
                font-weight: 800;
            }}

            .brand-subtitle {{
                margin: 0.15rem 0 0.5rem 0;
                color: {BRAND_MUTED};
                font-size: 0.94rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header() -> None:
    logo_candidates = [
        Path("assets/methamorphoz-logo.svg"),
        Path("assets/methamorphoz-logo.png"),
        Path("assets/methamorphoz-logo.jpg"),
        Path("assets/methamorphoz-logo.jpeg"),
        Path("assets/methamorphoz-logo.webp"),
        Path("assets/logo.png"),
        Path("logo.png"),
        Path(".streamlit/logo.png"),
    ]

    logo_path = next((candidate for candidate in logo_candidates if candidate.exists()), None)
    st.markdown('<div class="brand-hero">', unsafe_allow_html=True)
    left, right = st.columns([1.3, 2.2])
    with left:
        if logo_path:
            try:
                logo_bytes = logo_path.read_bytes()
                header = logo_bytes[:32]
                header_lower = header.lower()

                if b"<svg" in header_lower:
                    svg_b64 = base64.b64encode(logo_bytes).decode("ascii")
                    st.markdown(
                        f"""
                        <div style="display:flex; align-items:center; justify-content:flex-start;">
                            <img src="data:image/svg+xml;base64,{svg_b64}" style="width:100%; max-width:260px; height:auto;" />
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.image(logo_bytes, use_container_width=True)
            except Exception:
                st.caption("Logo indisponible")
    with right:
        st.markdown(
            f"""
            <h2 class="brand-title">METHAMORPHOZ</h2>
            <p class="brand-subtitle">Pilotage de production • Ration • Historique • Administration</p>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)


apply_brand_theme()

st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown('<meta name="google" content="notranslate" />', unsafe_allow_html=True)
components.html(
    """
    <script>
        (function () {
            try {
                const doc = window.parent && window.parent.document ? window.parent.document : document;
                if (!doc || !doc.documentElement) return;
                doc.documentElement.setAttribute("translate", "no");
                if (doc.body) {
                    doc.body.setAttribute("translate", "no");
                }
            } catch (e) {
            }
        })();
    </script>
    """,
    height=0,
)

render_brand_header()

REACTEURS = [f"C{i}" for i in range(1, 11)]
TBL_REF = "referentiel_ingredients"
TBL_FICHE = "fiche_ration"
TBL_SAISIES = "saisies_production"
TBL_REGISTRE_ENTREES = "registre_entrees"
TBL_MAINTENANCE = "maintenance_hourly_data"
TBL_SECURITE_TORCHERE = "securite_torchere_data"
TBL_ENERGIE = "energie_data"
TORCHERE_DEFAULT_MODEL = "hourly_counter_value"
TORCHERE_DEFAULT_GROUP_ID = "343"
TORCHERE_DEFAULT_GROUP_DUAL = "337"
TORCHERE_DEFAULT_GROUP_STRAWBERRY = "343"
TORCHERE_LOOKBACK_DAYS = 900
TORCHERE_WORKSPACE_GROUP_MAP = {
    "10": TORCHERE_DEFAULT_GROUP_DUAL,
    "41": TORCHERE_DEFAULT_GROUP_STRAWBERRY,
}
ENERGIE_DEFAULT_MODELS = {
    "process": "energy_integrator",
    "epurateur": "energy_integrator",
    "biomethane": "volume",
}
ENERGIE_MODEL_CANDIDATES = ["energy_integrator", "energy_meter", "energy_index", "energy_integrator_value"]
ENERGIE_LOOKBACK_DAYS = 600
ENERGIE_DATE_COLUMN_INDEX = 1
ENERGIE_EPURATION_COLUMN_INDEX = 2
ENERGIE_PROCESS_COLUMN_INDEX = 4
ENERGIE_BIOMETHANE_COLUMN_INDEX = 2
ENERGIE_BIOGAZ_COLUMN_INDEX = 4
ENERGIE_ELECTRICITY_EXPORT_UNIT = "kWh"
ENERGIE_BIOMETHANE_EXPORT_UNIT = "m³"
ENERGIE_REJECT_TORCHERE_COLUMNS = True
ENERGIE_DEFAULT_GROUP_DUAL = "337"
ENERGIE_DEFAULT_GROUP_STRAWBERRY = "343"
ENERGIE_WORKSPACE_GROUP_MAP = {
    "10": ENERGIE_DEFAULT_GROUP_DUAL,
    "41": ENERGIE_DEFAULT_GROUP_STRAWBERRY,
}
MS_OUTPUT_FACTOR = 100.0
POTENTIEL_OUTPUT_FACTOR = 10000.0

MODULES = [
    "Ration",
    "Entrées/Sorties",
    "Qualité",
    "Maintenance",
    "Sécurité",
    "Energie",
]

ROLES = ["agent", "mainteneur", "coordinateur", "tiers", "administrateur"]

MENU_KEYS = {
    "Ration": "ration",
    "Entrées/Sorties": "entrees_sorties",
    "Qualité": "qualite",
    "Maintenance": "maintenance",
    "Sécurité": "securite",
    "Energie": "energie",
    "Administration": "administration",
}

MENU_LABEL_BY_KEY = {value: key for key, value in MENU_KEYS.items()}

RIGHTS_ITEMS = [
    ("ration", ""),
    ("ration", "admin"),
    ("ration", "operateur"),
    ("ration", "historique"),
    ("entrees_sorties", ""),
    ("entrees_sorties", "stock"),
    ("entrees_sorties", "registre_entrees"),
    ("entrees_sorties", "registre_sorties"),
    ("qualite", ""),
    ("maintenance", ""),
    ("securite", ""),
    ("securite", "sync"),
    ("securite", "debug"),
    ("energie", ""),
    ("energie", "sync"),
    ("energie", "debug"),
    ("administration", ""),
    ("administration", "sites"),
    ("administration", "utilisateurs"),
    ("administration", "droits"),
]


def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()

    if not url or not key:
        try:
            url = str(st.secrets["SUPABASE_URL"]).strip()
            key = str(st.secrets["SUPABASE_KEY"]).strip()
        except Exception as error:
            raise RuntimeError(
                "Clés SUPABASE_URL / SUPABASE_KEY absentes (variables d'environnement ou st.secrets)."
            ) from error

    return create_client(url, key)


def get_supabase_admin_client() -> Client:
    url = os.getenv("SUPABASE_URL", "").strip()
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

    if not url or not service_key:
        try:
            url = str(st.secrets["SUPABASE_URL"]).strip()
            service_key = str(st.secrets["SUPABASE_SERVICE_ROLE_KEY"]).strip()
        except Exception as error:
            raise RuntimeError(
                "SUPABASE_SERVICE_ROLE_KEY absent. Impossible de créer un utilisateur sans envoi d'email."
            ) from error

    return create_client(url, service_key)


def to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except Exception:
        return False


def compute_kpis(tonnage: float, ms_pct: float, mo_pct: float, bmp_nm3_t: float, masse_volumique_t_m3: float) -> dict:
    tonnage = max(to_float(tonnage), 0.0)
    ms_pct = max(to_float(ms_pct), 0.0)
    mo_pct = max(to_float(mo_pct), 0.0)
    bmp_nm3_t = max(to_float(bmp_nm3_t), 0.0)
    masse_volumique_t_m3 = to_float(masse_volumique_t_m3)

    tonnage_ms_t_raw = tonnage * (ms_pct / 100.0)
    potentiel_nm3_raw = tonnage_ms_t_raw * (mo_pct / 100.0) * bmp_nm3_t
    volume_m3 = tonnage / masse_volumique_t_m3 if masse_volumique_t_m3 > 0 else 0.0

    tonnage_ms_t = tonnage_ms_t_raw * MS_OUTPUT_FACTOR
    potentiel_nm3 = potentiel_nm3_raw * POTENTIEL_OUTPUT_FACTOR

    return {
        "tonnage_ms_t": round(tonnage_ms_t, 3),
        "potentiel_nm3": round(potentiel_nm3, 3),
        "volume_m3": round(volume_m3, 3),
    }


def aggregate_kpis(rows: list[dict], tonnage_field: str) -> dict:
    total_ms_t = 0.0
    total_potentiel_nm3 = 0.0
    total_volume_m3 = 0.0

    for row in rows:
        kpi = compute_kpis(
            tonnage=to_float(row.get(tonnage_field), 0.0),
            ms_pct=to_float(row.get("ms_pct"), 0.0),
            mo_pct=to_float(row.get("mo_pct"), 0.0),
            bmp_nm3_t=to_float(row.get("bmp_nm3_t"), 0.0),
            masse_volumique_t_m3=to_float(row.get("masse_volumique_t_m3"), 0.0),
        )
        total_ms_t += kpi["tonnage_ms_t"]
        total_potentiel_nm3 += kpi["potentiel_nm3"]
        total_volume_m3 += kpi["volume_m3"]

    return {
        "total_ms_t": round(total_ms_t, 3),
        "total_potentiel_nm3": round(total_potentiel_nm3, 3),
        "total_volume_m3": round(total_volume_m3, 3),
    }


def insert_with_schema_fallback(client: Client, table_name: str, payload: list[dict], max_attempts: int = 10) -> None:
    if not payload:
        return

    working_payload = [dict(row) for row in payload]

    for _ in range(max_attempts):
        try:
            client.table(table_name).insert(working_payload).execute()
            return
        except Exception as error:
            error_text = str(error)
            match = re.search(r"Could not find the '([^']+)' column", error_text)
            if not match:
                bigint_match = re.search(r'invalid input syntax for type bigint: "([^"]+)"', error_text)
                if not bigint_match:
                    raise

                bad_value = bigint_match.group(1)
                removed = False
                for row in working_payload:
                    for key in list(row.keys()):
                        if str(row.get(key)) == bad_value:
                            del row[key]
                            removed = True

                if not removed:
                    raise

                continue

            missing_column = match.group(1)
            removed = False
            for row in working_payload:
                if missing_column in row:
                    del row[missing_column]
                    removed = True

            if not removed:
                raise

    raise RuntimeError(f"Insertion impossible dans {table_name}: trop de colonnes absentes dans le schéma.")


def init_auth_session() -> None:
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "auth_user_id" not in st.session_state:
        st.session_state.auth_user_id = ""
    if "auth_email" not in st.session_state:
        st.session_state.auth_email = ""
    if "selected_site_id" not in st.session_state:
        st.session_state.selected_site_id = ""
    if "site_roles_map" not in st.session_state:
        st.session_state.site_roles_map = {}
    if "auth_access_token" not in st.session_state:
        st.session_state.auth_access_token = ""
    if "auth_refresh_token" not in st.session_state:
        st.session_state.auth_refresh_token = ""


def _auth_session_file() -> Path:
    return Path(".streamlit/auth_session.json")


def clear_persisted_auth_session() -> None:
    try:
        auth_file = _auth_session_file()
        if auth_file.exists():
            auth_file.unlink()
    except Exception:
        pass


def save_persisted_auth_session(remember_me: bool) -> None:
    if not remember_me:
        clear_persisted_auth_session()
        return

    access_token = str(st.session_state.get("auth_access_token", "") or "").strip()
    refresh_token = str(st.session_state.get("auth_refresh_token", "") or "").strip()
    if not access_token or not refresh_token:
        return

    payload = {
        "auth_user_id": str(st.session_state.get("auth_user_id", "") or "").strip(),
        "auth_email": str(st.session_state.get("auth_email", "") or "").strip(),
        "auth_access_token": access_token,
        "auth_refresh_token": refresh_token,
    }

    try:
        auth_file = _auth_session_file()
        auth_file.parent.mkdir(parents=True, exist_ok=True)
        auth_file.write_text(json.dumps(payload), encoding="utf-8")
    except Exception:
        pass


def load_persisted_auth_session() -> dict:
    try:
        auth_file = _auth_session_file()
        if not auth_file.exists():
            return {}
        data = json.loads(auth_file.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        return {}


def try_restore_auth_session(client: Client) -> bool:
    if st.session_state.is_authenticated:
        return True

    data = load_persisted_auth_session()
    access_token = str(data.get("auth_access_token", "") or "").strip()
    refresh_token = str(data.get("auth_refresh_token", "") or "").strip()
    if not access_token or not refresh_token:
        return False

    try:
        response = client.auth.set_session(access_token, refresh_token)
        session = getattr(response, "session", None)
        user = getattr(response, "user", None)

        if user is None:
            try:
                user_resp = client.auth.get_user()
                user = getattr(user_resp, "user", None)
            except Exception:
                user = None

        user_id = str(getattr(user, "id", "") or "").strip() if user else ""
        user_email = str(getattr(user, "email", "") or "").strip() if user else ""
        if not user_id:
            raise RuntimeError("Session restaurée invalide")

        st.session_state.is_authenticated = True
        st.session_state.auth_user_id = user_id
        st.session_state.auth_email = user_email
        st.session_state.auth_access_token = str(getattr(session, "access_token", access_token) or access_token)
        st.session_state.auth_refresh_token = str(getattr(session, "refresh_token", refresh_token) or refresh_token)

        sync_user_profile(client, st.session_state.auth_user_id, st.session_state.auth_email)
        save_persisted_auth_session(True)
        return True
    except Exception:
        clear_auth_session()
        clear_persisted_auth_session()
        return False


def clear_auth_session() -> None:
    st.session_state.is_authenticated = False
    st.session_state.auth_user_id = ""
    st.session_state.auth_email = ""
    st.session_state.selected_site_id = ""
    st.session_state.site_roles_map = {}
    st.session_state.auth_access_token = ""
    st.session_state.auth_refresh_token = ""
    go_home()


def sync_user_profile(client: Client, user_id: str, email: str) -> None:
    payload = [{"user_id": user_id, "email": email, "is_active": True}]
    try:
        client.table("app_user_profiles").upsert(payload).execute()
    except Exception:
        insert_with_schema_fallback(client, "app_user_profiles", payload)


def sign_in_user(client: Client, email: str, password: str, remember_me: bool = True) -> None:
    response = client.auth.sign_in_with_password({"email": email, "password": password})
    user = getattr(response, "user", None)
    session = getattr(response, "session", None)
    if not user:
        raise RuntimeError("Authentification impossible.")

    st.session_state.is_authenticated = True
    st.session_state.auth_user_id = str(user.id)
    st.session_state.auth_email = str(getattr(user, "email", email))
    st.session_state.auth_access_token = str(getattr(session, "access_token", "") or "")
    st.session_state.auth_refresh_token = str(getattr(session, "refresh_token", "") or "")
    sync_user_profile(client, st.session_state.auth_user_id, st.session_state.auth_email)
    save_persisted_auth_session(remember_me)


def sign_out_user(client: Client) -> None:
    try:
        client.auth.sign_out()
    except Exception:
        pass
    clear_persisted_auth_session()
    clear_auth_session()


def confirm_user_email_as_admin(client: Client, email: str) -> bool:
    try:
        response = client.rpc("app_confirm_user_email", {"p_email": email}).execute()
        data = response.data
        if isinstance(data, bool):
            return data
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, bool):
                return first
        return bool(data)
    except Exception:
        return False


def _read_value(record: object, key: str, default: object = "") -> object:
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)


def _extract_admin_users_list(users_page: object) -> list:
    if isinstance(users_page, dict):
        users = users_page.get("users", [])
        if isinstance(users, list):
            return users
        data = users_page.get("data", {})
        if isinstance(data, dict):
            nested_users = data.get("users", [])
            return nested_users if isinstance(nested_users, list) else []
        return []

    users = getattr(users_page, "users", None)
    if isinstance(users, list):
        return users

    data_attr = getattr(users_page, "data", None)
    if isinstance(data_attr, dict):
        nested_users = data_attr.get("users", [])
        if isinstance(nested_users, list):
            return nested_users
    else:
        nested_users = getattr(data_attr, "users", None)
        if isinstance(nested_users, list):
            return nested_users

    if hasattr(users_page, "model_dump"):
        try:
            dumped = users_page.model_dump()
            if isinstance(dumped, dict):
                users = dumped.get("users", [])
                if isinstance(users, list):
                    return users
                data = dumped.get("data", {})
                if isinstance(data, dict):
                    nested_users = data.get("users", [])
                    return nested_users if isinstance(nested_users, list) else []
            return []
        except Exception:
            return []

    return []


def create_user_without_email(email: str, password: str) -> str:
    admin_client = get_supabase_admin_client()
    try:
        response = admin_client.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,
            }
        )

        user = _read_value(response, "user", None)
        user_id = str(_read_value(user, "id", "") or "").strip()
        if user_id:
            return user_id
    except Exception as error:
        error_text = str(error).lower()
        if "already" not in error_text and "exists" not in error_text and "registered" not in error_text:
            raise

    # Si l'utilisateur existe déjà, on tente de le retrouver via la liste admin
    try:
        page = 1
        while page <= 10:
            users_page = admin_client.auth.admin.list_users(page=page, per_page=100)
            users = _extract_admin_users_list(users_page)

            if not users:
                break

            for user in users:
                user_email = str(_read_value(user, "email", "") or "").strip().lower()
                if user_email == email.strip().lower():
                    user_id = str(_read_value(user, "id", "") or "").strip()
                    if user_id:
                        return user_id

            page += 1
    except Exception:
        pass

    raise RuntimeError("Utilisateur existant introuvable via l'API admin.")


def list_users_as_admin(max_pages: int = 20, per_page: int = 100) -> list[dict]:
    admin_client = get_supabase_admin_client()
    users_result: list[dict] = []

    page = 1
    while page <= max_pages:
        users_page = admin_client.auth.admin.list_users(page=page, per_page=per_page)
        users = _extract_admin_users_list(users_page)

        if not users:
            break

        for user in users:
            user_id = str(_read_value(user, "id", "") or "").strip()
            email = str(_read_value(user, "email", "") or "").strip().lower()
            email_confirmed_at = _read_value(user, "email_confirmed_at", None) or _read_value(user, "confirmed_at", None)
            last_sign_in_at = _read_value(user, "last_sign_in_at", None)

            if not user_id:
                continue

            users_result.append(
                {
                    "user_id": user_id,
                    "email": email,
                    "email_confirmed": bool(email_confirmed_at),
                    "last_sign_in_at": str(last_sign_in_at or ""),
                }
            )

        if len(users) < per_page:
            break

        page += 1

    users_result.sort(key=lambda row: (row.get("email", ""), row.get("user_id", "")))
    return users_result


def get_user_id_by_email_as_admin(email: str) -> str:
    lookup_email = email.strip().lower()
    if not lookup_email:
        return ""

    users = list_users_as_admin(max_pages=20, per_page=100)
    for row in users:
        row_email = str(row.get("email", "")).strip().lower()
        row_user_id = str(row.get("user_id", "")).strip()
        if row_email == lookup_email and row_user_id:
            return row_user_id
    return ""


def build_admin_users_view(client: Client) -> list[dict]:
    try:
        auth_users = list_users_as_admin()
    except Exception:
        auth_users = []

    try:
        profiles_rows = client.table("app_user_profiles").select("user_id, email, is_active").execute().data or []
    except Exception:
        profiles_rows = []

    users_map: dict[str, dict] = {}

    def ensure_row(user_id: str, email: str) -> dict:
        key = user_id or email
        if key not in users_map:
            users_map[key] = {
                "user_id": user_id,
                "email": email,
                "is_active": True,
                "email_confirmed": False,
                "last_sign_in_at": "",
            }
        return users_map[key]

    for row in auth_users:
        user_id = str(row.get("user_id", "")).strip()
        email = str(row.get("email", "")).strip().lower()
        if not user_id and not email:
            continue
        current = ensure_row(user_id, email)
        if user_id:
            current["user_id"] = user_id
        if email:
            current["email"] = email
        current["email_confirmed"] = bool(row.get("email_confirmed", False))
        current["last_sign_in_at"] = str(row.get("last_sign_in_at", "") or "")

    for row in profiles_rows:
        user_id = str(row.get("user_id", "")).strip()
        email = str(row.get("email", "")).strip().lower()
        if not user_id and not email:
            continue
        current = ensure_row(user_id, email)
        if user_id and not current.get("user_id"):
            current["user_id"] = user_id
        if email and not current.get("email"):
            current["email"] = email
        current["is_active"] = bool(row.get("is_active", True))

    users = list(users_map.values())
    users.sort(key=lambda item: (str(item.get("email", "")), str(item.get("user_id", ""))))
    return users


def delete_user_everywhere(client: Client, user_id: str) -> None:
    target_user_id = str(user_id).strip()
    if not target_user_id:
        raise RuntimeError("Identifiant utilisateur manquant.")

    if target_user_id == str(st.session_state.auth_user_id).strip():
        raise RuntimeError("Suppression de votre propre compte refusée.")

    try:
        client.table("app_user_site_roles").delete().eq("user_id", target_user_id).execute()
    except Exception:
        pass

    try:
        client.table("app_user_profiles").delete().eq("user_id", target_user_id).execute()
    except Exception:
        pass

    admin_client = get_supabase_admin_client()
    admin_client.auth.admin.delete_user(target_user_id)


def load_sites(client: Client) -> list[dict]:
    response = client.table("app_sites").select("id, code, name").order("name").execute()
    return response.data or []


def load_user_site_roles(client: Client, user_id: str) -> dict[str, list[str]]:
    try:
        response = client.table("app_user_site_roles").select("site_id, role").eq("user_id", user_id).execute()
    except Exception:
        return {}

    rows = response.data or []
    result: dict[str, list[str]] = {}
    for row in rows:
        site_id = str(row.get("site_id", "")).strip()
        role = str(row.get("role", "")).strip().lower()
        if not site_id or not role:
            continue
        if site_id not in result:
            result[site_id] = []
        if role not in result[site_id]:
            result[site_id].append(role)
    return result


def load_role_menu_rights(client: Client, roles: list[str]) -> set[tuple[str, str]]:
    if not roles:
        return set()

    try:
        response = (
            client.table("app_role_menu_rights")
            .select("role, menu_key, submenu_key, can_view")
            .in_("role", roles)
            .eq("can_view", True)
            .execute()
        )
    except Exception:
        return set()

    rows = response.data or []
    return {
        (str(row.get("menu_key", "")).strip(), str(row.get("submenu_key", "")).strip())
        for row in rows
        if str(row.get("menu_key", "")).strip()
    }


def has_permission(roles: list[str], rights: set[tuple[str, str]], menu_key: str, submenu_key: str = "") -> bool:
    if "administrateur" in roles:
        return True
    return (menu_key, submenu_key) in rights


def get_allowed_modules(roles: list[str], rights: set[tuple[str, str]]) -> list[str]:
    allowed = []
    for module_label in MODULES:
        menu_key = MENU_KEYS[module_label]
        if has_permission(roles, rights, menu_key, ""):
            allowed.append(module_label)
    return allowed


def ensure_default_rights_rows(client: Client) -> None:
    try:
        existing_rows = (
            client.table("app_role_menu_rights")
            .select("role, menu_key, submenu_key")
            .execute()
            .data
            or []
        )
    except Exception:
        existing_rows = []

    existing_keys: set[tuple[str, str, str]] = set()
    for row in existing_rows:
        role = str(row.get("role", "")).strip().lower()
        menu_key = str(row.get("menu_key", "")).strip()
        submenu_key = str(row.get("submenu_key", "")).strip()
        if role and menu_key:
            existing_keys.add((role, menu_key, submenu_key))

    payload = []
    for role in ROLES:
        for menu_key, submenu_key in RIGHTS_ITEMS:
            key = (role, menu_key, submenu_key)
            if key in existing_keys:
                continue
            payload.append(
                {
                    "role": role,
                    "menu_key": menu_key,
                    "submenu_key": submenu_key,
                    "can_view": role == "administrateur",
                }
            )

    if not payload:
        return

    try:
        client.table("app_role_menu_rights").insert(payload).execute()
    except Exception:
        pass


def load_referentiel(client: Client, site_id: str) -> tuple[list[str], dict[str, dict]]:
    try:
        query = client.table(TBL_REF).select("name, ms_pct, mo_pct, bmp_nm3_t, masse_volumique_t_m3")
        if site_id:
            query = query.eq("site_id", site_id)
        response = query.order("name").execute()
    except Exception:
        response = client.table(TBL_REF).select("name").order("name").execute()

    data = response.data or []
    ingredients: list[str] = []
    ingredient_params: dict[str, dict] = {}

    for row in data:
        value = str(row.get("name", "")).strip()
        if value:
            ingredients.append(value)
            ingredient_params[value] = {
                "ms_pct": round(to_float(row.get("ms_pct"), 0.0), 3),
                "mo_pct": round(to_float(row.get("mo_pct"), 0.0), 3),
                "bmp_nm3_t": round(to_float(row.get("bmp_nm3_t"), 0.0), 3),
                "masse_volumique_t_m3": round(to_float(row.get("masse_volumique_t_m3"), 0.0), 3),
            }

    ingredients = sorted(list(set(ingredients)))
    for ingredient in ingredients:
        if ingredient not in ingredient_params:
            ingredient_params[ingredient] = {
                "ms_pct": 0.0,
                "mo_pct": 0.0,
                "bmp_nm3_t": 0.0,
                "masse_volumique_t_m3": 0.0,
            }

    return ingredients, ingredient_params


def load_intrants_global(client: Client) -> list[dict]:
    rows = (
        client.table("referentiel_ingredients")
        .select("site_id, name, ms_pct, mo_pct, bmp_nm3_t, masse_volumique_t_m3")
        .order("name")
        .execute()
        .data
        or []
    )
    return rows


def get_natisoft_config() -> dict:
    login_url = os.getenv("NATISOFT_LOGIN_URL", "").strip()
    export_url = os.getenv("NATISOFT_EXPORT_URL", "").strip()
    username = os.getenv("NATISOFT_USERNAME", "").strip()
    password = os.getenv("NATISOFT_PASSWORD", "").strip()
    client_id = os.getenv("NATISOFT_CLIENT_ID", "").strip()
    client_secret = os.getenv("NATISOFT_CLIENT_SECRET", "").strip()

    if not all([login_url, export_url, username, password, client_id, client_secret]):
        try:
            login_url = login_url or str(st.secrets.get("NATISOFT_LOGIN_URL", "")).strip()
            export_url = export_url or str(st.secrets.get("NATISOFT_EXPORT_URL", "")).strip()
            username = username or str(st.secrets.get("NATISOFT_USERNAME", "")).strip()
            password = password or str(st.secrets.get("NATISOFT_PASSWORD", "")).strip()
            client_id = client_id or str(st.secrets.get("NATISOFT_CLIENT_ID", "")).strip()
            client_secret = client_secret or str(st.secrets.get("NATISOFT_CLIENT_SECRET", "")).strip()
        except Exception:
            pass

    if not login_url:
        login_url = "https://natisoft-connect.valpronat.com/api/api/auth/login"
    if not export_url:
        export_url = "https://natisoft-connect.valpronat.com/api/api/model/hourly_counter_value/export/csv"

    return {
        "login_url": login_url,
        "export_url": export_url,
        "username": username,
        "password": password,
        "client_id": client_id,
        "client_secret": client_secret,
    }


def natisoft_login_url_candidates(config: dict) -> list[str]:
    candidates: list[str] = []

    configured = str(config.get("login_url", "") or "").strip()
    if configured:
        candidates.append(configured)

    base_hosts: list[str] = []
    for raw in [configured, str(config.get("export_url", "") or "").strip()]:
        if not raw:
            continue
        parsed = urlparse(raw)
        if parsed.scheme and parsed.netloc:
            base = f"{parsed.scheme}://{parsed.netloc}"
            if base not in base_hosts:
                base_hosts.append(base)

    for base in base_hosts:
        for suffix in [
            "/api/api/auth/login",
            "/api/auth/login",
            "/oauth/token",
            "/api/oauth/token",
            "/api/api/oauth/token",
        ]:
            url = f"{base}{suffix}"
            if url not in candidates:
                candidates.append(url)

    return candidates


def _extract_access_token_from_response(response: requests.Response) -> str:
    try:
        data = response.json()
        if isinstance(data, dict):
            token = str(data.get("access_token", "") or "").strip()
            if token:
                return token

            nested_token = data.get("token", {})
            if isinstance(nested_token, dict):
                token = str(nested_token.get("access_token", "") or "").strip()
                if token:
                    return token
    except Exception:
        pass

    text = (response.text or "").strip()
    token_match = re.search(r'"access_token"\s*:\s*"([^"]+)"', text)
    if token_match:
        return token_match.group(1).strip()

    return ""


def _natisoft_error_brief(response: requests.Response) -> str:
    status = response.status_code
    text = (response.text or "").strip().replace("\n", " ")
    if len(text) > 180:
        text = text[:180] + "..."
    return f"HTTP {status} {text}".strip()


def try_natisoft_login(login_url: str, payload_login: dict) -> tuple[str, str]:
    attempts = [
        {
            "label": "json",
            "kwargs": {"json": payload_login, "headers": {"Accept": "application/json"}},
        },
        {
            "label": "form",
            "kwargs": {
                "data": payload_login,
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            },
        },
    ]

    last_error = ""
    for attempt in attempts:
        try:
            response = requests.post(login_url, timeout=30, **attempt["kwargs"])
            token = _extract_access_token_from_response(response)
            if token:
                return token, ""
            last_error = f"{attempt['label']} {_natisoft_error_brief(response)}"
        except Exception as error:
            last_error = f"{attempt['label']} {error}"

    return "", last_error


def maintenance_cache_paths(site_id: str) -> tuple[Path, Path]:
    safe_site_id = re.sub(r"[^a-zA-Z0-9_-]", "_", site_id.strip() or "default")
    base_dir = Path("data") / "maintenance"
    base_dir.mkdir(parents=True, exist_ok=True)
    csv_path = base_dir / f"hourly_{safe_site_id}.csv"
    meta_path = base_dir / f"hourly_{safe_site_id}_meta.json"
    return csv_path, meta_path


def maintenance_workspace_mapping_file() -> Path:
    base_dir = Path("data") / "maintenance"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "workspace_mapping.json"


def torchere_group_mapping_file() -> Path:
    base_dir = Path("data") / "securite"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "torchere_group_mapping.json"


def energie_group_mapping_file() -> Path:
    base_dir = Path("data") / "energie"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "energie_group_mapping.json"


def energie_import_script_config_file() -> Path:
    base_dir = Path("data") / "energie"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "energie_import_script_config.json"


def default_energie_import_script_config() -> dict:
    return {
        "date_column_index": ENERGIE_DATE_COLUMN_INDEX,
        "epuration_column_index": ENERGIE_EPURATION_COLUMN_INDEX,
        "process_column_index": ENERGIE_PROCESS_COLUMN_INDEX,
        "biomethane_column_index": ENERGIE_BIOMETHANE_COLUMN_INDEX,
        "biogas_column_index": ENERGIE_BIOGAZ_COLUMN_INDEX,
        "process_model": ENERGIE_DEFAULT_MODELS.get("process", "energy_integrator"),
        "epurateur_model": ENERGIE_DEFAULT_MODELS.get("epurateur", "energy_integrator"),
        "biomethane_model": ENERGIE_DEFAULT_MODELS.get("biomethane", "energy_integrator_value"),
        "reject_torchere_columns": ENERGIE_REJECT_TORCHERE_COLUMNS,
        "site_overrides": {},
    }


def load_energie_import_script_config() -> dict:
    config_file = energie_import_script_config_file()
    defaults = default_energie_import_script_config()
    try:
        if not config_file.exists():
            return defaults
        raw = json.loads(config_file.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return defaults

        site_overrides = raw.get("site_overrides", {})
        if not isinstance(site_overrides, dict):
            site_overrides = {}

        return {
            "date_column_index": int(raw.get("date_column_index", defaults["date_column_index"])),
            "epuration_column_index": int(raw.get("epuration_column_index", defaults["epuration_column_index"])),
            "process_column_index": int(raw.get("process_column_index", defaults["process_column_index"])),
            "biomethane_column_index": int(raw.get("biomethane_column_index", defaults["biomethane_column_index"])),
            "biogas_column_index": int(raw.get("biogas_column_index", raw.get("process_column_index", defaults["biogas_column_index"]))),
            "process_model": str(raw.get("process_model", defaults["process_model"]) or defaults["process_model"]).strip() or defaults["process_model"],
            "epurateur_model": str(raw.get("epurateur_model", defaults["epurateur_model"]) or defaults["epurateur_model"]).strip() or defaults["epurateur_model"],
            "biomethane_model": str(raw.get("biomethane_model", defaults["biomethane_model"]) or defaults["biomethane_model"]).strip() or defaults["biomethane_model"],
            "reject_torchere_columns": bool(raw.get("reject_torchere_columns", defaults["reject_torchere_columns"])),
            "site_overrides": {
                str(site_id).strip(): value
                for site_id, value in site_overrides.items()
                if str(site_id).strip() and isinstance(value, dict)
            },
        }
    except Exception:
        return defaults


def save_energie_import_script_config(config: dict) -> None:
    config_file = energie_import_script_config_file()
    cleaned = default_energie_import_script_config()
    cleaned["date_column_index"] = int(config.get("date_column_index", cleaned["date_column_index"]))
    cleaned["epuration_column_index"] = int(config.get("epuration_column_index", cleaned["epuration_column_index"]))
    cleaned["process_column_index"] = int(config.get("process_column_index", cleaned["process_column_index"]))
    cleaned["biomethane_column_index"] = int(config.get("biomethane_column_index", cleaned["biomethane_column_index"]))
    cleaned["biogas_column_index"] = int(config.get("biogas_column_index", config.get("process_column_index", cleaned["biogas_column_index"])))
    cleaned["process_model"] = str(config.get("process_model", cleaned["process_model"]) or cleaned["process_model"]).strip() or cleaned["process_model"]
    cleaned["epurateur_model"] = str(config.get("epurateur_model", cleaned["epurateur_model"]) or cleaned["epurateur_model"]).strip() or cleaned["epurateur_model"]
    cleaned["biomethane_model"] = str(config.get("biomethane_model", cleaned["biomethane_model"]) or cleaned["biomethane_model"]).strip() or cleaned["biomethane_model"]
    cleaned["reject_torchere_columns"] = bool(config.get("reject_torchere_columns", cleaned["reject_torchere_columns"]))

    site_overrides = config.get("site_overrides", {})
    if isinstance(site_overrides, dict):
        cleaned["site_overrides"] = {
            str(site_id).strip(): {
                "date_column_index": int(value.get("date_column_index", cleaned["date_column_index"])),
                "epuration_column_index": int(value.get("epuration_column_index", cleaned["epuration_column_index"])),
                "process_column_index": int(value.get("process_column_index", cleaned["process_column_index"])),
                "biomethane_column_index": int(value.get("biomethane_column_index", cleaned["biomethane_column_index"])),
                "biogas_column_index": int(value.get("biogas_column_index", value.get("process_column_index", cleaned["biogas_column_index"]))),
                "process_model": str(value.get("process_model", cleaned["process_model"]) or cleaned["process_model"]).strip() or cleaned["process_model"],
                "epurateur_model": str(value.get("epurateur_model", cleaned["epurateur_model"]) or cleaned["epurateur_model"]).strip() or cleaned["epurateur_model"],
                "biomethane_model": str(value.get("biomethane_model", cleaned["biomethane_model"]) or cleaned["biomethane_model"]).strip() or cleaned["biomethane_model"],
                "reject_torchere_columns": bool(value.get("reject_torchere_columns", cleaned["reject_torchere_columns"])),
            }
            for site_id, value in site_overrides.items()
            if str(site_id).strip() and isinstance(value, dict)
        }

    config_file.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")


def get_energie_import_script_config_for_site(site_id: str) -> dict:
    config = load_energie_import_script_config()
    merged = {
        "date_column_index": int(config.get("date_column_index", ENERGIE_DATE_COLUMN_INDEX)),
        "epuration_column_index": int(config.get("epuration_column_index", ENERGIE_EPURATION_COLUMN_INDEX)),
        "process_column_index": int(config.get("process_column_index", ENERGIE_PROCESS_COLUMN_INDEX)),
        "biomethane_column_index": int(config.get("biomethane_column_index", ENERGIE_BIOMETHANE_COLUMN_INDEX)),
        "biogas_column_index": int(config.get("biogas_column_index", config.get("process_column_index", ENERGIE_BIOGAZ_COLUMN_INDEX))),
        "process_model": str(config.get("process_model", ENERGIE_DEFAULT_MODELS.get("process", "energy_integrator")) or ENERGIE_DEFAULT_MODELS.get("process", "energy_integrator")).strip() or ENERGIE_DEFAULT_MODELS.get("process", "energy_integrator"),
        "epurateur_model": str(config.get("epurateur_model", ENERGIE_DEFAULT_MODELS.get("epurateur", "energy_integrator")) or ENERGIE_DEFAULT_MODELS.get("epurateur", "energy_integrator")).strip() or ENERGIE_DEFAULT_MODELS.get("epurateur", "energy_integrator"),
        "biomethane_model": str(config.get("biomethane_model", ENERGIE_DEFAULT_MODELS.get("biomethane", "energy_integrator_value")) or ENERGIE_DEFAULT_MODELS.get("biomethane", "energy_integrator_value")).strip() or ENERGIE_DEFAULT_MODELS.get("biomethane", "energy_integrator_value"),
        "reject_torchere_columns": bool(config.get("reject_torchere_columns", ENERGIE_REJECT_TORCHERE_COLUMNS)),
    }

    site_overrides = config.get("site_overrides", {})
    site_override = site_overrides.get(str(site_id).strip(), {}) if isinstance(site_overrides, dict) else {}
    if isinstance(site_override, dict):
        merged["date_column_index"] = int(site_override.get("date_column_index", merged["date_column_index"]))
        merged["epuration_column_index"] = int(site_override.get("epuration_column_index", merged["epuration_column_index"]))
        merged["process_column_index"] = int(site_override.get("process_column_index", merged["process_column_index"]))
        merged["biomethane_column_index"] = int(site_override.get("biomethane_column_index", merged["biomethane_column_index"]))
        merged["biogas_column_index"] = int(site_override.get("biogas_column_index", site_override.get("process_column_index", merged["biogas_column_index"])))
        merged["process_model"] = str(site_override.get("process_model", merged["process_model"]) or merged["process_model"]).strip() or merged["process_model"]
        merged["epurateur_model"] = str(site_override.get("epurateur_model", merged["epurateur_model"]) or merged["epurateur_model"]).strip() or merged["epurateur_model"]
        merged["biomethane_model"] = str(site_override.get("biomethane_model", merged["biomethane_model"]) or merged["biomethane_model"]).strip() or merged["biomethane_model"]
        merged["reject_torchere_columns"] = bool(site_override.get("reject_torchere_columns", merged["reject_torchere_columns"]))

    return merged


def load_maintenance_workspace_mapping() -> dict[str, str]:
    mapping_file = maintenance_workspace_mapping_file()
    try:
        if not mapping_file.exists():
            return {}
        data = json.loads(mapping_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return {str(k).strip(): str(v).strip() for k, v in data.items() if str(k).strip()}
    except Exception:
        return {}


def load_torchere_group_mapping() -> dict[str, str]:
    mapping_file = torchere_group_mapping_file()
    try:
        if not mapping_file.exists():
            return {}
        data = json.loads(mapping_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return {str(k).strip(): str(v).strip() for k, v in data.items() if str(k).strip()}
    except Exception:
        return {}


def load_energie_group_mapping() -> dict[str, str]:
    mapping_file = energie_group_mapping_file()
    try:
        if not mapping_file.exists():
            return {}
        data = json.loads(mapping_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return {str(k).strip(): str(v).strip() for k, v in data.items() if str(k).strip()}
    except Exception:
        return {}


def save_maintenance_workspace_mapping(mapping: dict[str, str]) -> None:
    mapping_file = maintenance_workspace_mapping_file()
    cleaned = {str(k).strip(): str(v).strip() for k, v in mapping.items() if str(k).strip()}
    mapping_file.write_text(json.dumps(cleaned, ensure_ascii=False), encoding="utf-8")


def save_torchere_group_mapping(mapping: dict[str, str]) -> None:
    mapping_file = torchere_group_mapping_file()
    cleaned = {str(k).strip(): str(v).strip() for k, v in mapping.items() if str(k).strip()}
    mapping_file.write_text(json.dumps(cleaned, ensure_ascii=False), encoding="utf-8")


def save_energie_group_mapping(mapping: dict[str, str]) -> None:
    mapping_file = energie_group_mapping_file()
    cleaned = {str(k).strip(): str(v).strip() for k, v in mapping.items() if str(k).strip()}
    mapping_file.write_text(json.dumps(cleaned, ensure_ascii=False), encoding="utf-8")


def default_workspace_for_site(site_code: str, site_name: str) -> str:
    code = site_code.strip().upper()
    name = site_name.strip().upper()

    if "DUAL" in code or "DUAL" in name or "PREMERY" in name:
        return "10"
    if "STRAWBERRY" in code or "STRAWBERRY" in name:
        return "41"
    return ""


def get_workspace_for_site(site_id: str, site_code: str, site_name: str) -> str:
    mapping = load_maintenance_workspace_mapping()
    mapped = str(mapping.get(site_id, "") or "").strip()
    if mapped:
        return mapped
    return default_workspace_for_site(site_code, site_name)


def default_torchere_group_for_site(site_code: str, site_name: str) -> str:
    code = site_code.strip().upper()
    name = site_name.strip().upper()

    if "DUAL" in code or "DUAL" in name or "PREMERY" in name:
        return TORCHERE_DEFAULT_GROUP_DUAL
    if "STRAWBERRY" in code or "STRAWBERRY" in name:
        return TORCHERE_DEFAULT_GROUP_STRAWBERRY
    return TORCHERE_DEFAULT_GROUP_ID


def resolve_torchere_group_for_workspace(workspace_id: str, group_id: str) -> tuple[str, bool]:
    workspace_clean = str(workspace_id or "").strip()
    group_clean = str(group_id or "").strip()
    expected = TORCHERE_WORKSPACE_GROUP_MAP.get(workspace_clean, "")
    if expected and group_clean != expected:
        return expected, True
    return group_clean, False


def get_torchere_group_for_site(site_id: str, site_code: str, site_name: str) -> str:
    mapping = load_torchere_group_mapping()
    mapped = str(mapping.get(site_id, "") or "").strip()
    if mapped:
        return mapped
    return default_torchere_group_for_site(site_code, site_name)


def default_energie_group_for_site(site_code: str, site_name: str) -> str:
    code = site_code.strip().upper()
    name = site_name.strip().upper()

    if "DUAL" in code or "DUAL" in name or "PREMERY" in name:
        return ENERGIE_DEFAULT_GROUP_DUAL
    if "STRAWBERRY" in code or "STRAWBERRY" in name:
        return ENERGIE_DEFAULT_GROUP_STRAWBERRY
    return ""


def resolve_energie_group_for_workspace(workspace_id: str, group_id: str) -> tuple[str, bool]:
    workspace_clean = str(workspace_id or "").strip()
    group_clean = str(group_id or "").strip()
    expected = ENERGIE_WORKSPACE_GROUP_MAP.get(workspace_clean, "")
    if expected and group_clean != expected:
        return expected, True
    return group_clean, False


def get_energie_group_for_site(site_id: str, site_code: str, site_name: str) -> str:
    mapping = load_energie_group_mapping()
    mapped = str(mapping.get(site_id, "") or "").strip()
    if mapped:
        return mapped
    return default_energie_group_for_site(site_code, site_name)


def load_maintenance_cache(site_id: str) -> tuple[pd.DataFrame, dict]:
    csv_path, meta_path = maintenance_cache_paths(site_id)
    df = pd.DataFrame()
    meta: dict = {}

    try:
        if csv_path.exists():
            df = pd.read_csv(csv_path)
    except Exception:
        df = pd.DataFrame()

    try:
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if not isinstance(meta, dict):
                meta = {}
    except Exception:
        meta = {}

    return df, meta


def torchere_cache_paths(site_id: str) -> tuple[Path, Path]:
    safe_site_id = re.sub(r"[^a-zA-Z0-9_-]", "_", site_id.strip() or "default")
    base_dir = Path("data") / "securite"
    base_dir.mkdir(parents=True, exist_ok=True)
    csv_path = base_dir / f"torchere_{safe_site_id}.csv"
    meta_path = base_dir / f"torchere_{safe_site_id}_meta.json"
    return csv_path, meta_path


def load_torchere_cache(site_id: str) -> tuple[pd.DataFrame, dict]:
    csv_path, meta_path = torchere_cache_paths(site_id)
    df = pd.DataFrame()
    meta: dict = {}

    try:
        if csv_path.exists():
            df = pd.read_csv(csv_path)
    except Exception:
        df = pd.DataFrame()

    try:
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if not isinstance(meta, dict):
                meta = {}
    except Exception:
        meta = {}

    return df, meta


def energie_cache_paths(site_id: str, consommation_type: str = "") -> tuple[Path, Path]:
    safe_site_id = re.sub(r"[^a-zA-Z0-9_-]", "_", site_id.strip() or "default")
    type_suffix = re.sub(r"[^a-zA-Z0-9_-]", "_", str(consommation_type or "global").strip().lower() or "global")
    base_dir = Path("data") / "energie"
    base_dir.mkdir(parents=True, exist_ok=True)
    csv_path = base_dir / f"energie_{safe_site_id}_{type_suffix}.csv"
    meta_path = base_dir / f"energie_{safe_site_id}_{type_suffix}_meta.json"
    return csv_path, meta_path


def load_energie_cache(site_id: str, consommation_type: str) -> tuple[pd.DataFrame, dict]:
    csv_path, meta_path = energie_cache_paths(site_id, consommation_type)
    df = pd.DataFrame()
    meta: dict = {}

    try:
        if csv_path.exists():
            df = pd.read_csv(csv_path)
    except Exception:
        df = pd.DataFrame()

    try:
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if not isinstance(meta, dict):
                meta = {}
    except Exception:
        meta = {}

    return df, meta


def save_torchere_cache(site_id: str, df: pd.DataFrame, meta: dict) -> None:
    csv_path, meta_path = torchere_cache_paths(site_id)
    df.to_csv(csv_path, index=False)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")


def save_energie_cache(site_id: str, consommation_type: str, df: pd.DataFrame, meta: dict) -> None:
    csv_path, meta_path = energie_cache_paths(site_id, consommation_type)
    df.to_csv(csv_path, index=False)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")


def save_maintenance_cache(site_id: str, df: pd.DataFrame, meta: dict) -> None:
    csv_path, meta_path = maintenance_cache_paths(site_id)
    df.to_csv(csv_path, index=False)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")


def _json_safe_value(value: object) -> object:
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _deduplicate_column_names(columns: list[str]) -> list[str]:
    counters: dict[str, int] = {}
    deduped: list[str] = []
    for raw_name in columns:
        name = str(raw_name or "").strip() or "col"
        if name not in counters:
            counters[name] = 0
            deduped.append(name)
            continue
        counters[name] += 1
        deduped.append(f"{name}.{counters[name]}")
    return deduped


def _parse_natisoft_csv_text(text: str) -> pd.DataFrame:
    csv_text = str(text or "").strip()
    if not csv_text:
        return pd.DataFrame()

    try:
        raw_df = pd.read_csv(StringIO(csv_text), sep=";", header=None, dtype=str, engine="python")
    except Exception:
        try:
            return pd.read_csv(StringIO(csv_text), dtype=str)
        except Exception:
            return pd.DataFrame()

    raw_df = raw_df.fillna("")
    if raw_df.empty:
        return pd.DataFrame()

    if len(raw_df.index) >= 2:
        header_main = [str(value).strip() for value in raw_df.iloc[0].tolist()]
        header_sub = [str(value).strip() for value in raw_df.iloc[1].tolist()]

        combined_headers: list[str] = []
        for idx, (main, sub) in enumerate(zip(header_main, header_sub)):
            if idx == 0:
                combined_headers.append(sub or main or "Date")
                continue
            if sub.lower() in {"journalier", "cumul"}:
                combined_headers.append(f"{main} {sub}".strip())
            else:
                combined_headers.append(main or sub or f"col_{idx}")

        combined_headers = _deduplicate_column_names(combined_headers)
        data_df = raw_df.iloc[2:].copy()
        data_df.columns = combined_headers
        return data_df.reset_index(drop=True)

    one_header = _deduplicate_column_names([str(value).strip() for value in raw_df.iloc[0].tolist()])
    data_df = raw_df.iloc[1:].copy()
    data_df.columns = one_header
    return data_df.reset_index(drop=True)


def _coerce_single_column_natisoft_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or len(df.columns) != 1:
        return df

    col = str(df.columns[0])
    sample = [str(value) for value in df[col].head(20).tolist()]
    if not any(";" in value for value in sample):
        return df

    text = "\n".join(str(value) for value in df[col].tolist())
    parsed = _parse_natisoft_csv_text(text)
    return parsed if not parsed.empty else df


def persist_maintenance_to_supabase(client: Client, site_id: str, workspace_id: str, df: pd.DataFrame) -> tuple[int, int]:
    if df.empty:
        return 0, 0

    sync_date = datetime.now().strftime("%Y-%m-%d")
    existing_row_indexes: set[int] = set()
    try:
        existing_rows = (
            client.table(TBL_MAINTENANCE)
            .select("row_index")
            .eq("site_id", site_id)
            .eq("workspace_id", workspace_id)
            .eq("sync_date", sync_date)
            .execute()
            .data
            or []
        )
        for row in existing_rows:
            try:
                existing_row_indexes.add(int(row.get("row_index")))
            except Exception:
                pass
    except Exception:
        existing_row_indexes = set()

    payload: list[dict] = []
    imported_at = datetime.now().isoformat(timespec="seconds")
    skipped_count = 0
    for idx, (_, row) in enumerate(df.reset_index(drop=True).iterrows()):
        if idx in existing_row_indexes:
            skipped_count += 1
            continue

        row_data = {str(col): _json_safe_value(val) for col, val in row.items()}
        payload.append(
            {
                "site_id": site_id,
                "workspace_id": workspace_id,
                "sync_date": sync_date,
                "row_index": idx,
                "row_data": row_data,
                "imported_at": imported_at,
            }
        )

    try:
        chunk_size = 500
        for start in range(0, len(payload), chunk_size):
            insert_with_schema_fallback(client, TBL_MAINTENANCE, payload[start : start + chunk_size])
    except Exception as error:
        raise RuntimeError(
            "Import en table maintenance impossible. Vérifiez que la table `maintenance_hourly_data` existe côté Supabase. "
            f"Détail: {error}"
        ) from error

    return len(payload), skipped_count


def _parse_runtime_seconds(value: object) -> int | None:
    text = str(value or "").strip().strip('"')
    if not text:
        return None

    match = re.fullmatch(r"(\d+):(\d{2}):(\d{2})", text)
    if not match:
        return None

    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    return hours * 3600 + minutes * 60 + seconds


def _format_runtime_seconds(total_seconds: int) -> str:
    total = max(int(total_seconds), 0)
    hours = total // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _guess_history_date_column(history_df: pd.DataFrame) -> str:
    candidates = [
        column
        for column in history_df.columns
        if str(column).strip().lower() in {"date", "#"} or "date" in str(column).strip().lower()
    ]
    if not candidates:
        candidates = list(history_df.columns)

    best_column = ""
    best_score = -1
    for column in candidates:
        parsed = pd.to_datetime(history_df[column], dayfirst=True, errors="coerce")
        score = int(parsed.notna().sum())
        if score > best_score:
            best_column = str(column)
            best_score = score

    return best_column if best_column else str(history_df.columns[0])


def _detect_journalier_columns(history_df: pd.DataFrame, date_column: str) -> list[str]:
    if history_df.empty:
        return []

    by_name = [
        str(column)
        for column in history_df.columns
        if str(column) != date_column and "journalier" in str(column).strip().lower()
    ]
    if by_name:
        return by_name

    descriptor_row = None
    for _, row in history_df.head(20).iterrows():
        values = [str(value or "").strip().lower() for value in row.values]
        journalier_count = sum(1 for value in values if "journalier" in value)
        cumul_count = sum(1 for value in values if "cumul" in value)
        if journalier_count >= 3 and cumul_count >= 3:
            descriptor_row = row
            break

    journalier_columns: list[str] = []
    if descriptor_row is not None:
        for column in history_df.columns:
            label = str(descriptor_row.get(column, "") or "").strip().lower()
            if "journalier" in label:
                journalier_columns.append(str(column))

    if not journalier_columns:
        for column in history_df.columns:
            column_name = str(column)
            if column_name == date_column:
                continue
            if re.search(r"\.\d+$", column_name):
                continue
            if f"{column_name}.1" in history_df.columns:
                journalier_columns.append(column_name)

    return [column for column in journalier_columns if column != date_column]


def load_maintenance_history_from_supabase(client: Client, site_id: str, workspace_id: str) -> pd.DataFrame:
    workspace_clean = workspace_id.strip()
    if not workspace_clean:
        return pd.DataFrame()

    page_size = 1000
    start = 0
    rows: list[dict] = []
    while True:
        response = (
            client.table(TBL_MAINTENANCE)
            .select("row_data")
            .eq("site_id", site_id)
            .eq("workspace_id", workspace_clean)
            .order("imported_at", desc=False)
            .range(start, start + page_size - 1)
            .execute()
        )
        chunk = response.data or []
        if not chunk:
            break

        for row in chunk:
            row_data = row.get("row_data")
            if isinstance(row_data, dict) and row_data:
                rows.append(row_data)

        if len(chunk) < page_size:
            break
        start += page_size

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def load_torchere_history_from_supabase(
    client: Client,
    site_id: str,
    workspace_id: str,
    group_id: str,
    model_name: str,
) -> pd.DataFrame:
    workspace_clean = str(workspace_id or "").strip()
    group_clean = str(group_id or "").strip()
    model_clean = str(model_name or "").strip()

    if not workspace_clean or not group_clean or not model_clean:
        return pd.DataFrame()

    page_size = 1000
    start = 0
    rows: list[dict] = []

    while True:
        response = (
            client.table(TBL_SECURITE_TORCHERE)
            .select("row_data")
            .eq("site_id", site_id)
            .eq("workspace_id", workspace_clean)
            .eq("group_id", group_clean)
            .eq("model_name", model_clean)
            .order("imported_at", desc=False)
            .range(start, start + page_size - 1)
            .execute()
        )
        chunk = response.data or []
        if not chunk:
            break

        for row in chunk:
            row_data = row.get("row_data")
            if isinstance(row_data, dict) and row_data:
                rows.append(row_data)

        if len(chunk) < page_size:
            break
        start += page_size

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def load_energie_history_from_supabase(
    client: Client,
    site_id: str,
    workspace_id: str,
    group_id: str,
    consommation_type: str,
    model_name: str,
) -> pd.DataFrame:
    workspace_clean = str(workspace_id or "").strip()
    group_clean = str(group_id or "").strip()
    consommation_clean = str(consommation_type or "").strip().lower()
    model_clean = str(model_name or "").strip()

    if not workspace_clean or not group_clean or not consommation_clean or not model_clean:
        return pd.DataFrame()

    page_size = 1000
    start = 0
    rows: list[dict] = []

    while True:
        response = (
            client.table(TBL_ENERGIE)
            .select("row_data")
            .eq("site_id", site_id)
            .eq("workspace_id", workspace_clean)
            .eq("group_id", group_clean)
            .eq("consommation_type", consommation_clean)
            .eq("model_name", model_clean)
            .order("imported_at", desc=False)
            .range(start, start + page_size - 1)
            .execute()
        )
        chunk = response.data or []
        if not chunk:
            break

        for row in chunk:
            row_data = row.get("row_data")
            if isinstance(row_data, dict) and row_data:
                rows.append(row_data)

        if len(chunk) < page_size:
            break
        start += page_size

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def load_energie_history_from_supabase_any_model(
    client: Client,
    site_id: str,
    workspace_id: str,
    group_id: str,
    consommation_type: str,
) -> pd.DataFrame:
    workspace_clean = str(workspace_id or "").strip()
    group_clean = str(group_id or "").strip()
    consommation_clean = str(consommation_type or "").strip().lower()

    if not workspace_clean or not group_clean or not consommation_clean:
        return pd.DataFrame()

    page_size = 1000
    start = 0
    rows: list[dict] = []

    while True:
        response = (
            client.table(TBL_ENERGIE)
            .select("row_data")
            .eq("site_id", site_id)
            .eq("workspace_id", workspace_clean)
            .eq("group_id", group_clean)
            .eq("consommation_type", consommation_clean)
            .order("imported_at", desc=False)
            .range(start, start + page_size - 1)
            .execute()
        )
        chunk = response.data or []
        if not chunk:
            break

        for row in chunk:
            row_data = row.get("row_data")
            if isinstance(row_data, dict) and row_data:
                rows.append(row_data)

        if len(chunk) < page_size:
            break
        start += page_size

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def average_flow_on_period(daily_df: pd.DataFrame, start_date: date, end_date: date) -> float:
    if daily_df.empty or "date" not in daily_df.columns or "consumption_value" not in daily_df.columns:
        return 0.0

    scoped = daily_df[(daily_df["date"] >= start_date) & (daily_df["date"] <= end_date)]
    if scoped.empty:
        return 0.0

    return float(scoped["consumption_value"].mean())


def _format_pct_delta(current_value: float, reference_value: float) -> str:
    if reference_value <= 0:
        return "N/A"

    delta_pct = ((current_value - reference_value) / reference_value) * 100.0
    return f"{delta_pct:+.1f}%"


def build_runtime_summary_by_equipment(history_df: pd.DataFrame) -> pd.DataFrame:
    if history_df.empty:
        return pd.DataFrame()

    date_column = _guess_history_date_column(history_df)
    if date_column not in history_df.columns:
        return pd.DataFrame()

    working_df = history_df.copy()
    working_df["_parsed_date"] = pd.to_datetime(working_df[date_column], dayfirst=True, errors="coerce").dt.date
    working_df = working_df[working_df["_parsed_date"].notna()]
    if working_df.empty:
        return pd.DataFrame()

    journalier_columns = _detect_journalier_columns(history_df, date_column)
    if not journalier_columns:
        return pd.DataFrame()

    records: list[dict] = []
    for column in journalier_columns:
        equipment_name = re.sub(r"\.\d+$", "", str(column)).strip()
        if not equipment_name or equipment_name.lower() in {"date", "#"}:
            continue

        for _, row in working_df[["_parsed_date", column]].iterrows():
            runtime_seconds = _parse_runtime_seconds(row[column])
            if runtime_seconds is None:
                continue
            records.append(
                {
                    "date": row["_parsed_date"],
                    "equipement": equipment_name,
                    "runtime_seconds": runtime_seconds,
                }
            )

    if not records:
        return pd.DataFrame()

    runtime_df = pd.DataFrame(records)
    deduplicated_daily = (
        runtime_df.groupby(["equipement", "date"], as_index=False)["runtime_seconds"]
        .max()
    )

    summary = (
        deduplicated_daily.groupby("equipement", as_index=False)
        .agg(
            jours_couverts=("date", "nunique"),
            runtime_seconds_total=("runtime_seconds", "sum"),
        )
    )
    summary["moyenne_jour_seconds"] = (
        summary["runtime_seconds_total"] / summary["jours_couverts"].clip(lower=1)
    )
    summary["temps_total"] = summary["runtime_seconds_total"].apply(_format_runtime_seconds)
    summary["heures_total"] = (summary["runtime_seconds_total"] / 3600).round(2)
    summary["moyenne_jour"] = summary["moyenne_jour_seconds"].round().astype(int).apply(_format_runtime_seconds)

    return (
        summary.sort_values("runtime_seconds_total", ascending=False)
        [["equipement", "jours_couverts", "temps_total", "heures_total", "moyenne_jour"]]
        .reset_index(drop=True)
    )


def build_torchere_daily_runtime(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df = _coerce_single_column_natisoft_df(df)

    date_column = _guess_history_date_column(df)
    if date_column not in df.columns:
        return pd.DataFrame()

    journalier_columns = _detect_journalier_columns(df, date_column)
    if not journalier_columns:
        return pd.DataFrame()

    torchere_columns = [
        column
        for column in journalier_columns
        if "torch" in str(column).lower() or "torchère" in str(column).lower()
    ]
    columns_to_use = torchere_columns if torchere_columns else journalier_columns

    working_df = df[[date_column] + columns_to_use].copy()
    working_df["date"] = pd.to_datetime(working_df[date_column], dayfirst=True, errors="coerce").dt.date
    working_df = working_df[working_df["date"].notna()]
    if working_df.empty:
        return pd.DataFrame()

    def _row_runtime_seconds(row: pd.Series) -> int:
        total = 0
        for column in columns_to_use:
            parsed = _parse_runtime_seconds(row.get(column))
            if parsed is not None:
                total += parsed
        return total

    working_df["runtime_seconds"] = working_df.apply(_row_runtime_seconds, axis=1)
    daily = (
        working_df.groupby("date", as_index=False)["runtime_seconds"]
        .max()
        .sort_values("date")
        .reset_index(drop=True)
    )

    daily = daily[daily["runtime_seconds"] > 0]
    if daily.empty:
        return pd.DataFrame()

    daily["runtime_hours"] = (daily["runtime_seconds"] / 3600).round(3)
    daily["runtime_hms"] = daily["runtime_seconds"].apply(_format_runtime_seconds)
    daily["month_date"] = pd.to_datetime(daily["date"]).dt.to_period("M").dt.to_timestamp()
    daily["month_label"] = pd.to_datetime(daily["date"]).dt.strftime("%Y-%m")

    return daily


def _parse_decimal_number(value: object) -> float | None:
    text = str(value or "").strip().strip('"').replace("\xa0", "")
    if not text:
        return None
    if ":" in text:
        return None

    text = text.replace(" ", "")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")

    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None

    try:
        return float(match.group(0))
    except Exception:
        return None


def _parse_energie_date_value(value: object) -> date | None:
    text = str(value or "").strip().strip('"')
    if not text:
        return None

    for fmt in (
        "%m/%d/%Y",
        "%m/%d/%y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%y %H:%M:%S",
        "%m/%d/%y %H:%M",
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ):
        try:
            return datetime.strptime(text, fmt).date()
        except Exception:
            continue

    return None


def _resolve_energie_value_column(
    columns_in_order: list[str],
    date_column: str,
    consommation_type: str,
    preferred_index: int,
) -> str:
    type_clean = str(consommation_type or "").strip().lower()

    def _norm(text: str) -> str:
        return str(text or "").strip().lower()

    def _is_cumul(column_name: str) -> bool:
        return "cumul" in _norm(column_name)

    def _is_journalier(column_name: str) -> bool:
        normalized = _norm(column_name)
        return "journalier" in normalized and "cumul" not in normalized

    non_date_columns = [column for column in columns_in_order if str(column).strip() and str(column) != date_column]

    if 0 <= preferred_index < len(columns_in_order):
        preferred_column = str(columns_in_order[preferred_index]).strip()
        if preferred_column and preferred_column != date_column and not _is_cumul(preferred_column):
            if type_clean == "biomethane":
                normalized = _norm(preferred_column)
                looks_like_biomethane = (
                    "biométhane" in normalized
                    or "biomethane" in normalized
                    or "injection" in normalized
                    or ("production" in normalized and "biogaz" not in normalized)
                )
                looks_like_biogas = (
                    "biogaz" in normalized
                    or "gaz_in_epur" in normalized
                    or ("epur" in normalized and "gaz" in normalized)
                )
                if looks_like_biomethane and not looks_like_biogas:
                    return preferred_column
            else:
                return preferred_column

    if type_clean == "epurateur":
        for column in non_date_columns:
            normalized = _norm(column)
            if _is_journalier(column) and ("épurateur" in normalized or "epurateur" in normalized):
                return str(column).strip()

    if type_clean == "process":
        for column in non_date_columns:
            normalized = _norm(column)
            if _is_journalier(column) and "process" in normalized:
                return str(column).strip()
        for column in non_date_columns:
            normalized = _norm(column)
            if _is_journalier(column) and ("métha" in normalized or "metha" in normalized):
                return str(column).strip()

    if type_clean == "biomethane":
        for column in non_date_columns:
            normalized = _norm(column)
            if _is_journalier(column) and (
                "biométhane" in normalized
                or "biomethane" in normalized
                or "production" in normalized
                or "injection" in normalized
            ):
                return str(column).strip()

    if type_clean == "process":
        for column in non_date_columns:
            normalized = _norm(column)
            if _is_journalier(column) and "épurateur" not in normalized and "epurateur" not in normalized:
                return str(column).strip()

    for column in non_date_columns:
        if _is_journalier(column):
            return str(column).strip()

    return ""


def build_energie_daily_consumption(df: pd.DataFrame, consommation_type: str, site_id: str = "") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df = _coerce_single_column_natisoft_df(df)

    columns_in_order = [str(col) for col in df.columns]
    if not columns_in_order:
        return pd.DataFrame()

    script_config = get_energie_import_script_config_for_site(site_id)
    date_idx = int(script_config.get("date_column_index", ENERGIE_DATE_COLUMN_INDEX)) - 1
    if date_idx < 0 or date_idx >= len(columns_in_order):
        return pd.DataFrame()

    date_column = columns_in_order[date_idx]
    if date_column not in df.columns:
        return pd.DataFrame()

    type_clean = str(consommation_type or "").strip().lower()

    process_idx = int(script_config.get("process_column_index", ENERGIE_PROCESS_COLUMN_INDEX)) - 1
    epuration_idx = int(script_config.get("epuration_column_index", ENERGIE_EPURATION_COLUMN_INDEX)) - 1
    biomethane_idx = int(script_config.get("biomethane_column_index", ENERGIE_BIOMETHANE_COLUMN_INDEX)) - 1
    if type_clean == "process":
        preferred_index = process_idx
    elif type_clean == "biomethane":
        preferred_index = biomethane_idx
    else:
        preferred_index = epuration_idx
    if preferred_index < 0 or preferred_index >= len(columns_in_order):
        preferred_index = -1

    mapped_column = _resolve_energie_value_column(
        columns_in_order=columns_in_order,
        date_column=date_column,
        consommation_type=type_clean,
        preferred_index=preferred_index,
    )

    if not mapped_column or mapped_column == date_column:
        return pd.DataFrame()

    if "cumul" in mapped_column.lower():
        return pd.DataFrame()

    reject_torchere_columns = bool(script_config.get("reject_torchere_columns", ENERGIE_REJECT_TORCHERE_COLUMNS))
    if reject_torchere_columns and ("torch" in mapped_column.lower() or "torchère" in mapped_column.lower()):
        return pd.DataFrame()

    columns_to_use = [mapped_column]

    working_df = df[[date_column] + columns_to_use].copy()
    working_df["date"] = working_df[date_column].apply(_parse_energie_date_value)
    working_df = working_df[working_df["date"].notna()]
    if working_df.empty:
        return pd.DataFrame()

    def _row_consumption_value(row: pd.Series) -> float:
        total = 0.0
        for column in columns_to_use:
            parsed = _parse_decimal_number(row.get(column))
            if parsed is not None:
                total += parsed
        return total

    working_df["consumption_value"] = working_df.apply(_row_consumption_value, axis=1)
    daily = (
        working_df.groupby("date", as_index=False)["consumption_value"]
        .max()
        .sort_values("date")
        .reset_index(drop=True)
    )

    daily = daily[daily["consumption_value"] > 0]
    if daily.empty:
        return pd.DataFrame()

    daily["month_date"] = pd.to_datetime(daily["date"]).dt.to_period("M").dt.to_timestamp()
    daily["month_label"] = pd.to_datetime(daily["date"]).dt.strftime("%Y-%m")
    daily["consommation_type"] = type_clean

    return daily


def fetch_natisoft_hourly_data(workspace_id: str = "") -> pd.DataFrame:
    config = get_natisoft_config()
    missing = [
        key
        for key in ["username", "password", "client_id", "client_secret"]
        if not str(config.get(key, "")).strip()
    ]
    if missing:
        raise RuntimeError(
            "Configuration Natisoft incomplète. Ajoutez NATISOFT_USERNAME, NATISOFT_PASSWORD, "
            "NATISOFT_CLIENT_ID, NATISOFT_CLIENT_SECRET dans .streamlit/secrets.toml ou variables d'environnement."
        )

    payload_login = {
        "username": config["username"],
        "password": config["password"],
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "grant_type": "password",
        "accept_conditions": True,
    }

    token = ""
    login_errors: list[str] = []
    for login_url in natisoft_login_url_candidates(config):
        token, error_text = try_natisoft_login(login_url, payload_login)
        if token:
            break
        if error_text:
            login_errors.append(f"{login_url} -> {error_text}")
        else:
            login_errors.append(f"{login_url} -> token absent")

    if not token:
        raise RuntimeError(
            "Connexion Natisoft impossible. Endpoints testés: "
            + " | ".join(login_errors[:5])
        )

    today_date = datetime.now().strftime("%Y-%m-%d")
    params = {
        "sort": "raised_at",
        "filters": f'[{{"field":"hasValueMonth","operator":"scope","value":"{today_date}"}}]',
    }
    workspace_clean = workspace_id.strip()
    if workspace_clean:
        params["workspace"] = workspace_clean
    base_urls = natisoft_base_urls(config)
    referer_base = base_urls[0] if base_urls else "https://natisoft-connect.valpronat.com"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "APP-Terrain/1.0",
        "Accept": "text/csv",
        "bkr-workspace-id": workspace_clean,
    }
    if workspace_clean:
        headers["Referer"] = f"{referer_base}/workspaces/{workspace_clean}/integrators/energy"
        headers["Origin"] = referer_base

    attempts: list[tuple[str, str, dict | None]] = []
    configured_export_url = str(config.get("export_url", "") or "").strip()
    if configured_export_url:
        attempts.append(("configured_export", configured_export_url, params))

    for base in base_urls:
        if workspace_clean:
            attempts.extend(
                [
                    (
                        "integrator_value_sy_m3",
                        f"{base}/sy/workspaces/{quote(workspace_clean, safe='')}/integrator/value/export/csv/{quote('m³', safe='')}/{quote(today_date, safe='')}/year",
                        {
                            "from": today_date,
                            "to": today_date,
                            "workspace": workspace_clean,
                        },
                    ),
                    (
                        "integrator_value_sy_m3_ascii",
                        f"{base}/sy/workspaces/{quote(workspace_clean, safe='')}/integrator/value/export/csv/m3/{quote(today_date, safe='')}/year",
                        {
                            "from": today_date,
                            "to": today_date,
                            "workspace": workspace_clean,
                        },
                    ),
                    (
                        "integrator_value_sy_nm3",
                        f"{base}/sy/workspaces/{quote(workspace_clean, safe='')}/integrator/value/export/csv/Nm3/{quote(today_date, safe='')}/year",
                        {
                            "from": today_date,
                            "to": today_date,
                            "workspace": workspace_clean,
                        },
                    ),
                    (
                        "integrator_value_api_sy_m3",
                        f"{base}/api/sy/workspaces/{quote(workspace_clean, safe='')}/integrator/value/export/csv/{quote('m³', safe='')}/{quote(today_date, safe='')}/year",
                        {
                            "from": today_date,
                            "to": today_date,
                            "workspace": workspace_clean,
                        },
                    ),
                ]
            )

        attempts.extend(
            [
                ("hourly_model_api_api", f"{base}/api/api/model/hourly_counter_value/export/csv", params),
                ("hourly_model_api", f"{base}/api/model/hourly_counter_value/export/csv", params),
            ]
        )

    diagnostics: list[str] = []
    seen_urls: set[str] = set()
    for label, url, query_params in attempts:
        clean_url = str(url or "").strip()
        if not clean_url or clean_url in seen_urls:
            continue
        seen_urls.add(clean_url)
        try:
            export_res = requests.get(clean_url, params=query_params, headers=headers, timeout=60)
            if export_res.status_code >= 400:
                diagnostics.append(f"{label}:{export_res.status_code}")
                continue

            text = export_res.text or ""
            if not text.strip():
                diagnostics.append(f"{label}:empty")
                continue

            df = _parse_natisoft_csv_text(text)
            if not df.empty:
                return df

            diagnostics.append(f"{label}:parsed-empty")
        except Exception:
            diagnostics.append(f"{label}:err")

    raise RuntimeError(
        "Aucune donnée horaire récupérée depuis Natisoft. Tentatives: " + " | ".join(diagnostics[:8])
    )


def natisoft_export_url_for_model(config: dict, model_name: str) -> str:
    configured_export_url = str(config.get("export_url", "") or "").strip()
    if configured_export_url:
        if "/model/" in configured_export_url and "/export/csv" in configured_export_url:
            return re.sub(r"/model/[^/]+/export/csv", f"/model/{model_name}/export/csv", configured_export_url)

        parsed = urlparse(configured_export_url)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}/api/api/model/{model_name}/export/csv"

    return f"https://natisoft-connect.valpronat.com/api/api/model/{model_name}/export/csv"


def natisoft_energy_integrator_value_url(
    config: dict,
    workspace_id: str,
    export_date: str,
    export_unit: str = ENERGIE_ELECTRICITY_EXPORT_UNIT,
    export_period: str = "year",
) -> str:
    workspace_clean = str(workspace_id or "").strip() or "10"
    date_clean = str(export_date or "").strip() or datetime.now().strftime("%Y-%m-%d")
    configured_export_url = str(config.get("export_url", "") or "").strip()

    default_unit = str(export_unit or ENERGIE_ELECTRICITY_EXPORT_UNIT).strip() or ENERGIE_ELECTRICITY_EXPORT_UNIT
    default_period = str(export_period or "year").strip() or "year"
    base = "https://natisoft-connect.valpronat.com"

    if configured_export_url:
        parsed = urlparse(configured_export_url)
        if parsed.scheme and parsed.netloc:
            base = f"{parsed.scheme}://{parsed.netloc}"

        match = re.search(
            r"/sy/workspaces/[^/]+/integrator/value/export/csv/([^/]+)/([^/]+)/([^/?#]+)",
            configured_export_url,
        )
        if match:
            default_period = str(match.group(3) or default_period).strip() or default_period

    workspace_path = quote(workspace_clean, safe="")
    unit_path = quote(default_unit, safe="")
    date_path = quote(date_clean, safe="")
    period_path = quote(default_period, safe="")
    return f"{base}/sy/workspaces/{workspace_path}/integrator/value/export/csv/{unit_path}/{date_path}/{period_path}"


def natisoft_energy_integrator_value_urls(
    config: dict,
    workspace_id: str,
    export_date: str,
    export_unit: str = ENERGIE_ELECTRICITY_EXPORT_UNIT,
    export_period: str = "year",
) -> list[str]:
    workspace_clean = str(workspace_id or "").strip() or "10"
    date_clean = str(export_date or "").strip() or datetime.now().strftime("%Y-%m-%d")
    default_unit = str(export_unit or ENERGIE_ELECTRICITY_EXPORT_UNIT).strip() or ENERGIE_ELECTRICITY_EXPORT_UNIT
    default_period = str(export_period or "year").strip() or "year"

    urls: list[str] = []
    for base in natisoft_base_urls(config):
        urls.extend(
            [
                f"{base}/sy/workspaces/{quote(workspace_clean, safe='')}/integrator/value/export/csv/{quote(default_unit, safe='')}/{quote(date_clean, safe='')}/{quote(default_period, safe='')}",
                f"{base}/api/sy/workspaces/{quote(workspace_clean, safe='')}/integrator/value/export/csv/{quote(default_unit, safe='')}/{quote(date_clean, safe='')}/{quote(default_period, safe='')}",
                f"{base}/api/api/sy/workspaces/{quote(workspace_clean, safe='')}/integrator/value/export/csv/{quote(default_unit, safe='')}/{quote(date_clean, safe='')}/{quote(default_period, safe='')}",
            ]
        )

    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        clean = str(url or "").strip()
        if clean and clean not in seen:
            seen.add(clean)
            deduped.append(clean)
    return deduped


def natisoft_biomethane_volume_urls(config: dict, workspace_id: str) -> list[str]:
    workspace_clean = str(workspace_id or "").strip() or "10"
    urls: list[str] = []
    for base in natisoft_base_urls(config):
        urls.extend(
            [
                f"{base}/sy/workspaces/{workspace_clean}/integrators/volume/export/csv",
                f"{base}/api/api/workspaces/{workspace_clean}/integrators/volume/export/csv",
                f"{base}/api/workspaces/{workspace_clean}/integrators/volume/export/csv",
                f"{base}/api/sy/workspaces/{workspace_clean}/integrators/volume/export/csv",
            ]
        )

    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        clean = str(url or "").strip()
        if clean and clean not in seen:
            seen.add(clean)
            deduped.append(clean)
    return deduped


def infer_natisoft_model_name_from_response(response: requests.Response | None, df: pd.DataFrame, fallback: str) -> str:
    fallback_clean = str(fallback or "").strip() or "unknown_model"

    try:
        response_url = str(getattr(response, "url", "") or "")
        if response_url:
            match = re.search(r"/model/([^/]+)/export/csv", response_url)
            if match:
                detected = str(match.group(1) or "").strip()
                if detected:
                    return detected
    except Exception:
        pass

    if df is None or df.empty:
        return fallback_clean

    possible_model_columns = [
        "model",
        "model_name",
        "element.model",
        "integrator",
        "integrator_name",
    ]
    col_map = {str(col).strip().lower(): str(col) for col in df.columns}
    for candidate in possible_model_columns:
        source_col = col_map.get(candidate)
        if not source_col:
            continue
        values = (
            df[source_col]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
        )
        if not values.empty:
            return str(values.iloc[0]).strip()

    return fallback_clean


def _filter_natisoft_epurateur_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    pattern = r"epurateur|épurateur"

    try:
        as_text = df.astype(str)
        row_mask = as_text.apply(lambda col: col.str.contains(pattern, case=False, na=False, regex=True)).any(axis=1)
        if bool(row_mask.any()):
            return df.loc[row_mask].reset_index(drop=True)
    except Exception:
        pass

    matching_columns = [
        column
        for column in df.columns
        if re.search(pattern, str(column), flags=re.IGNORECASE)
    ]
    if matching_columns:
        return df[matching_columns].copy()

    return df


def natisoft_base_urls(config: dict) -> list[str]:
    bases: list[str] = []
    for raw in [str(config.get("login_url", "") or "").strip(), str(config.get("export_url", "") or "").strip()]:
        if not raw:
            continue
        parsed = urlparse(raw)
        if parsed.scheme and parsed.netloc:
            base = f"{parsed.scheme}://{parsed.netloc}"
            if base not in bases:
                bases.append(base)

    if not bases:
        bases.append("https://natisoft-connect.valpronat.com")
    return bases


def fetch_natisoft_torchere_data(workspace_id: str, group_id: str, model_name: str = TORCHERE_DEFAULT_MODEL) -> pd.DataFrame:
    config = get_natisoft_config()
    missing = [
        key
        for key in ["username", "password", "client_id", "client_secret"]
        if not str(config.get(key, "")).strip()
    ]
    if missing:
        raise RuntimeError(
            "Configuration Natisoft incomplète. Ajoutez NATISOFT_USERNAME, NATISOFT_PASSWORD, "
            "NATISOFT_CLIENT_ID, NATISOFT_CLIENT_SECRET dans .streamlit/secrets.toml ou variables d'environnement."
        )

    payload_login = {
        "username": config["username"],
        "password": config["password"],
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "grant_type": "password",
        "accept_conditions": True,
    }

    token = ""
    login_errors: list[str] = []
    for login_url in natisoft_login_url_candidates(config):
        token, error_text = try_natisoft_login(login_url, payload_login)
        if token:
            break
        if error_text:
            login_errors.append(f"{login_url} -> {error_text}")
        else:
            login_errors.append(f"{login_url} -> token absent")

    if not token:
        raise RuntimeError(
            "Connexion Natisoft impossible. Endpoints testés: "
            + " | ".join(login_errors[:5])
        )

    workspace_clean = workspace_id.strip()
    group_clean = str(group_id).strip()

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=TORCHERE_LOOKBACK_DAYS)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    filters_range = [
        {"field": "raised_at", "operator": ">=", "value": start_str},
        {"field": "raised_at", "operator": "<=", "value": end_str},
        {"field": "element.group_id", "operator": "=", "value": group_clean},
    ]
    model_params = {
        "sort": "raised_at",
        "filters": json.dumps(filters_range, ensure_ascii=False),
    }
    if workspace_clean:
        model_params["workspace"] = workspace_clean

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "APP-Terrain/1.0",
        "Accept": "text/csv",
        "bkr-workspace-id": workspace_clean,
    }

    attempts: list[tuple[str, str, dict | None]] = []
    for base in natisoft_base_urls(config):
        attempts.append(
            (
                "working-time-range",
                f"{base}/api/api/workspaces/{workspace_clean}/working-time/{group_clean}",
                {"from": start_str, "to": end_str},
            )
        )
        attempts.append(
            (
                "working-time-no-params",
                f"{base}/api/api/workspaces/{workspace_clean}/working-time/{group_clean}",
                None,
            )
        )
        attempts.append(
            (
                "working-time-alt",
                f"{base}/api/workspaces/{workspace_clean}/working-time/{group_clean}",
                {"from": start_str, "to": end_str},
            )
        )

    export_url = natisoft_export_url_for_model(config, model_name=model_name)
    attempts.append(("model-export", export_url, model_params))

    diagnostics: list[str] = []
    for label, url, params in attempts:
        try:
            response = requests.get(url, params=params, headers=headers, timeout=60)
            if response.status_code >= 400:
                diagnostics.append(f"{label}:{response.status_code}")
                continue

            parsed_df = _parse_natisoft_csv_text(response.text or "")
            if not parsed_df.empty:
                return parsed_df

            diagnostics.append(f"{label}:empty")
        except Exception:
            diagnostics.append(f"{label}:err")

    raise RuntimeError(
        "Aucune donnée torchère récupérée depuis Natisoft. Tentatives: " + " | ".join(diagnostics[:8])
    )


def fetch_natisoft_energie_data(
    workspace_id: str,
    group_id: str,
    consommation_type: str,
    preferred_model: str,
    export_unit: str = ENERGIE_ELECTRICITY_EXPORT_UNIT,
) -> tuple[pd.DataFrame, str]:
    config = get_natisoft_config()
    missing = [
        key
        for key in ["username", "password", "client_id", "client_secret"]
        if not str(config.get(key, "")).strip()
    ]
    if missing:
        raise RuntimeError(
            "Configuration Natisoft incomplète. Ajoutez NATISOFT_USERNAME, NATISOFT_PASSWORD, "
            "NATISOFT_CLIENT_ID, NATISOFT_CLIENT_SECRET dans .streamlit/secrets.toml ou variables d'environnement."
        )

    payload_login = {
        "username": config["username"],
        "password": config["password"],
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "grant_type": "password",
        "accept_conditions": True,
    }

    token = ""
    login_errors: list[str] = []
    for login_url in natisoft_login_url_candidates(config):
        token, error_text = try_natisoft_login(login_url, payload_login)
        if token:
            break
        if error_text:
            login_errors.append(f"{login_url} -> {error_text}")
        else:
            login_errors.append(f"{login_url} -> token absent")

    if not token:
        raise RuntimeError(
            "Connexion Natisoft impossible. Endpoints testés: "
            + " | ".join(login_errors[:5])
        )

    workspace_clean = str(workspace_id or "").strip()
    group_clean = str(group_id or "").strip()

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=ENERGIE_LOOKBACK_DAYS)
    today_str = end_date.strftime("%Y-%m-%d")
    start_str = start_date.strftime("%Y-%m-%d")

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "APP-Terrain/1.0",
        "Accept": "text/csv",
        "bkr-workspace-id": workspace_clean,
    }
    base_urls = natisoft_base_urls(config)
    referer_base = base_urls[0] if base_urls else "https://natisoft-connect.valpronat.com"
    if workspace_clean:
        consommation_type_clean = str(consommation_type or "").strip().lower()
        referer_section = "volume" if consommation_type_clean == "biomethane" else "energy"
        headers["Referer"] = f"{referer_base}/workspaces/{workspace_clean}/integrators/{referer_section}"

    consommation_type_clean = str(consommation_type or "").strip().lower()
    model_candidates = [preferred_model] + [m for m in ENERGIE_MODEL_CANDIDATES if m != preferred_model]
    configured_export_url = str(config.get("export_url", "") or "").strip()
    attempts: list[tuple[str, str]] = []
    for idx, integrator_value_url in enumerate(
        natisoft_energy_integrator_value_urls(
            config,
            workspace_clean,
            today_str,
            export_unit=export_unit,
        ),
        start=1,
    ):
        attempts.append((f"integrator_value_{idx}", integrator_value_url))
    if configured_export_url and "/integrator/value/export/csv/" in configured_export_url:
        attempts.append(("configured", configured_export_url))
    if consommation_type_clean == "biomethane":
        for idx, volume_url in enumerate(natisoft_biomethane_volume_urls(config, workspace_clean), start=1):
            attempts.append((f"volume_alt_{idx}", volume_url))
    else:
        for model_name in model_candidates:
            attempts.append((model_name, natisoft_export_url_for_model(config, model_name=model_name)))

    dedup_attempts: list[tuple[str, str]] = []
    seen_urls: set[str] = set()
    for label, url in attempts:
        url_clean = str(url or "").strip()
        if not url_clean or url_clean in seen_urls:
            continue
        seen_urls.add(url_clean)
        dedup_attempts.append((label, url_clean))

    diagnostics: list[str] = []
    collected_frames: list[pd.DataFrame] = []
    resolved_model = ""

    for attempt_label, export_url in dedup_attempts:
        model_params: dict | None
        if "/integrator/value/export/csv/" in export_url or "/integrators/volume/export/csv" in export_url:
            model_params = {
                "from": start_str,
                "to": today_str,
                "start": start_str,
                "end": today_str,
                "start_date": start_str,
                "end_date": today_str,
            }
            if group_clean:
                model_params["group_id"] = group_clean
            if workspace_clean:
                model_params["workspace"] = workspace_clean
        else:
            filters_for_export = [
                {"field": "raised_at", "operator": ">=", "value": start_str},
                {"field": "raised_at", "operator": "<=", "value": today_str},
                {"field": "element.group_id", "operator": "=", "value": group_clean},
            ]
            model_params = {
                "sort": "raised_at",
                "filters": json.dumps(filters_for_export, ensure_ascii=False),
            }
            if workspace_clean:
                model_params["workspace"] = workspace_clean

        try:
            response = requests.get(export_url, params=model_params, headers=headers, timeout=60)
            if response.status_code >= 400:
                diagnostics.append(f"{attempt_label}:{response.status_code}")
                continue

            parsed_df = _parse_natisoft_csv_text(response.text or "")
            parsed_df = _coerce_single_column_natisoft_df(parsed_df)
            if consommation_type_clean == "epurateur" and not parsed_df.empty:
                parsed_df = _filter_natisoft_epurateur_rows(parsed_df)
            if not parsed_df.empty:
                attempt_model = infer_natisoft_model_name_from_response(
                    response,
                    parsed_df,
                    fallback=attempt_label if attempt_label != "configured" else preferred_model,
                )
                diagnostics.append(f"{attempt_label}:ok({len(parsed_df.index)})")
                return parsed_df.reset_index(drop=True), (attempt_model or preferred_model)

            diagnostics.append(f"{attempt_label}:empty")
        except Exception:
            diagnostics.append(f"{attempt_label}:err")

    if collected_frames:
        merged_df = pd.concat(collected_frames, ignore_index=True)
        merged_df = merged_df.drop_duplicates().reset_index(drop=True)
        return merged_df, (resolved_model or preferred_model)

    raise RuntimeError(
        "Aucune donnée énergie récupérée depuis Natisoft "
        f"({consommation_type}). Tentatives: " + " | ".join(diagnostics[:8])
    )


def persist_energie_to_supabase(
    client: Client,
    site_id: str,
    workspace_id: str,
    group_id: str,
    consommation_type: str,
    model_name: str,
    df: pd.DataFrame,
) -> tuple[int, int]:
    if df.empty:
        return 0, 0

    sync_date = datetime.now().strftime("%Y-%m-%d")
    type_clean = str(consommation_type or "").strip().lower()
    existing_row_indexes: set[int] = set()
    try:
        existing_rows = (
            client.table(TBL_ENERGIE)
            .select("row_index")
            .eq("site_id", site_id)
            .eq("workspace_id", workspace_id)
            .eq("group_id", group_id)
            .eq("consommation_type", type_clean)
            .eq("model_name", model_name)
            .eq("sync_date", sync_date)
            .execute()
            .data
            or []
        )
        for row in existing_rows:
            try:
                existing_row_indexes.add(int(row.get("row_index")))
            except Exception:
                pass
    except Exception:
        existing_row_indexes = set()

    payload: list[dict] = []
    imported_at = datetime.now().isoformat(timespec="seconds")
    skipped_count = 0
    for idx, (_, row) in enumerate(df.reset_index(drop=True).iterrows()):
        if idx in existing_row_indexes:
            skipped_count += 1
            continue

        row_data = {str(col): _json_safe_value(val) for col, val in row.items()}
        payload.append(
            {
                "site_id": site_id,
                "workspace_id": workspace_id,
                "group_id": str(group_id),
                "consommation_type": type_clean,
                "model_name": str(model_name),
                "sync_date": sync_date,
                "row_index": idx,
                "row_data": row_data,
                "imported_at": imported_at,
            }
        )

    try:
        chunk_size = 500
        for start in range(0, len(payload), chunk_size):
            insert_with_schema_fallback(client, TBL_ENERGIE, payload[start : start + chunk_size])
    except Exception as error:
        raise RuntimeError(
            "Import en table énergie impossible. Vérifiez que la table `energie_data` existe côté Supabase. "
            f"Détail: {error}"
        ) from error

    return len(payload), skipped_count


def sync_energie_hourly(
    client: Client,
    site_id: str,
    workspace_id: str,
    group_id: str,
    consommation_type: str,
    force: bool = False,
    preferred_model: str = "",
    export_unit: str = ENERGIE_ELECTRICITY_EXPORT_UNIT,
) -> tuple[pd.DataFrame, dict]:
    workspace_clean = str(workspace_id or "").strip()
    group_input = str(group_id or "").strip()

    if not workspace_clean and group_input:
        for ws_candidate, grp_candidate in ENERGIE_WORKSPACE_GROUP_MAP.items():
            if str(grp_candidate or "").strip() == group_input:
                workspace_clean = str(ws_candidate or "").strip()
                break

    group_clean, _ = resolve_energie_group_for_workspace(workspace_clean, group_input)
    type_clean = str(consommation_type or "").strip().lower()
    script_config = get_energie_import_script_config_for_site(site_id)
    model_from_script = str(script_config.get(f"{type_clean}_model", "") or "").strip()
    model_hint = str(
        preferred_model
        or model_from_script
        or ENERGIE_DEFAULT_MODELS.get(type_clean, ENERGIE_MODEL_CANDIDATES[0])
    ).strip()

    if not workspace_clean:
        raise RuntimeError("Aucun workspace Natisoft configuré pour cette usine.")
    if not group_clean:
        raise RuntimeError("Aucun groupe énergie Natisoft configuré pour cette usine.")
    if not type_clean:
        raise RuntimeError("Type de consommation énergie manquant (process/epurateur).")

    cached_df, cached_meta = load_energie_cache(site_id, type_clean)
    last_sync_iso = str(cached_meta.get("last_sync", "") or "").strip()

    should_sync = force
    if not should_sync:
        if not last_sync_iso:
            should_sync = True
        else:
            try:
                last_sync = datetime.fromisoformat(last_sync_iso)
                should_sync = datetime.now() - last_sync >= timedelta(hours=1)
            except Exception:
                should_sync = True

    if not should_sync:
        return cached_df, cached_meta

    df, resolved_model = fetch_natisoft_energie_data(
        workspace_id=workspace_clean,
        group_id=group_clean,
        consommation_type=type_clean,
        preferred_model=model_hint,
        export_unit=export_unit,
    )
    imported_rows, skipped_rows = persist_energie_to_supabase(
        client,
        site_id=site_id,
        workspace_id=workspace_clean,
        group_id=group_clean,
        consommation_type=type_clean,
        model_name=resolved_model,
        df=df,
    )
    new_meta = {
        "last_sync": datetime.now().isoformat(timespec="seconds"),
        "rows": int(len(df.index)),
        "workspace_id": workspace_clean,
        "group_id": group_clean,
        "consommation_type": type_clean,
        "model_name": resolved_model,
        "imported_rows": imported_rows,
        "skipped_rows": skipped_rows,
    }
    save_energie_cache(site_id, type_clean, df, new_meta)
    return df, new_meta


def persist_torchere_to_supabase(
    client: Client,
    site_id: str,
    workspace_id: str,
    group_id: str,
    model_name: str,
    df: pd.DataFrame,
) -> tuple[int, int]:
    if df.empty:
        return 0, 0

    sync_date = datetime.now().strftime("%Y-%m-%d")
    existing_row_indexes: set[int] = set()
    try:
        existing_rows = (
            client.table(TBL_SECURITE_TORCHERE)
            .select("row_index")
            .eq("site_id", site_id)
            .eq("workspace_id", workspace_id)
            .eq("group_id", group_id)
            .eq("model_name", model_name)
            .eq("sync_date", sync_date)
            .execute()
            .data
            or []
        )
        for row in existing_rows:
            try:
                existing_row_indexes.add(int(row.get("row_index")))
            except Exception:
                pass
    except Exception:
        existing_row_indexes = set()

    payload: list[dict] = []
    imported_at = datetime.now().isoformat(timespec="seconds")
    skipped_count = 0
    for idx, (_, row) in enumerate(df.reset_index(drop=True).iterrows()):
        if idx in existing_row_indexes:
            skipped_count += 1
            continue

        row_data = {str(col): _json_safe_value(val) for col, val in row.items()}
        payload.append(
            {
                "site_id": site_id,
                "workspace_id": workspace_id,
                "group_id": str(group_id),
                "model_name": str(model_name),
                "sync_date": sync_date,
                "row_index": idx,
                "row_data": row_data,
                "imported_at": imported_at,
            }
        )

    try:
        chunk_size = 500
        for start in range(0, len(payload), chunk_size):
            insert_with_schema_fallback(client, TBL_SECURITE_TORCHERE, payload[start : start + chunk_size])
    except Exception as error:
        raise RuntimeError(
            "Import en table sécurité torchère impossible. Vérifiez que la table `securite_torchere_data` existe côté Supabase. "
            f"Détail: {error}"
        ) from error

    return len(payload), skipped_count


def sync_torchere_hourly(
    client: Client,
    site_id: str,
    workspace_id: str,
    group_id: str,
    force: bool = False,
    model_name: str = TORCHERE_DEFAULT_MODEL,
) -> tuple[pd.DataFrame, dict]:
    workspace_clean = workspace_id.strip()
    group_clean, _ = resolve_torchere_group_for_workspace(workspace_clean, str(group_id or ""))
    if not workspace_clean:
        raise RuntimeError("Aucun workspace Natisoft configuré pour cette usine.")
    if not group_clean:
        raise RuntimeError("Aucun groupe torchère Natisoft configuré pour cette usine.")

    cached_df, cached_meta = load_torchere_cache(site_id)
    last_sync_iso = str(cached_meta.get("last_sync", "") or "").strip()

    should_sync = force
    if not should_sync:
        if not last_sync_iso:
            should_sync = True
        else:
            try:
                last_sync = datetime.fromisoformat(last_sync_iso)
                should_sync = datetime.now() - last_sync >= timedelta(hours=1)
            except Exception:
                should_sync = True

    if not should_sync:
        return cached_df, cached_meta

    df = fetch_natisoft_torchere_data(workspace_id=workspace_clean, group_id=group_clean, model_name=model_name)
    imported_rows, skipped_rows = persist_torchere_to_supabase(
        client,
        site_id=site_id,
        workspace_id=workspace_clean,
        group_id=group_clean,
        model_name=model_name,
        df=df,
    )
    new_meta = {
        "last_sync": datetime.now().isoformat(timespec="seconds"),
        "rows": int(len(df.index)),
        "workspace_id": workspace_clean,
        "group_id": group_clean,
        "model_name": model_name,
        "imported_rows": imported_rows,
        "skipped_rows": skipped_rows,
    }
    save_torchere_cache(site_id, df, new_meta)
    return df, new_meta


def sync_maintenance_hourly(client: Client, site_id: str, workspace_id: str, force: bool = False) -> tuple[pd.DataFrame, dict]:
    workspace_clean = workspace_id.strip()
    if not workspace_clean:
        raise RuntimeError("Aucun workspace Natisoft configuré pour cette usine.")

    cached_df, cached_meta = load_maintenance_cache(site_id)
    last_sync_iso = str(cached_meta.get("last_sync", "") or "").strip()

    should_sync = force
    if not should_sync:
        if not last_sync_iso:
            should_sync = True
        else:
            try:
                last_sync = datetime.fromisoformat(last_sync_iso)
                should_sync = datetime.now() - last_sync >= timedelta(hours=1)
            except Exception:
                should_sync = True

    if not should_sync:
        return cached_df, cached_meta

    df = fetch_natisoft_hourly_data(workspace_id=workspace_clean)
    imported_rows, skipped_rows = persist_maintenance_to_supabase(client, site_id, workspace_clean, df)
    new_meta = {
        "last_sync": datetime.now().isoformat(timespec="seconds"),
        "rows": int(len(df.index)),
        "workspace_id": workspace_clean,
        "imported_rows": imported_rows,
        "skipped_rows": skipped_rows,
    }
    save_maintenance_cache(site_id, df, new_meta)
    return df, new_meta


def maintenance_module(client: Client, site_id: str, site_code: str, site_name: str) -> None:
    st.subheader("Maintenance")
    render_help_for_screen("maintenance")
    st.caption("Récupération automatique horaire des données de fonctionnement Natisoft")

    workspace_id = get_workspace_for_site(site_id, site_code, site_name)
    if workspace_id:
        st.caption(f"Workspace Natisoft configuré pour cette usine : {workspace_id}")
    else:
        st.warning("Aucun workspace Natisoft configuré pour cette usine (paramétrez-le dans Administration > Sites).")

    auto_refresh_key = f"maintenance_last_refresh_check_{site_id}"
    if auto_refresh_key not in st.session_state:
        st.session_state[auto_refresh_key] = ""

    try:
        df, meta = sync_maintenance_hourly(client, site_id, workspace_id, force=False)
    except Exception as error:
        st.error(f"Échec synchronisation automatique Maintenance: {error}")
        df, meta = load_maintenance_cache(site_id)

    c1, c2, c3 = st.columns(3)
    c1.metric("Lignes récupérées", str(int(len(df.index))) if not df.empty else "0")
    c2.metric("Dernière synchro", str(meta.get("last_sync", "-") or "-"))
    c3.metric("Nouvelles importées", str(meta.get("imported_rows", 0)))
    st.caption(f"Lignes déjà présentes ignorées: {meta.get('skipped_rows', 0)}")

    if st.button("Forcer la synchronisation maintenant", type="primary", use_container_width=True):
        try:
            df, meta = sync_maintenance_hourly(client, site_id, workspace_id, force=True)
            st.success(f"Synchronisation forcée réussie. {len(df.index)} lignes récupérées.")
            st.rerun()
        except Exception as error:
            st.error(f"Erreur synchro forcée: {error}")

    summary_state_key = f"maintenance_runtime_summary_{site_id}"
    summary_meta_state_key = f"maintenance_runtime_summary_meta_{site_id}"

    if st.button("Synthèse historique par équipement", use_container_width=True):
        try:
            with st.spinner("Calcul de la synthèse historique depuis la base..."):
                history_df = load_maintenance_history_from_supabase(client, site_id, workspace_id)
                runtime_summary_df = build_runtime_summary_by_equipment(history_df)

            st.session_state[summary_state_key] = runtime_summary_df
            st.session_state[summary_meta_state_key] = {
                "rows": int(len(history_df.index)),
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            if runtime_summary_df.empty:
                st.warning("Aucune synthèse calculable sur les données historisées (colonnes Journalier non détectées).")
            else:
                st.success(f"Synthèse calculée pour {len(runtime_summary_df.index)} équipements.")
        except Exception as error:
            st.error(f"Erreur calcul synthèse historique: {error}")

    runtime_summary_df = st.session_state.get(summary_state_key, pd.DataFrame())
    runtime_summary_meta = st.session_state.get(summary_meta_state_key, {})

    st.markdown("### Synthèse historique temps de fonctionnement")
    if isinstance(runtime_summary_df, pd.DataFrame) and not runtime_summary_df.empty:
        st.caption(
            f"Lignes historisées analysées : {runtime_summary_meta.get('rows', 0)} · "
            f"Générée le {runtime_summary_meta.get('generated_at', '-') }"
        )
        st.dataframe(runtime_summary_df, use_container_width=True, hide_index=True)
    else:
        st.info("Cliquez sur 'Synthèse historique par équipement' pour calculer la synthèse depuis la base.")

    st.markdown("### Données équipements")
    if df.empty:
        st.info("Aucune donnée disponible pour le moment.")
    else:
        preview_df = df.copy()
        if len(preview_df.index) > 2000:
            st.caption("Affichage limité aux 2000 premières lignes pour l'interface.")
            preview_df = preview_df.head(2000)
        st.dataframe(preview_df, use_container_width=True, hide_index=True)


def securite_module(
    client: Client,
    site_id: str,
    site_code: str,
    site_name: str,
    selected_roles: list[str],
    rights: set[tuple[str, str]],
) -> None:
    st.subheader("Sécurité")
    render_help_for_screen("securite")

    workspace_id = get_workspace_for_site(site_id, site_code, site_name)
    group_id = get_torchere_group_for_site(site_id, site_code, site_name)
    group_id, _ = resolve_torchere_group_for_workspace(workspace_id, group_id)
    model_name = TORCHERE_DEFAULT_MODEL

    try:
        df, meta = sync_torchere_hourly(
            client,
            site_id=site_id,
            workspace_id=workspace_id,
            group_id=group_id,
            force=False,
            model_name=model_name,
        )
    except Exception as error:
        st.error(f"Échec synchronisation automatique registre torchère: {error}")
        df, meta = load_torchere_cache(site_id)

    history_df = pd.DataFrame()
    try:
        history_df = load_torchere_history_from_supabase(
            client,
            site_id=site_id,
            workspace_id=workspace_id,
            group_id=group_id,
            model_name=model_name,
        )
    except Exception:
        history_df = pd.DataFrame()

    runtime_source_df = history_df if not history_df.empty else df
    runtime_daily_df = build_torchere_daily_runtime(runtime_source_df)

    st.markdown("### Temps de fonctionnement torchère")
    if runtime_daily_df.empty:
        st.info("Aucune donnée de fonctionnement torchère exploitable pour tracer le graphique.")
        return

    monthly_df = (
        runtime_daily_df.groupby(["month_date", "month_label"], as_index=False)["runtime_hours"]
        .sum()
        .rename(columns={"runtime_hours": "hours"})
        .sort_values("month_date")
        .reset_index(drop=True)
    )

    month_selection = alt.selection_point(fields=["month_label"], on="click", clear="dblclick")

    monthly_line = (
        alt.Chart(monthly_df)
        .mark_line(color=BRAND_PRIMARY_DARK, strokeWidth=2)
        .encode(
            x=alt.X("month_date:T", title="Mois", axis=alt.Axis(format="%Y-%m")),
            y=alt.Y("hours:Q", title="Heures de fonctionnement"),
            tooltip=[
                alt.Tooltip("month_label:N", title="Mois"),
                alt.Tooltip("hours:Q", title="Heures", format=".2f"),
            ],
        )
    )

    monthly_points = (
        alt.Chart(monthly_df)
        .mark_circle(size=95)
        .encode(
            x=alt.X("month_date:T", axis=alt.Axis(format="%Y-%m")),
            y=alt.Y("hours:Q"),
            color=alt.condition(month_selection, alt.value(BRAND_PRIMARY), alt.value("#D6C5E1")),
            tooltip=[
                alt.Tooltip("month_label:N", title="Mois"),
                alt.Tooltip("hours:Q", title="Heures", format=".2f"),
            ],
        )
        .add_params(month_selection)
    )

    monthly_chart = (monthly_line + monthly_points).properties(height=260, title="Temps de fonctionnement mensuel")

    daily_chart = (
        alt.Chart(runtime_daily_df)
        .mark_bar(color=BRAND_PRIMARY_DARK)
        .encode(
            x=alt.X("date:T", title="Jour"),
            y=alt.Y("runtime_hours:Q", title="Heures par jour"),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("runtime_hours:Q", title="Heures", format=".3f"),
                alt.Tooltip("runtime_hms:N", title="Durée (HH:MM:SS)"),
            ],
        )
        .transform_filter(month_selection)
        .properties(height=240, title="Détail journalier du mois sélectionné")
    )

    st.caption("Cliquez sur un point du graphe mensuel pour afficher le détail journalier. Double-clic pour réinitialiser.")
    combined_chart = alt.vconcat(monthly_chart, daily_chart).resolve_scale(x="independent")
    st.altair_chart(combined_chart, use_container_width=True)


def energie_electricite_module(
    client: Client,
    site_id: str,
    site_code: str,
    site_name: str,
    selected_roles: list[str],
    rights: set[tuple[str, str]],
) -> None:
    workspace_id = get_workspace_for_site(site_id, site_code, site_name)
    group_id = get_energie_group_for_site(site_id, site_code, site_name)
    group_id, _ = resolve_energie_group_for_workspace(workspace_id, group_id)

    consommation_specs = [
        ("process", "Process"),
        ("epurateur", "Épurateur"),
    ]

    sync_frames: list[pd.DataFrame] = []
    for consommation_type, _ in consommation_specs:
        model_hint = ENERGIE_DEFAULT_MODELS.get(consommation_type, ENERGIE_MODEL_CANDIDATES[0])
        try:
            raw_df, meta = sync_energie_hourly(
                client,
                site_id=site_id,
                workspace_id=workspace_id,
                group_id=group_id,
                consommation_type=consommation_type,
                force=False,
                preferred_model=model_hint,
                export_unit=ENERGIE_ELECTRICITY_EXPORT_UNIT,
            )
        except Exception as error:
            st.error(f"Échec synchronisation automatique énergie ({consommation_type}): {error}")
            raw_df, meta = load_energie_cache(site_id, consommation_type)

        model_used = str(meta.get("model_name", "") or model_hint)
        history_df = pd.DataFrame()
        history_error = ""
        try:
            history_df = load_energie_history_from_supabase(
                client,
                site_id=site_id,
                workspace_id=workspace_id,
                group_id=group_id,
                consommation_type=consommation_type,
                model_name=model_used,
            )
        except Exception as error:
            history_error = str(error)

        source_df = history_df if not history_df.empty else raw_df
        daily_df = build_energie_daily_consumption(source_df, consommation_type, site_id=site_id)
        if not daily_df.empty:
            sync_frames.append(daily_df)

        _ = meta
        _ = history_error

    combined_daily_df = pd.concat(sync_frames, ignore_index=True) if sync_frames else pd.DataFrame()

    st.markdown("### Consommations énergie")
    if combined_daily_df.empty:
        st.info("Aucune donnée de consommation énergie exploitable pour tracer le graphique.")
        return

    display_type_map = {
        "process": "Process",
        "epurateur": "Épuration",
    }

    monthly_df = (
        combined_daily_df.groupby(["month_date", "month_label", "consommation_type"], as_index=False)["consumption_value"]
        .sum()
        .rename(columns={"consumption_value": "value"})
        .sort_values("month_date")
        .reset_index(drop=True)
    )
    monthly_df["type_label"] = monthly_df["consommation_type"].map(display_type_map).fillna(monthly_df["consommation_type"])

    daily_chart_df = combined_daily_df.copy()
    daily_chart_df["type_label"] = daily_chart_df["consommation_type"].map(display_type_map).fillna(daily_chart_df["consommation_type"])

    month_selection = alt.selection_point(fields=["month_date"], on="click", clear="dblclick")

    monthly_chart = (
        alt.Chart(monthly_df)
        .mark_bar()
        .encode(
            x=alt.X("month_date:T", title="Mois", axis=alt.Axis(format="%Y-%m")),
            y=alt.Y("value:Q", title="Consommation mensuelle totale"),
            color=alt.Color(
                "type_label:N",
                title="Type",
                scale=alt.Scale(domain=["Process", "Épuration"], range=[BRAND_PRIMARY_DARK, BRAND_TEXT]),
            ),
            order=alt.Order("type_label:N", sort="ascending"),
            tooltip=[
                alt.Tooltip("month_label:N", title="Mois"),
                alt.Tooltip("type_label:N", title="Type"),
                alt.Tooltip("value:Q", title="Valeur", format=".2f"),
            ],
        )
        .add_params(month_selection)
        .properties(height=260, title="Histogramme mensuel cumulé (process + épuration)")
    )

    daily_chart = (
        alt.Chart(daily_chart_df)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("date:T", title="Jour"),
            y=alt.Y("consumption_value:Q", title="Consommation journalière"),
            color=alt.Color(
                "type_label:N",
                title="Type",
                scale=alt.Scale(domain=["Process", "Épuration"], range=[BRAND_PRIMARY_DARK, BRAND_TEXT]),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("type_label:N", title="Type"),
                alt.Tooltip("consumption_value:Q", title="Valeur", format=".3f"),
            ],
        )
        .transform_filter(month_selection)
        .properties(height=260, title="Courbes journalières du mois sélectionné (process et épuration)")
    )

    st.caption("Cliquez sur un mois pour afficher le détail journalier. Double-clic pour réinitialiser.")
    st.altair_chart(alt.vconcat(monthly_chart, daily_chart).resolve_scale(x="independent"), use_container_width=True)


def biomethane_module(
    client: Client,
    site_id: str,
    site_code: str,
    site_name: str,
    selected_roles: list[str],
    rights: set[tuple[str, str]],
) -> None:

    is_admin = "administrateur" in selected_roles
    can_force_sync = has_permission(selected_roles, rights, "energie", "sync")
    can_debug = has_permission(selected_roles, rights, "energie", "debug")

    workspace_id = get_workspace_for_site(site_id, site_code, site_name)
    group_id = get_energie_group_for_site(site_id, site_code, site_name)

    site_code_upper = str(site_code or "").strip().upper()
    site_name_upper = str(site_name or "").strip().upper()
    is_premery_or_dual = (
        "PREMERY" in site_code_upper
        or "PREMERY" in site_name_upper
        or "DUAL" in site_code_upper
        or "DUAL" in site_name_upper
    )

    if not str(workspace_id or "").strip() and is_premery_or_dual:
        workspace_id = "10"
    if not str(group_id or "").strip() and is_premery_or_dual:
        group_id = ENERGIE_DEFAULT_GROUP_DUAL

    group_id, _ = resolve_energie_group_for_workspace(workspace_id, group_id)

    type_key = "biomethane"
    script_config = get_energie_import_script_config_for_site(site_id)
    model_hint = str(
        script_config.get("biomethane_model", "")
        or ENERGIE_DEFAULT_MODELS.get("biomethane", ENERGIE_MODEL_CANDIDATES[0])
    ).strip()

    try:
        raw_df, meta = sync_energie_hourly(
            client,
            site_id=site_id,
            workspace_id=workspace_id,
            group_id=group_id,
            consommation_type=type_key,
            force=False,
            preferred_model=model_hint,
            export_unit=ENERGIE_BIOMETHANE_EXPORT_UNIT,
        )

        cached_model_name = str(meta.get("model_name", "") or "").strip().lower()
        if cached_model_name == "hourly_counter_value":
            raw_df, meta = sync_energie_hourly(
                client,
                site_id=site_id,
                workspace_id=workspace_id,
                group_id=group_id,
                consommation_type=type_key,
                force=True,
                preferred_model="volume",
                export_unit=ENERGIE_BIOMETHANE_EXPORT_UNIT,
            )
    except Exception as error:
        st.error(f"Échec synchronisation automatique biométhane: {error}")
        raw_df, meta = load_energie_cache(site_id, type_key)

    model_used = str(meta.get("model_name", "") or model_hint)
    history_df = pd.DataFrame()
    history_error = ""
    try:
        history_df = load_energie_history_from_supabase(
            client,
            site_id=site_id,
            workspace_id=workspace_id,
            group_id=group_id,
            consommation_type=type_key,
            model_name=model_used,
        )
    except Exception as error:
        history_error = str(error)

    configured_date_idx = int(script_config.get("date_column_index", ENERGIE_DATE_COLUMN_INDEX))
    configured_bio_idx = int(script_config.get("biomethane_column_index", ENERGIE_BIOMETHANE_COLUMN_INDEX))
    configured_biogas_idx = int(
        script_config.get("biogas_column_index", script_config.get("process_column_index", ENERGIE_BIOGAZ_COLUMN_INDEX))
    )

    biogas_type_key = str(script_config.get("biogas_source_type", "biomethane") or "biomethane").strip().lower()
    if biogas_type_key not in {"process", "epurateur", "biomethane"}:
        biogas_type_key = "process"
    biogas_model_hint = str(
        script_config.get(f"{biogas_type_key}_model", "")
        or ENERGIE_DEFAULT_MODELS.get(biogas_type_key, ENERGIE_MODEL_CANDIDATES[0])
    ).strip()

    biogas_raw_df = pd.DataFrame()
    biogas_meta: dict = {}
    biogas_history_df = pd.DataFrame()
    biogas_history_error = ""

    if biogas_type_key == type_key:
        biogas_raw_df = raw_df.copy()
        biogas_meta = dict(meta or {})
        biogas_history_df = history_df.copy()
    else:
        try:
            biogas_raw_df, biogas_meta = sync_energie_hourly(
                client,
                site_id=site_id,
                workspace_id=workspace_id,
                group_id=group_id,
                consommation_type=biogas_type_key,
                force=False,
                preferred_model=biogas_model_hint,
                export_unit=ENERGIE_BIOMETHANE_EXPORT_UNIT,
            )
        except Exception as error:
            biogas_history_error = str(error)
            biogas_raw_df, biogas_meta = load_energie_cache(site_id, biogas_type_key)

        biogas_model_used = str(biogas_meta.get("model_name", "") or biogas_model_hint)
        try:
            biogas_history_df = load_energie_history_from_supabase(
                client,
                site_id=site_id,
                workspace_id=workspace_id,
                group_id=group_id,
                consommation_type=biogas_type_key,
                model_name=biogas_model_used,
            )
        except Exception as error:
            biogas_history_error = str(error)

    any_model_history_df = pd.DataFrame()

    def _build_series_from_source(df_source: pd.DataFrame, value_idx_1_based: int, series_label: str) -> pd.DataFrame:
        if df_source.empty:
            return pd.DataFrame()

        source_df = _coerce_single_column_natisoft_df(df_source)
        columns_in_order = [str(col) for col in source_df.columns]
        if not columns_in_order:
            return pd.DataFrame()

        date_idx = configured_date_idx - 1
        value_idx = int(value_idx_1_based) - 1

        if min(date_idx, value_idx) < 0:
            return pd.DataFrame()
        if max(date_idx, value_idx) >= len(columns_in_order):
            return pd.DataFrame()

        date_column = columns_in_order[date_idx]
        value_column = columns_in_order[value_idx]

        if date_column not in source_df.columns or value_column not in source_df.columns:
            return pd.DataFrame()

        working_df = source_df[[date_column, value_column]].copy()
        working_df["date"] = working_df[date_column].apply(_parse_energie_date_value)
        working_df = working_df[working_df["date"].notna()]
        if working_df.empty:
            return pd.DataFrame()

        working_df["consumption_value"] = working_df[value_column].apply(_parse_decimal_number)
        series_df = working_df[["date", "consumption_value"]].copy()
        series_df = series_df[series_df["consumption_value"] > 0]
        series_df = series_df.sort_values("date").reset_index(drop=True)
        if series_df.empty:
            return pd.DataFrame()
        series_df["series_label"] = series_label
        return series_df

    biomethane_chart_df = pd.DataFrame()
    biomethane_source_candidates: list[pd.DataFrame] = [raw_df, history_df]
    biogas_source_candidates: list[pd.DataFrame] = [biogas_raw_df, biogas_history_df]

    source_candidates: list[pd.DataFrame] = [raw_df, history_df]
    try:
        any_model_history_df = load_energie_history_from_supabase_any_model(
            client,
            site_id=site_id,
            workspace_id=workspace_id,
            group_id=group_id,
            consommation_type=type_key,
        )
    except Exception:
        any_model_history_df = pd.DataFrame()
    biomethane_source_candidates.append(any_model_history_df)

    biogas_any_model_history_df = pd.DataFrame()
    try:
        biogas_any_model_history_df = load_energie_history_from_supabase_any_model(
            client,
            site_id=site_id,
            workspace_id=workspace_id,
            group_id=group_id,
            consommation_type=biogas_type_key,
        )
    except Exception:
        biogas_any_model_history_df = pd.DataFrame()
    biogas_source_candidates.append(biogas_any_model_history_df)

    biomethane_daily_df = pd.DataFrame()
    for source_candidate in biomethane_source_candidates:
        candidate_series = _build_series_from_source(source_candidate, configured_bio_idx, "Biométhane produit")
        if not candidate_series.empty:
            biomethane_daily_df = candidate_series
            break

    biogas_daily_df = pd.DataFrame()
    for source_candidate in biogas_source_candidates:
        candidate_series = _build_series_from_source(source_candidate, configured_biogas_idx, "Biogaz traité")
        if not candidate_series.empty:
            biogas_daily_df = candidate_series
            break

    if not biomethane_daily_df.empty:
        biomethane_chart_df = pd.concat([biomethane_chart_df, biomethane_daily_df], ignore_index=True)
    if not biogas_daily_df.empty:
        biomethane_chart_df = pd.concat([biomethane_chart_df, biogas_daily_df], ignore_index=True)

    if biomethane_chart_df.empty:
        st.info("Aucune donnée de production biométhane exploitable pour tracer le graphique.")
        return

    overview_df = biomethane_chart_df.sort_values("date").reset_index(drop=True)
    legend_swap_map = {
        "Biométhane produit": "Biogaz traité",
        "Biogaz traité": "Biométhane produit",
    }
    overview_df["series_label_display"] = overview_df["series_label"].map(legend_swap_map).fillna(overview_df["series_label"])
    overview_df["month"] = pd.to_datetime(overview_df["date"]).dt.to_period("M").dt.to_timestamp()
    monthly_overview_df = (
        overview_df.groupby(["month", "series_label_display"], as_index=False)["consumption_value"].sum()
        .rename(columns={"month": "date", "series_label_display": "series_label"})
        .sort_values("date")
        .reset_index(drop=True)
    )

    biomethane_daily = overview_df[overview_df["series_label"] == "Biométhane produit"].copy()
    biogas_daily = overview_df[overview_df["series_label"] == "Biogaz traité"].copy()

    biomethane_counter_daily = pd.DataFrame()
    for source_candidate in biomethane_source_candidates:
        candidate_daily = build_energie_daily_consumption(
            source_candidate,
            consommation_type="biomethane",
            site_id=site_id,
        )
        if not candidate_daily.empty:
            biomethane_counter_daily = (
                candidate_daily[["date", "consumption_value"]]
                .sort_values("date")
                .reset_index(drop=True)
            )
            break
    if biomethane_counter_daily.empty and not biomethane_daily.empty:
        biomethane_counter_daily = biomethane_daily[["date", "consumption_value"]].copy()

    def _render_cumulative_biomethane_metrics(series_df: pd.DataFrame) -> None:
        metric_col_1, metric_col_2 = st.columns(2)
        if series_df.empty:
            metric_col_1.metric("Biométhane produit (année)", "-")
            metric_col_2.metric("Biométhane produit (10 jours)", "-")
            return

        working_df = series_df.copy()
        working_df["date"] = pd.to_datetime(working_df["date"]).dt.date
        working_df = working_df.sort_values("date").reset_index(drop=True)

        last_date = working_df["date"].max()
        year_start = date(last_date.year, 1, 1)
        ten_days_start = last_date - timedelta(days=9)

        year_scope = working_df.loc[working_df["date"] >= year_start].copy()
        ten_days_scope = working_df.loc[working_df["date"] >= ten_days_start].copy()

        year_sum = float(year_scope["consumption_value"].sum())
        ten_days_sum = float(ten_days_scope["consumption_value"].sum())
        year_days = max(int(year_scope["date"].nunique()), 1)
        ten_days = max(int(ten_days_scope["date"].nunique()), 1)

        year_avg_h = year_sum / (year_days * 24.0)
        ten_days_avg_h = ten_days_sum / (ten_days * 24.0)

        metric_col_1.metric(
            "Biométhane produit (année)",
            f"{year_avg_h:.2f} Nm3/h",
            help=(
                f"Du {year_start.strftime('%d/%m/%Y')} au {last_date.strftime('%d/%m/%Y')} | "
                f"{year_days} jour(s) | calcul: somme / jours / 24"
            ),
        )
        metric_col_2.metric(
            "Biométhane produit (10 jours)",
            f"{ten_days_avg_h:.2f} Nm3/h",
            help=(
                f"Du {ten_days_start.strftime('%d/%m/%Y')} au {last_date.strftime('%d/%m/%Y')} | "
                f"{ten_days} jour(s) | calcul: somme / jours / 24"
            ),
        )

    _render_cumulative_biomethane_metrics(biomethane_counter_daily)

    selected_view = st.radio(
        "Vue du graphique",
        options=["Mois", "Jour"],
        horizontal=True,
        key="biomethane_chart_view",
    )

    chart_df = monthly_overview_df if selected_view == "Mois" else overview_df
    selected_month_label = ""
    if selected_view == "Jour":
        daily_months = (
            pd.to_datetime(overview_df["date"])
            .dt.to_period("M")
            .dropna()
            .sort_values()
            .unique()
            .tolist()
        )
        if daily_months:
            month_options = sorted(daily_months, reverse=True)
            selected_month = st.selectbox(
                "Mois à afficher (mois + année)",
                options=month_options,
                index=0,
                format_func=lambda period_value: period_value.strftime("%m/%Y"),
                key="biomethane_daily_month",
            )
            selected_month_label = selected_month.strftime("%m/%Y")
            chart_df = overview_df[
                pd.to_datetime(overview_df["date"]).dt.to_period("M") == selected_month
            ].copy()

    x_title = "Mois" if selected_view == "Mois" else "Jour"
    y_title = "Production mensuelle" if selected_view == "Mois" else "Production journalière"
    chart_title = (
        "Production biométhane / biogaz (regroupement mensuel)"
        if selected_view == "Mois"
        else (
            f"Production biométhane / biogaz (vue journalière - {selected_month_label})"
            if selected_month_label
            else "Production biométhane / biogaz (vue journalière)"
        )
    )

    production_chart = (
        alt.Chart(chart_df)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("date:T", title=x_title),
            y=alt.Y("consumption_value:Q", title=y_title),
            color=alt.Color(
                "series_label_display:N" if selected_view == "Jour" else "series_label:N",
                title="Série",
                scale=alt.Scale(domain=["Biométhane produit", "Biogaz traité"], range=[BRAND_PRIMARY_DARK, BRAND_TEXT]),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("series_label_display:N", title="Série") if selected_view == "Jour" else alt.Tooltip("series_label:N", title="Série"),
                alt.Tooltip("consumption_value:Q", title="Valeur", format=".2f"),
            ],
        )
        .properties(height=320, title=chart_title)
    )

    st.altair_chart(production_chart, use_container_width=True)

    if is_admin or can_debug:
        with st.expander("Debug synchro biométhane", expanded=False):
            st.write(f"Workspace actif: {workspace_id or '-'}")
            st.write(f"Groupe actif: {group_id or '-'}")
            st.write(f"Modèle actif: {model_used or '-'}")
            st.write(f"Source biogaz (type): {biogas_type_key}")
            st.write(f"Unité export: {ENERGIE_BIOMETHANE_EXPORT_UNIT}")
            st.write(f"Colonne date configurée (index 1-based): {configured_date_idx}")
            st.write(f"Colonne biométhane configurée (index 1-based): {configured_bio_idx}")
            st.write(f"Colonne biogaz configurée (index 1-based): {configured_biogas_idx}")
            st.write(f"Lignes cache: {int(len(raw_df.index)) if not raw_df.empty else 0}")
            st.write(f"Lignes base: {int(len(history_df.index)) if not history_df.empty else 0}")
            st.write(f"Lignes cache biogaz: {int(len(biogas_raw_df.index)) if not biogas_raw_df.empty else 0}")
            st.write(f"Lignes base biogaz: {int(len(biogas_history_df.index)) if not biogas_history_df.empty else 0}")
            if history_error:
                st.write(f"Erreur lecture base: {history_error}")
            if biogas_history_error:
                st.write(f"Erreur lecture base biogaz: {biogas_history_error}")
            if can_force_sync:
                if st.button("Forcer la synchronisation biométhane", key="bio_force_sync_debug"):
                    try:
                        sync_energie_hourly(
                            client,
                            site_id=site_id,
                            workspace_id=workspace_id,
                            group_id=group_id,
                            consommation_type=type_key,
                            force=True,
                            preferred_model=model_hint,
                            export_unit=ENERGIE_BIOMETHANE_EXPORT_UNIT,
                        )
                        st.success("Synchronisation forcée biométhane réussie.")
                        st.rerun()
                    except Exception as error:
                        st.error(f"Erreur synchro forcée biométhane: {error}")


def energie_module(
    client: Client,
    site_id: str,
    site_code: str,
    site_name: str,
    selected_roles: list[str],
    rights: set[tuple[str, str]],
) -> None:
    st.subheader("Énergie")

    tab_bio, tab_elec = st.tabs(["Production biométhane", "Consommation électrique"])

    with tab_bio:
        biomethane_module(client, site_id, site_code, site_name, selected_roles, rights)

    with tab_elec:
        energie_electricite_module(client, site_id, site_code, site_name, selected_roles, rights)

    render_help_for_screen("energie")


def upsert_intrant_links(
    client: Client,
    intrant_name: str,
    ms_pct: float,
    mo_pct: float,
    bmp_nm3_t: float,
    masse_volumique_t_m3: float,
    selected_site_ids: list[str],
    remove_unselected_links: bool,
) -> tuple[int, int, int]:
    name_clean = intrant_name.strip()
    if not name_clean:
        raise RuntimeError("Nom intrant manquant.")

    selected_set = {str(site_id).strip() for site_id in selected_site_ids if str(site_id).strip()}
    if not selected_set:
        raise RuntimeError("Sélectionnez au moins une usine.")

    existing_rows = (
        client.table("referentiel_ingredients")
        .select("site_id, name")
        .eq("name", name_clean)
        .execute()
        .data
        or []
    )
    existing_site_ids = {str(row.get("site_id", "")).strip() for row in existing_rows if str(row.get("site_id", "")).strip()}

    payload_values = {
        "name": name_clean,
        "ms_pct": round(to_float(ms_pct, 0.0), 3),
        "mo_pct": round(to_float(mo_pct, 0.0), 3),
        "bmp_nm3_t": round(to_float(bmp_nm3_t, 0.0), 3),
        "masse_volumique_t_m3": round(to_float(masse_volumique_t_m3, 0.0), 3),
    }

    inserted_count = 0
    updated_count = 0
    deleted_count = 0

    for site_id in selected_set:
        if site_id in existing_site_ids:
            (
                client.table("referentiel_ingredients")
                .update(payload_values)
                .eq("site_id", site_id)
                .eq("name", name_clean)
                .execute()
            )
            updated_count += 1
        else:
            insert_row = {"site_id": site_id, **payload_values}
            client.table("referentiel_ingredients").insert([insert_row]).execute()
            inserted_count += 1

    if remove_unselected_links:
        to_remove = existing_site_ids - selected_set
        for site_id in to_remove:
            (
                client.table("referentiel_ingredients")
                .delete()
                .eq("site_id", site_id)
                .eq("name", name_clean)
                .execute()
            )
            deleted_count += 1

    return inserted_count, updated_count, deleted_count


def normalize_date_value(value: object) -> str:
    if value is None:
        return ""

    text = str(value).strip()
    if not text:
        return ""

    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]

    return text


def format_fr_date(date_value: object) -> str:
    text = normalize_date_value(date_value)
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        return f"{text[8:10]}/{text[5:7]}/{text[0:4]}"
    return text


def format_fr_number(value: object, decimals: int = 3) -> str:
    number = to_float(value, 0.0)
    formatted = f"{number:,.{decimals}f}"
    return formatted.replace(",", " ").replace(".", ",")


def load_fiche(client: Client, site_id: str, reacteur: str | None = None, date_str: str | None = None) -> list[dict]:
    columns = (
        "date, reacteur, ingredient, tonnage_prevu, "
        "ms_pct, mo_pct, bmp_nm3_t, masse_volumique_t_m3, "
        "tonnage_ms_t_prevu, potentiel_nm3_prevu, volume_m3_prevu, "
        "total_ms_t_prevu, total_potentiel_nm3_prevu, total_volume_m3_prevu"
    )
    query = client.table(TBL_FICHE).select(columns)
    if site_id:
        query = query.eq("site_id", site_id)
    if reacteur:
        query = query.eq("reacteur", reacteur)
    if date_str:
        query = query.eq("date", date_str)
    try:
        response = query.execute()
    except Exception:
        fallback_query = client.table(TBL_FICHE).select("date, reacteur, ingredient, tonnage_prevu")
        if site_id:
            fallback_query = fallback_query.eq("site_id", site_id)
        if reacteur:
            fallback_query = fallback_query.eq("reacteur", reacteur)
        if date_str:
            fallback_query = fallback_query.eq("date", date_str)
        response = fallback_query.execute()

    rows = response.data or []
    cleaned = []
    for row in rows:
        ingredient = str(row.get("ingredient", "")).strip()
        reactor = str(row.get("reacteur", "")).strip()
        date_value = normalize_date_value(row.get("date"))
        tonnage = to_float(row.get("tonnage_prevu"), 0.0)
        if ingredient and reactor and date_value:
            cleaned.append(
                {
                    "date": date_value,
                    "reacteur": reactor,
                    "ingredient": ingredient,
                    "tonnage_prevu": round(tonnage, 3),
                    "ms_pct": round(to_float(row.get("ms_pct"), 0.0), 3),
                    "mo_pct": round(to_float(row.get("mo_pct"), 0.0), 3),
                    "bmp_nm3_t": round(to_float(row.get("bmp_nm3_t"), 0.0), 3),
                    "masse_volumique_t_m3": round(to_float(row.get("masse_volumique_t_m3"), 0.0), 3),
                    "tonnage_ms_t_prevu": round(to_float(row.get("tonnage_ms_t_prevu"), 0.0), 3),
                    "potentiel_nm3_prevu": round(to_float(row.get("potentiel_nm3_prevu"), 0.0), 3),
                    "volume_m3_prevu": round(to_float(row.get("volume_m3_prevu"), 0.0), 3),
                    "total_ms_t_prevu": round(to_float(row.get("total_ms_t_prevu"), 0.0), 3),
                    "total_potentiel_nm3_prevu": round(to_float(row.get("total_potentiel_nm3_prevu"), 0.0), 3),
                    "total_volume_m3_prevu": round(to_float(row.get("total_volume_m3_prevu"), 0.0), 3),
                }
            )
    return cleaned


def load_ration_history(client: Client, site_id: str) -> tuple[list[dict], dict[str, list[dict]]]:
    try:
        query = client.table(TBL_SAISIES).select(
            "date, reacteur, batch_code, batch_id, ingredient, tonnage_reel, ms_pct, mo_pct, bmp_nm3_t, masse_volumique_t_m3, "
            "total_potentiel_nm3_reel, total_volume_m3_reel"
        )
        if site_id:
            query = query.eq("site_id", site_id)
        response = query.order("date", desc=True).execute()
    except Exception:
        fallback_query = client.table(TBL_SAISIES).select(
            "date, reacteur, batch_id, ingredient, tonnage_reel, ms_pct, mo_pct, bmp_nm3_t, masse_volumique_t_m3"
        )
        if site_id:
            fallback_query = fallback_query.eq("site_id", site_id)
        response = fallback_query.order("date", desc=True).execute()

    rows = response.data or []
    grouped: dict[str, dict] = {}

    for row in rows:
        date_value = normalize_date_value(row.get("date"))
        reacteur = str(row.get("reacteur", "")).strip()
        batch_code = str(row.get("batch_code", "")).strip()
        batch_id = str(row.get("batch_id", "")).strip()
        batch_ref = batch_code or batch_id or f"{date_value}_{reacteur}"
        key = f"{date_value}|{reacteur}|{batch_ref}"

        if key not in grouped:
            grouped[key] = {
                "Cuve": reacteur,
                "Date": date_value,
                "_batch_ref": batch_ref,
                "_key": key,
                "Tonnage (t)": 0.0,
                "Potentiel (Nm3)": 0.0,
                "Volume (m3)": 0.0,
                "_composition": [],
            }

        tonnage_reel = to_float(row.get("tonnage_reel"), 0.0)
        ms_pct = to_float(row.get("ms_pct"), 0.0)
        mo_pct = to_float(row.get("mo_pct"), 0.0)
        bmp_nm3_t = to_float(row.get("bmp_nm3_t"), 0.0)
        masse_vol = to_float(row.get("masse_volumique_t_m3"), 0.0)
        ingredient_name = str(row.get("ingredient", "")).strip()

        intrant_kpi = compute_kpis(
            tonnage=tonnage_reel,
            ms_pct=ms_pct,
            mo_pct=mo_pct,
            bmp_nm3_t=bmp_nm3_t,
            masse_volumique_t_m3=masse_vol,
        )

        grouped[key]["_composition"].append(
            {
                "Ingrédient": ingredient_name,
                "Tonnage (t)": round(tonnage_reel, 3),
                "MS (%)": round(ms_pct, 3),
                "MO (%)": round(mo_pct, 3),
                "BMP (Nm3/t)": round(bmp_nm3_t, 3),
                "Volume intrant (m3)": intrant_kpi["volume_m3"],
                "Potentiel méthane intrant (Nm3)": intrant_kpi["potentiel_nm3"],
            }
        )

        grouped[key]["Tonnage (t)"] += tonnage_reel

        total_potentiel = to_float(row.get("total_potentiel_nm3_reel"), -1.0)
        total_volume = to_float(row.get("total_volume_m3_reel"), -1.0)

        if total_potentiel >= 0 and total_volume >= 0:
            grouped[key]["Potentiel (Nm3)"] = max(grouped[key]["Potentiel (Nm3)"], total_potentiel)
            grouped[key]["Volume (m3)"] = max(grouped[key]["Volume (m3)"], total_volume)
        else:
            grouped[key]["Potentiel (Nm3)"] += intrant_kpi["potentiel_nm3"]
            grouped[key]["Volume (m3)"] += intrant_kpi["volume_m3"]

    history = []
    composition_by_key: dict[str, list[dict]] = {}
    for value in grouped.values():
        composition_rows = value["_composition"]
        composition_rows.sort(key=lambda item: item["Ingrédient"])

        total_line = {
            "Ingrédient": "TOTAL",
            "Tonnage (t)": round(sum(to_float(r.get("Tonnage (t)"), 0.0) for r in composition_rows), 3),
            "MS (%)": "",
            "MO (%)": "",
            "BMP (Nm3/t)": "",
            "Volume intrant (m3)": round(sum(to_float(r.get("Volume intrant (m3)"), 0.0) for r in composition_rows), 3),
            "Potentiel méthane intrant (Nm3)": round(
                sum(to_float(r.get("Potentiel méthane intrant (Nm3)"), 0.0) for r in composition_rows), 3
            ),
        }
        composition_by_key[value["_key"]] = composition_rows + [total_line]

        history.append(
            {
                "_key": value["_key"],
                "Cuve": value["Cuve"],
                "Date": value["Date"],
                "Potentiel (Nm3)": round(to_float(value["Potentiel (Nm3)"]), 3),
                "Tonnage (t)": round(to_float(value["Tonnage (t)"]), 3),
                "Volume (m3)": round(to_float(value["Volume (m3)"]), 3),
            }
        )

    history.sort(key=lambda item: (item["Date"], item["Cuve"]), reverse=True)
    return history, composition_by_key


def history_tab(client: Client, site_id: str) -> None:
    st.subheader("Historique du suivi des rations")
    render_help_for_screen("ration_historique")
    try:
        history_rows, composition_by_key = load_ration_history(client, site_id)
    except Exception:
        st.error("Impossible de charger l'historique des rations depuis Supabase.")
        return

    if not history_rows:
        st.info("Aucun historique disponible pour le moment.")
        return

    display_history_rows = []
    for row in history_rows:
        display_history_rows.append(
            {
                "Cuve": row["Cuve"],
                "Date": format_fr_date(row["Date"]),
                "Potentiel (Nm3)": format_fr_number(row["Potentiel (Nm3)"], 3),
                "Tonnage (t)": format_fr_number(row["Tonnage (t)"], 3),
                "Volume (m3)": format_fr_number(row["Volume (m3)"], 3),
            }
        )
    history_df = pd.DataFrame(display_history_rows)

    if "history_selected_key" not in st.session_state:
        st.session_state.history_selected_key = None

    selection_event = st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    selected_rows = selection_event.selection.rows if selection_event and selection_event.selection else []
    if selected_rows:
        selected_index = int(selected_rows[0])
        if 0 <= selected_index < len(history_rows):
            st.session_state.history_selected_key = history_rows[selected_index]["_key"]

    selected_key = st.session_state.history_selected_key
    if not selected_key:
        st.info("Cliquez sur une ligne de l'historique pour afficher la composition détaillée.")
        return

    composition_rows = composition_by_key.get(selected_key, [])
    if not composition_rows:
        st.info("Aucune composition disponible pour cette ration.")
        return

    display_composition_rows = []
    for row in composition_rows:
        display_composition_rows.append(
            {
                "Ingrédient": row["Ingrédient"],
                "Tonnage (t)": format_fr_number(row.get("Tonnage (t)", 0.0), 3),
                "MS (%)": format_fr_number(row.get("MS (%)", 0.0), 3) if row.get("MS (%)", "") != "" else "",
                "MO (%)": format_fr_number(row.get("MO (%)", 0.0), 3) if row.get("MO (%)", "") != "" else "",
                "BMP (Nm3/t)": format_fr_number(row.get("BMP (Nm3/t)", 0.0), 3)
                if row.get("BMP (Nm3/t)", "") != ""
                else "",
                "Volume intrant (m3)": format_fr_number(row.get("Volume intrant (m3)", 0.0), 3),
                "Potentiel méthane intrant (Nm3)": format_fr_number(
                    row.get("Potentiel méthane intrant (Nm3)", 0.0), 3
                ),
            }
        )

    st.markdown("### Composition par ingrédient")
    st.dataframe(pd.DataFrame(display_composition_rows), use_container_width=True, hide_index=True)


def load_stock_consumption(
    client: Client,
    site_id: str,
    start_date_iso: str,
    end_date_iso: str,
) -> list[dict]:
    query = client.table(TBL_SAISIES).select("date, ingredient, tonnage_reel")
    if site_id:
        query = query.eq("site_id", site_id)
    if start_date_iso:
        query = query.gte("date", start_date_iso)
    if end_date_iso:
        query = query.lte("date", end_date_iso)

    response = query.execute()
    rows = response.data or []

    cleaned: list[dict] = []
    for row in rows:
        ingredient = str(row.get("ingredient", "")).strip()
        date_value = normalize_date_value(row.get("date"))
        tonnage = to_float(row.get("tonnage_reel"), 0.0)
        if ingredient and date_value and tonnage > 0:
            cleaned.append(
                {
                    "date": date_value,
                    "ingredient": ingredient,
                    "tonnage_reel": round(tonnage, 3),
                }
            )
    return cleaned


def stock_tab(client: Client, site_id: str) -> None:
    st.subheader("Stock - Consommations")

    today = date.today()
    default_start = today - timedelta(days=30)

    c1, c2 = st.columns(2)
    start_date = c1.date_input("Période du", value=default_start, key="stock_start_date")
    end_date = c2.date_input("au", value=today, key="stock_end_date")

    if start_date > end_date:
        st.error("La date de début doit être antérieure ou égale à la date de fin.")
        render_help_for_screen("entrees_sorties_stock")
        return

    try:
        rows = load_stock_consumption(
            client,
            site_id=site_id,
            start_date_iso=start_date.isoformat(),
            end_date_iso=end_date.isoformat(),
        )
    except Exception as error:
        st.error(f"Impossible de charger les consommations stock depuis Supabase: {error}")
        render_help_for_screen("entrees_sorties_stock")
        return

    if not rows:
        st.info("Aucune consommation disponible sur la période sélectionnée.")
        render_help_for_screen("entrees_sorties_stock")
        return

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["date"].notna()]
    if df.empty:
        st.info("Aucune consommation exploitable sur la période sélectionnée.")
        render_help_for_screen("entrees_sorties_stock")
        return

    agg_df = (
        df.groupby("ingredient", as_index=False)
        .agg(
            quantite_consommee_t=("tonnage_reel", "sum"),
            nb_saisies=("tonnage_reel", "count"),
            nb_jours=("date", "nunique"),
            derniere_consommation=("date", "max"),
        )
        .sort_values("quantite_consommee_t", ascending=False)
        .reset_index(drop=True)
    )

    total_t = float(agg_df["quantite_consommee_t"].sum())
    m1, m2, m3 = st.columns(3)
    m1.metric("Quantité consommée (t)", format_fr_number(total_t, 3))
    m2.metric("Ingrédients consommés", str(int(agg_df["ingredient"].nunique())))
    m3.metric("Lignes de saisie", str(int(df.shape[0])))

    display_df = agg_df.copy()
    display_df["quantite_consommee_t"] = display_df["quantite_consommee_t"].apply(
        lambda value: format_fr_number(value, 3)
    )
    display_df["derniere_consommation"] = display_df["derniere_consommation"].dt.strftime("%d/%m/%Y")
    display_df = display_df.rename(
        columns={
            "ingredient": "Ingrédient",
            "quantite_consommee_t": "Quantité consommée (t)",
            "nb_saisies": "Nb saisies",
            "nb_jours": "Nb jours",
            "derniere_consommation": "Dernière consommation",
        }
    )

    st.markdown("### Sorties calculées depuis les fiches rations")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    render_help_for_screen("entrees_sorties_stock")


def load_entrees_sorties_register(
    client: Client,
    table_name: str,
    quantity_column: str,
    site_id: str,
    start_date_iso: str,
    end_date_iso: str,
) -> list[dict]:
    query = client.table(table_name).select(f"date, reacteur, ingredient, {quantity_column}")
    if site_id:
        query = query.eq("site_id", site_id)
    if start_date_iso:
        query = query.gte("date", start_date_iso)
    if end_date_iso:
        query = query.lte("date", end_date_iso)
    response = query.execute()
    rows = response.data or []

    cleaned: list[dict] = []
    for row in rows:
        date_value = normalize_date_value(row.get("date"))
        ingredient = str(row.get("ingredient", "")).strip()
        reacteur = str(row.get("reacteur", "")).strip()
        quantite = to_float(row.get(quantity_column), 0.0)
        if date_value and ingredient and quantite > 0:
            cleaned.append(
                {
                    "date": date_value,
                    "reacteur": reacteur,
                    "ingredient": ingredient,
                    "quantite_t": round(quantite, 3),
                }
            )
    cleaned.sort(key=lambda item: (item["date"], item["reacteur"], item["ingredient"]), reverse=True)
    return cleaned


def load_registre_entrees_rows(
    client: Client,
    site_id: str,
    start_date_iso: str,
    end_date_iso: str,
) -> list[dict]:
    query = client.table(TBL_REGISTRE_ENTREES).select(
        "date, code, dechet, designation, forme, qtt_mb, ms_pct, qt_ms, nom_expediteur, adresse_expediteur, ingredient"
    )
    if site_id:
        query = query.eq("site_id", site_id)
    if start_date_iso:
        query = query.gte("date", start_date_iso)
    if end_date_iso:
        query = query.lte("date", end_date_iso)

    rows = query.execute().data or []
    cleaned: list[dict] = []
    for row in rows:
        date_value = normalize_date_value(row.get("date"))
        qtt_mb = to_float(row.get("qtt_mb"), 0.0)
        ms_pct = to_float(row.get("ms_pct"), 0.0)
        qt_ms = to_float(row.get("qt_ms"), qtt_mb * ms_pct / 100.0)
        if not date_value:
            continue

        cleaned.append(
            {
                "Code": str(row.get("code", "")).strip(),
                "Déchet": str(row.get("dechet", "")).strip(),
                "Désignation": str(row.get("designation", "")).strip(),
                "Forme": str(row.get("forme", "")).strip(),
                "Date": date_value,
                "Qtt MB": round(qtt_mb, 3),
                "%MS": round(ms_pct, 3),
                "Qt MS": round(qt_ms, 3),
                "Nom expéditeur": str(row.get("nom_expediteur", "")).strip(),
                "Adresse expéditeur": str(row.get("adresse_expediteur", "")).strip(),
                "Ingrédient lié": str(row.get("ingredient", "")).strip(),
            }
        )

    cleaned.sort(key=lambda item: item["Date"], reverse=True)
    return cleaned


def registre_entrees_tab(client: Client, site_id: str) -> None:
    st.subheader("Registre des entrées")

    today = date.today()
    default_start = today - timedelta(days=30)
    c1, c2 = st.columns(2)
    start_date = c1.date_input("Période du", value=default_start, key="registre_entrees_start_date")
    end_date = c2.date_input("au", value=today, key="registre_entrees_end_date")

    if start_date > end_date:
        st.error("La date de début doit être antérieure ou égale à la date de fin.")
        render_help_for_screen("entrees_sorties_registre_entrees")
        return

    try:
        rows = load_registre_entrees_rows(
            client,
            site_id=site_id,
            start_date_iso=start_date.isoformat(),
            end_date_iso=end_date.isoformat(),
        )
    except Exception as error:
        st.error(f"Impossible de charger le registre des entrées: {error}")
        render_help_for_screen("entrees_sorties_registre_entrees")
        return

    if not rows:
        st.info("Aucune entrée disponible sur la période sélectionnée (table registre_entrees vide ou non alimentée).")
        render_help_for_screen("entrees_sorties_registre_entrees")
        return

    df = pd.DataFrame(rows)
    total_mb = float(df["Qtt MB"].sum())
    total_ms = float(df["Qt MS"].sum())
    m1, m2, m3 = st.columns(3)
    m1.metric("Qtt MB totale", format_fr_number(total_mb, 3))
    m2.metric("Qt MS totale", format_fr_number(total_ms, 3))
    m3.metric("Lignes", str(int(df.shape[0])))

    display_df = df.copy()
    display_df["Date"] = pd.to_datetime(display_df["Date"], errors="coerce").dt.strftime("%d/%m/%Y")
    for col in ["Qtt MB", "%MS", "Qt MS"]:
        display_df[col] = display_df[col].apply(lambda value: format_fr_number(value, 3))
    display_df = display_df[
        [
            "Code",
            "Déchet",
            "Désignation",
            "Forme",
            "Date",
            "Qtt MB",
            "%MS",
            "Qt MS",
            "Nom expéditeur",
            "Adresse expéditeur",
        ]
    ]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    render_help_for_screen("entrees_sorties_registre_entrees")


def registre_sorties_tab(client: Client, site_id: str) -> None:
    st.subheader("Registre des sorties")

    today = date.today()
    default_start = today - timedelta(days=30)
    c1, c2 = st.columns(2)
    start_date = c1.date_input("Période du", value=default_start, key="registre_sorties_start_date")
    end_date = c2.date_input("au", value=today, key="registre_sorties_end_date")

    if start_date > end_date:
        st.error("La date de début doit être antérieure ou égale à la date de fin.")
        render_help_for_screen("entrees_sorties_registre_sorties")
        return

    try:
        rows = load_entrees_sorties_register(
            client,
            table_name=TBL_SAISIES,
            quantity_column="tonnage_reel",
            site_id=site_id,
            start_date_iso=start_date.isoformat(),
            end_date_iso=end_date.isoformat(),
        )
    except Exception as error:
        st.error(f"Impossible de charger le registre des sorties: {error}")
        render_help_for_screen("entrees_sorties_registre_sorties")
        return

    if not rows:
        st.info("Aucune sortie disponible sur la période sélectionnée.")
        render_help_for_screen("entrees_sorties_registre_sorties")
        return

    df = pd.DataFrame(rows)
    total_t = float(df["quantite_t"].sum())
    m1, m2, m3 = st.columns(3)
    m1.metric("Quantité totale (t)", format_fr_number(total_t, 3))
    m2.metric("Lignes", str(int(df.shape[0])))
    m3.metric("Ingrédients", str(int(df["ingredient"].nunique())))

    display_df = df.copy()
    display_df["date"] = pd.to_datetime(display_df["date"], errors="coerce").dt.strftime("%d/%m/%Y")
    display_df["quantite_t"] = display_df["quantite_t"].apply(lambda value: format_fr_number(value, 3))
    display_df = display_df.rename(
        columns={
            "date": "Date",
            "reacteur": "Cuve",
            "ingredient": "Ingrédient",
            "quantite_t": "Quantité réelle (t)",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    render_help_for_screen("entrees_sorties_registre_sorties")


def save_ration(client: Client, site_id: str, date_str: str, reacteur: str, lines: list[dict]) -> None:
    site_id_clean = str(site_id or "").strip()
    if not site_id_clean:
        raise RuntimeError("Publication impossible: site_id manquant pour la ration.")

    try:
        site_check = client.table("app_sites").select("id").eq("id", site_id_clean).limit(1).execute()
        if not (site_check.data or []):
            raise RuntimeError(
                f"Publication impossible: le site_id '{site_id_clean}' n'existe pas dans app_sites."
            )
    except RuntimeError:
        raise
    except Exception as error:
        raise RuntimeError(f"Vérification site impossible avant publication ration: {error}") from error

    totals = aggregate_kpis(lines, "tonnage_prevu")
    delete_query = client.table(TBL_FICHE).delete().eq("date", date_str).eq("reacteur", reacteur).eq("site_id", site_id_clean)
    delete_query.execute()
    payload = []
    for line in lines:
        tonnage_prevu = round(to_float(line.get("tonnage_prevu"), 0.0), 3)
        ms_pct = round(to_float(line.get("ms_pct"), 0.0), 3)
        mo_pct = round(to_float(line.get("mo_pct"), 0.0), 3)
        bmp_nm3_t = round(to_float(line.get("bmp_nm3_t"), 0.0), 3)
        masse_volumique_t_m3 = round(to_float(line.get("masse_volumique_t_m3"), 0.0), 3)
        kpi = compute_kpis(tonnage_prevu, ms_pct, mo_pct, bmp_nm3_t, masse_volumique_t_m3)
        payload.append(
            {
                "date": date_str,
                "site_id": site_id_clean,
                "reacteur": reacteur,
                "ingredient": line["ingredient"],
                "tonnage_prevu": tonnage_prevu,
                "ms_pct": ms_pct,
                "mo_pct": mo_pct,
                "bmp_nm3_t": bmp_nm3_t,
                "masse_volumique_t_m3": masse_volumique_t_m3,
                "tonnage_ms_t_prevu": kpi["tonnage_ms_t"],
                "potentiel_nm3_prevu": kpi["potentiel_nm3"],
                "volume_m3_prevu": kpi["volume_m3"],
                "total_ms_t_prevu": totals["total_ms_t"],
                "total_potentiel_nm3_prevu": totals["total_potentiel_nm3"],
                "total_volume_m3_prevu": totals["total_volume_m3"],
            }
        )
    try:
        insert_with_schema_fallback(client, TBL_FICHE, payload)
    except Exception as error:
        raise RuntimeError(
            "Échec publication ration (fiche_ration). "
            "Vérifiez la liaison site_id de l'utilisateur et la ligne correspondante dans app_sites. "
            f"Détail: {error}"
        ) from error


def save_batch(client: Client, site_id: str, date_str: str, reacteur: str, records: list[dict]) -> str:
    batch_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"
    totals = aggregate_kpis(records, "tonnage_reel")
    payload = []
    for record in records:
        tonnage_reel = round(to_float(record.get("tonnage_reel"), 0.0), 3)
        ms_pct = round(to_float(record.get("ms_pct"), 0.0), 3)
        mo_pct = round(to_float(record.get("mo_pct"), 0.0), 3)
        bmp_nm3_t = round(to_float(record.get("bmp_nm3_t"), 0.0), 3)
        masse_volumique_t_m3 = round(to_float(record.get("masse_volumique_t_m3"), 0.0), 3)
        kpi = compute_kpis(tonnage_reel, ms_pct, mo_pct, bmp_nm3_t, masse_volumique_t_m3)

        payload.append(
            {
                "batch_id": batch_id,
                "batch_code": batch_id,
                "site_id": site_id,
                "date": date_str,
                "reacteur": reacteur,
                "ingredient": record["ingredient"],
                "tonnage_reel": tonnage_reel,
                "ecart": round(to_float(record.get("ecart"), 0.0), 3),
                "ms_pct": ms_pct,
                "mo_pct": mo_pct,
                "bmp_nm3_t": bmp_nm3_t,
                "masse_volumique_t_m3": masse_volumique_t_m3,
                "tonnage_ms_t_reel": kpi["tonnage_ms_t"],
                "potentiel_nm3_reel": kpi["potentiel_nm3"],
                "volume_m3_reel": kpi["volume_m3"],
                "total_ms_t_reel": totals["total_ms_t"],
                "total_potentiel_nm3_reel": totals["total_potentiel_nm3"],
                "total_volume_m3_reel": totals["total_volume_m3"],
            }
        )

    try:
        insert_with_schema_fallback(client, TBL_SAISIES, payload)
    except Exception as error:
        raise RuntimeError(
            "Échec de l'enregistrement du lot (schema/politiques Supabase). "
            f"Détail: {error}"
        ) from error

    return batch_id


def purge_ration(client: Client, site_id: str, date_str: str, reacteur: str) -> None:
    query = client.table(TBL_FICHE).delete().eq("date", date_str).eq("reacteur", reacteur)
    if site_id:
        query = query.eq("site_id", site_id)
    query.execute()


def init_session(ingredients: list[str]) -> None:
    if "admin_ration_rows" not in st.session_state:
        st.session_state.admin_ration_rows = [{"ingredient": ingredients[0], "tonnage_prevu": 0.0}]


def init_navigation_session() -> None:
    if "active_module" not in st.session_state:
        st.session_state.active_module = "HOME"


def go_home() -> None:
    st.session_state.active_module = "HOME"


def open_module(module_name: str) -> None:
    st.session_state.active_module = module_name


HELP_BY_SCREEN: dict[str, dict[str, object]] = {
    "connexion": {
        "title": "Connexion",
        "items": [
            "Renseignez votre email et votre mot de passe, puis cliquez sur Se connecter.",
            "L'option Se souvenir de moi garde la session sur ce navigateur.",
            "Si la connexion échoue, vérifiez vos identifiants puis contactez un administrateur.",
        ],
    },
    "accueil": {
        "title": "Accueil",
        "items": [
            "Choisissez le site en haut de l'écran puis cliquez sur un module.",
            "Les modules visibles dépendent de vos droits pour le site sélectionné.",
            "Utilisez Déconnexion en haut à droite pour fermer la session.",
        ],
    },
    "ration_admin": {
        "title": "Ration - Préparation",
        "items": [
            "Sélectionnez la date et le réacteur, puis saisissez les ingrédients prévus.",
            "Chaque ingrédient ne doit apparaître qu'une seule fois dans la ration.",
            "Publier la Ration enregistre la fiche dans la base pour la saisie opérateur.",
        ],
    },
    "ration_operateur": {
        "title": "Ration - Saisie opérateur",
        "items": [
            "Chargez la ration active du réacteur puis saisissez les tonnages réels.",
            "Ajoutez des ingrédients imprévus si nécessaire.",
            "Finaliser le Lot enregistre le batch et purge la ration planifiée du créneau.",
        ],
    },
    "ration_historique": {
        "title": "Ration - Historique",
        "items": [
            "Cliquez sur une ligne pour afficher la composition détaillée du lot.",
            "Les indicateurs affichent tonnage, potentiel et volume enregistrés.",
            "Utilisez ce tableau pour contrôle qualité et traçabilité.",
        ],
    },
    "entrees_sorties_stock": {
        "title": "Entrées/Sorties - Stock",
        "items": [
            "Les sorties sont calculées automatiquement à partir des lots saisis.",
            "Filtrez la période pour suivre les quantités consommées par ingrédient.",
            "Le tableau agrège tonnage total, nombre de saisies et dernière consommation.",
        ],
    },
    "entrees_sorties_registre_entrees": {
        "title": "Entrées/Sorties - Registre des entrées",
        "items": [
            "Ce registre affiche les intrants planifiés (fiche ration) sur la période.",
            "Utilisez-le pour contrôler les quantités prévues par cuve et ingrédient.",
        ],
    },
    "entrees_sorties_registre_sorties": {
        "title": "Entrées/Sorties - Registre des sorties",
        "items": [
            "Ce registre affiche les sorties réellement saisies (saisies production).",
            "Utilisez-le pour tracer les quantités consommées par date, cuve et intrant.",
        ],
    },
    "maintenance": {
        "title": "Maintenance",
        "items": [
            "La synchronisation horaire récupère les données de fonctionnement depuis Natisoft.",
            "Utilisez Forcer la synchronisation maintenant pour un rafraîchissement immédiat.",
            "La synthèse historique calcule les temps de fonctionnement par équipement.",
        ],
    },
    "securite": {
        "title": "Sécurité",
        "items": [
            "Ce module suit le fonctionnement torchère sur la période configurée.",
            "Le graphique mensuel permet d'ouvrir le détail journalier par clic.",
            "Utilisez la synchro forcée si vous devez mettre à jour les données immédiatement.",
        ],
    },
    "energie": {
        "title": "Énergie",
        "items": [
            "Le sous-menu Production biométhane est affiché en premier.",
            "Le sous-menu Consommation électrique affiche process et épuration journalières et mensuelles.",
            "En cas d'écart, lancez d'abord la synchro forcée puis contrôlez le détail journalier.",
        ],
    },
    "administration": {
        "title": "Administration",
        "items": [
            "L'onglet Sites gère les usines et les paramètres Natisoft.",
            "L'onglet Utilisateurs gère comptes, rôles et affectations par site.",
            "L'onglet Droits définit la visibilité des menus et sous-menus par rôle.",
        ],
    },
    "construction": {
        "title": "Module en construction",
        "items": [
            "Ce module n'est pas encore finalisé.",
            "Revenez au menu pour utiliser les modules disponibles.",
        ],
    },
}


def render_help_for_screen(screen_key: str) -> None:
    help_content = HELP_BY_SCREEN.get(screen_key, HELP_BY_SCREEN["accueil"])
    title = str(help_content.get("title", "Aide"))
    items = help_content.get("items", [])

    with st.expander(f"❓ Aide - {title}", expanded=False):
        if isinstance(items, list):
            for item in items:
                st.markdown(f"- {str(item)}")
        st.caption("Besoin d'assistance: contactez votre administrateur de site.")


def home_screen(
    allowed_modules: list[str],
    show_admin_button: bool,
    client: Client,
    site_roles_map: dict[str, list[str]],
    site_by_id: dict[str, dict],
) -> None:
    st.markdown(
        """
        <div style="
            margin: 0 0 0.8rem 0;
            padding: 0.8rem 0.95rem;
            border-radius: 14px;
            border: 1px solid #E4DDED;
            background: linear-gradient(135deg, rgba(143, 90, 168, 0.14) 0%, rgba(255,255,255,0.95) 68%);
            color: #6F3F86;
            font-weight: 700;
        ">
            Tableau de bord usines • Sélectionnez un module
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_home_biomethane_injection_indicators(client, site_roles_map, site_by_id)

    st.markdown(
        """
        <style>
        div.stButton > button {
            min-height: 56px;
            font-size: 0.96rem;
            font-weight: 600;
            width: 100%;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(111, 63, 134, 0.08);
            background: #FFFFFF;
            border: 1px solid #E4DDED;
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 20px rgba(111, 63, 134, 0.14);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    module_order = [m for m in MODULES if m in allowed_modules]
    if not module_order:
        st.info("Aucun module accessible pour votre profil sur ce site.")
        return

    for idx in range(0, len(module_order), 2):
        cols = st.columns(2)
        left_label = module_order[idx]
        if cols[0].button(left_label, use_container_width=True, key=f"home_{left_label}"):
            open_module(left_label)
            st.rerun()

        if idx + 1 < len(module_order):
            right_label = module_order[idx + 1]
            if cols[1].button(right_label, use_container_width=True, key=f"home_{right_label}"):
                open_module(right_label)
                st.rerun()

    if show_admin_button:
        st.markdown("---")
        if st.button("Administration", use_container_width=True):
            open_module("Administration")
            st.rerun()

    render_help_for_screen("accueil")


def render_home_biomethane_injection_indicators(
    client: Client,
    site_roles_map: dict[str, list[str]],
    site_by_id: dict[str, dict],
) -> None:
    today = datetime.now().date()
    last_10_start = today - timedelta(days=9)
    prev_10_end = last_10_start - timedelta(days=1)
    prev_10_start = prev_10_end - timedelta(days=9)

    indicator_rows: list[dict] = []
    for site_id, roles in site_roles_map.items():
        if site_id not in site_by_id:
            continue

        site_rights = load_role_menu_rights(client, roles)
        if not has_permission(roles, site_rights, "energie", ""):
            continue

        site_row = site_by_id[site_id]
        site_code = str(site_row.get("code", "")).strip()
        site_name = str(site_row.get("name", "")).strip()

        workspace_id = get_workspace_for_site(site_id, site_code, site_name)
        group_id = get_energie_group_for_site(site_id, site_code, site_name)
        group_id, _ = resolve_energie_group_for_workspace(workspace_id, group_id)

        history_df = load_energie_history_from_supabase_any_model(
            client,
            site_id=site_id,
            workspace_id=workspace_id,
            group_id=group_id,
            consommation_type="biomethane",
        )
        if history_df.empty:
            history_df, _ = load_energie_cache(site_id, "biomethane")

        daily_df = build_energie_daily_consumption(history_df, "biomethane", site_id=site_id)
        if daily_df.empty:
            continue

        avg_last_10 = average_flow_on_period(daily_df, last_10_start, today)
        avg_prev_10 = average_flow_on_period(daily_df, prev_10_start, prev_10_end)
        indicator_rows.append(
            {
                "label": f"{site_name} ({site_code})" if site_code else site_name,
                "value": avg_last_10 / 24.0,
                "delta": _format_pct_delta(avg_last_10, avg_prev_10),
            }
        )

    if not indicator_rows:
        return

    st.markdown("#### Injection biométhane · moyenne 10 jours")
    cols = st.columns(min(3, len(indicator_rows)))
    for idx, row in enumerate(indicator_rows):
        with cols[idx % len(cols)]:
            st.metric(str(row["label"]), f"{float(row['value']):.2f} Nm3/h", str(row["delta"]))


def under_construction_screen(module_name: str) -> None:
    st.subheader(module_name)
    render_help_for_screen("construction")
    st.info("Application en construction")


def admin_module(client: Client, selected_site_id: str, selected_roles: list[str], rights: set[tuple[str, str]]) -> None:
    render_help_for_screen("administration")

    if not has_permission(selected_roles, rights, "administration", ""):
        st.error("Accès refusé au module Administration.")
        return

    admin_db_client = client
    try:
        admin_db_client = get_supabase_admin_client()
    except Exception:
        st.warning(
            "SUPABASE_SERVICE_ROLE_KEY absent/invalide: certaines opérations d'administration peuvent échouer avec les politiques RLS."
        )

    st.subheader("Administration")
    admin_tabs = st.tabs(["Sites", "Utilisateurs", "Droits"])

    with admin_tabs[0]:
        if not has_permission(selected_roles, rights, "administration", "sites"):
            st.info("Vous n'avez pas le droit de gérer les sites.")
        else:
            try:
                all_sites = load_sites(admin_db_client)
            except Exception:
                st.error("Impossible de charger les sites.")
                all_sites = []

            st.markdown("### Sites existants")
            if all_sites:
                st.dataframe(pd.DataFrame(all_sites), use_container_width=True, hide_index=True)
            else:
                st.info("Aucun site configuré.")

            st.markdown("### Ajouter / modifier un site")
            site_code = st.text_input("Code site", key="admin_site_code")
            site_name = st.text_input("Nom site", key="admin_site_name")
            if st.button("Enregistrer le site", key="admin_save_site", use_container_width=True):
                if not site_code.strip() or not site_name.strip():
                    st.error("Code et nom site sont obligatoires.")
                else:
                    payload = [{"code": site_code.strip(), "name": site_name.strip()}]
                    try:
                        admin_db_client.table("app_sites").upsert(payload).execute()
                        st.success("Site enregistré.")
                    except Exception as error:
                        st.error(f"Erreur enregistrement site: {error}")

            st.markdown("### Paramétrage Workspace Natisoft par usine")
            workspace_mapping = load_maintenance_workspace_mapping()
            workspace_inputs: dict[str, str] = {}
            for site in all_sites:
                site_id = str(site.get("id", "")).strip()
                site_code = str(site.get("code", "")).strip()
                site_name = str(site.get("name", "")).strip()
                if not site_id:
                    continue

                default_ws = workspace_mapping.get(site_id, "") or default_workspace_for_site(site_code, site_name)
                label = f"Workspace pour {site_name} ({site_code})"
                workspace_inputs[site_id] = st.text_input(
                    label,
                    value=str(default_ws).strip(),
                    key=f"admin_workspace_map_{site_id}",
                    placeholder="Ex: 10 ou 41",
                )

            if st.button("Enregistrer les workspaces", key="admin_save_workspaces", use_container_width=True):
                try:
                    save_maintenance_workspace_mapping(workspace_inputs)
                    st.success("Paramétrage workspaces enregistré.")
                except Exception as error:
                    st.error(f"Erreur enregistrement workspaces: {error}")

            st.markdown("### Paramétrage Groupe torchère Natisoft par usine")
            torchere_group_mapping = load_torchere_group_mapping()
            torchere_group_inputs: dict[str, str] = {}
            for site in all_sites:
                site_id = str(site.get("id", "")).strip()
                site_code = str(site.get("code", "")).strip()
                site_name = str(site.get("name", "")).strip()
                if not site_id:
                    continue

                workspace_for_site = get_workspace_for_site(site_id, site_code, site_name)
                expected_group_for_workspace = TORCHERE_WORKSPACE_GROUP_MAP.get(
                    str(workspace_for_site).strip(),
                    default_torchere_group_for_site(site_code, site_name),
                )
                default_group = torchere_group_mapping.get(site_id, expected_group_for_workspace)
                label = f"Groupe torchère pour {site_name} ({site_code})"
                torchere_group_inputs[site_id] = st.text_input(
                    label,
                    value=str(default_group).strip(),
                    key=f"admin_torchere_group_map_{site_id}",
                    placeholder="Ex: 343",
                )

            if st.button("Enregistrer les groupes torchère", key="admin_save_torchere_groups", use_container_width=True):
                try:
                    save_torchere_group_mapping(torchere_group_inputs)
                    st.success("Paramétrage groupes torchère enregistré.")
                except Exception as error:
                    st.error(f"Erreur enregistrement groupes torchère: {error}")

            st.markdown("### Paramétrage Groupe énergie Natisoft par usine")
            energie_group_mapping = load_energie_group_mapping()
            energie_group_inputs: dict[str, str] = {}
            for site in all_sites:
                site_id = str(site.get("id", "")).strip()
                site_code = str(site.get("code", "")).strip()
                site_name = str(site.get("name", "")).strip()
                if not site_id:
                    continue

                workspace_for_site = get_workspace_for_site(site_id, site_code, site_name)
                expected_group_for_workspace = ENERGIE_WORKSPACE_GROUP_MAP.get(
                    str(workspace_for_site).strip(),
                    default_energie_group_for_site(site_code, site_name),
                )
                default_group = energie_group_mapping.get(site_id, expected_group_for_workspace)
                label = f"Groupe énergie pour {site_name} ({site_code})"
                energie_group_inputs[site_id] = st.text_input(
                    label,
                    value=str(default_group).strip(),
                    key=f"admin_energie_group_map_{site_id}",
                    placeholder="Ex: 337 ou 343",
                )

            if st.button("Enregistrer les groupes énergie", key="admin_save_energie_groups", use_container_width=True):
                try:
                    save_energie_group_mapping(energie_group_inputs)
                    st.success("Paramétrage groupes énergie enregistré.")
                except Exception as error:
                    st.error(f"Erreur enregistrement groupes énergie: {error}")

            st.markdown("### Script paramétrable import Énergie (mapping colonnes)")
            energie_script_config = load_energie_import_script_config()
            default_date_idx = int(energie_script_config.get("date_column_index", ENERGIE_DATE_COLUMN_INDEX))
            default_epu_idx = int(energie_script_config.get("epuration_column_index", ENERGIE_EPURATION_COLUMN_INDEX))
            default_proc_idx = int(energie_script_config.get("process_column_index", ENERGIE_PROCESS_COLUMN_INDEX))
            default_biomethane_idx = int(energie_script_config.get("biomethane_column_index", ENERGIE_BIOMETHANE_COLUMN_INDEX))
            default_biogas_idx = int(energie_script_config.get("biogas_column_index", ENERGIE_BIOGAZ_COLUMN_INDEX))
            default_reject_torch = bool(
                energie_script_config.get("reject_torchere_columns", ENERGIE_REJECT_TORCHERE_COLUMNS)
            )

            gc1, gc2, gc3 = st.columns(3)
            global_date_idx = gc1.number_input(
                "Colonne Date (globale)",
                min_value=1,
                step=1,
                value=default_date_idx,
                key="admin_energie_script_global_date_idx",
            )
            global_epu_idx = gc2.number_input(
                "Colonne Épuration (globale)",
                min_value=1,
                step=1,
                value=default_epu_idx,
                key="admin_energie_script_global_epu_idx",
            )
            global_proc_idx = gc3.number_input(
                "Colonne Process (globale)",
                min_value=1,
                step=1,
                value=default_proc_idx,
                key="admin_energie_script_global_proc_idx",
            )
            global_biomethane_idx = st.number_input(
                "Colonne Biométhane (globale)",
                min_value=1,
                step=1,
                value=default_biomethane_idx,
                key="admin_energie_script_global_biomethane_idx",
            )
            global_biogas_idx = st.number_input(
                "Colonne Biogaz traité (globale)",
                min_value=1,
                step=1,
                value=default_biogas_idx,
                key="admin_energie_script_global_biogas_idx",
            )
            gm1, gm2, gm3 = st.columns(3)
            default_process_model = str(energie_script_config.get("process_model", ENERGIE_DEFAULT_MODELS.get("process", "energy_integrator")) or "energy_integrator").strip() or "energy_integrator"
            default_epurateur_model = str(energie_script_config.get("epurateur_model", ENERGIE_DEFAULT_MODELS.get("epurateur", "energy_integrator")) or "energy_integrator").strip() or "energy_integrator"
            default_biomethane_model = str(energie_script_config.get("biomethane_model", ENERGIE_DEFAULT_MODELS.get("biomethane", "volume")) or "volume").strip() or "volume"
            global_process_model = gm1.text_input(
                "Modèle Process (global)",
                value=default_process_model,
                key="admin_energie_script_global_process_model",
            ).strip()
            global_epurateur_model = gm2.text_input(
                "Modèle Épuration (global)",
                value=default_epurateur_model,
                key="admin_energie_script_global_epurateur_model",
            ).strip()
            global_biomethane_model = gm3.text_input(
                "Modèle Biométhane (global)",
                value=default_biomethane_model,
                key="admin_energie_script_global_biomethane_model",
            ).strip()
            global_reject_torch = st.checkbox(
                "Rejeter les colonnes contenant 'torchère/torch'",
                value=default_reject_torch,
                key="admin_energie_script_global_reject_torch",
            )

            existing_overrides = energie_script_config.get("site_overrides", {})
            site_overrides_inputs: dict[str, dict] = {}
            for site in all_sites:
                site_id = str(site.get("id", "")).strip()
                site_code = str(site.get("code", "")).strip()
                site_name = str(site.get("name", "")).strip()
                if not site_id:
                    continue

                override = existing_overrides.get(site_id, {}) if isinstance(existing_overrides, dict) else {}
                site_date_default = int(override.get("date_column_index", global_date_idx))
                site_epu_default = int(override.get("epuration_column_index", global_epu_idx))
                site_proc_default = int(override.get("process_column_index", global_proc_idx))
                site_biomethane_default = int(override.get("biomethane_column_index", global_biomethane_idx))
                site_biogas_default = int(override.get("biogas_column_index", override.get("process_column_index", global_biogas_idx)))
                site_process_model_default = str(override.get("process_model", global_process_model) or global_process_model).strip() or global_process_model
                site_epurateur_model_default = str(override.get("epurateur_model", global_epurateur_model) or global_epurateur_model).strip() or global_epurateur_model
                site_biomethane_model_default = str(override.get("biomethane_model", global_biomethane_model) or global_biomethane_model).strip() or global_biomethane_model
                site_reject_default = bool(override.get("reject_torchere_columns", global_reject_torch))

                st.caption(f"Override script pour {site_name} ({site_code})")
                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                site_date_idx = sc1.number_input(
                    f"Date [{site_code}]",
                    min_value=1,
                    step=1,
                    value=site_date_default,
                    key=f"admin_energie_script_site_date_idx_{site_id}",
                )
                site_epu_idx = sc2.number_input(
                    f"Épuration [{site_code}]",
                    min_value=1,
                    step=1,
                    value=site_epu_default,
                    key=f"admin_energie_script_site_epu_idx_{site_id}",
                )
                site_proc_idx = sc3.number_input(
                    f"Process [{site_code}]",
                    min_value=1,
                    step=1,
                    value=site_proc_default,
                    key=f"admin_energie_script_site_proc_idx_{site_id}",
                )
                site_biomethane_idx = sc4.number_input(
                    f"Biométhane [{site_code}]",
                    min_value=1,
                    step=1,
                    value=site_biomethane_default,
                    key=f"admin_energie_script_site_biomethane_idx_{site_id}",
                )
                site_biogas_idx = sc5.number_input(
                    f"Biogaz [{site_code}]",
                    min_value=1,
                    step=1,
                    value=site_biogas_default,
                    key=f"admin_energie_script_site_biogas_idx_{site_id}",
                )
                sm1, sm2, sm3 = st.columns(3)
                site_process_model = sm1.text_input(
                    f"Modèle Process [{site_code}]",
                    value=site_process_model_default,
                    key=f"admin_energie_script_site_process_model_{site_id}",
                ).strip()
                site_epurateur_model = sm2.text_input(
                    f"Modèle Épuration [{site_code}]",
                    value=site_epurateur_model_default,
                    key=f"admin_energie_script_site_epurateur_model_{site_id}",
                ).strip()
                site_biomethane_model = sm3.text_input(
                    f"Modèle Biométhane [{site_code}]",
                    value=site_biomethane_model_default,
                    key=f"admin_energie_script_site_biomethane_model_{site_id}",
                ).strip()
                site_reject_torch = st.checkbox(
                    f"Rejet torchère [{site_code}]",
                    value=site_reject_default,
                    key=f"admin_energie_script_site_reject_torch_{site_id}",
                )

                site_overrides_inputs[site_id] = {
                    "date_column_index": int(site_date_idx),
                    "epuration_column_index": int(site_epu_idx),
                    "process_column_index": int(site_proc_idx),
                    "biomethane_column_index": int(site_biomethane_idx),
                    "biogas_column_index": int(site_biogas_idx),
                    "process_model": str(site_process_model or global_process_model),
                    "epurateur_model": str(site_epurateur_model or global_epurateur_model),
                    "biomethane_model": str(site_biomethane_model or global_biomethane_model),
                    "reject_torchere_columns": bool(site_reject_torch),
                }

            if st.button("Enregistrer le script import Énergie", key="admin_save_energie_script_config", use_container_width=True):
                try:
                    save_energie_import_script_config(
                        {
                            "date_column_index": int(global_date_idx),
                            "epuration_column_index": int(global_epu_idx),
                            "process_column_index": int(global_proc_idx),
                            "biomethane_column_index": int(global_biomethane_idx),
                            "biogas_column_index": int(global_biogas_idx),
                            "process_model": str(global_process_model or "energy_integrator"),
                            "epurateur_model": str(global_epurateur_model or "energy_integrator"),
                            "biomethane_model": str(global_biomethane_model or "volume"),
                            "reject_torchere_columns": bool(global_reject_torch),
                            "site_overrides": site_overrides_inputs,
                        }
                    )
                    st.success("Script import Énergie enregistré.")
                except Exception as error:
                    st.error(f"Erreur enregistrement script import Énergie: {error}")

            st.markdown("### Dupliquer le référentiel d'intrants")
            if all_sites:
                source_site_options = {
                    f"{s.get('name', '')} ({s.get('code', '')})": str(s.get("id", ""))
                    for s in all_sites
                    if str(s.get("id", "")).strip()
                }
                source_site_label = st.selectbox(
                    "Usine source",
                    options=list(source_site_options.keys()),
                    key="admin_copy_source_site",
                )
                target_site_labels = st.multiselect(
                    "Usines cibles",
                    options=[label for label in source_site_options.keys() if label != source_site_label],
                    key="admin_copy_target_sites",
                )

                if st.button("Dupliquer les intrants", key="admin_copy_intrants", use_container_width=True):
                    source_site_id = source_site_options.get(source_site_label, "")
                    target_site_ids = [source_site_options[label] for label in target_site_labels if label in source_site_options]

                    if not source_site_id or not target_site_ids:
                        st.error("Sélectionnez une usine source et au moins une usine cible.")
                    else:
                        try:
                            source_rows = (
                                admin_db_client.table("referentiel_ingredients")
                                .select("name, ms_pct, mo_pct, bmp_nm3_t, masse_volumique_t_m3")
                                .eq("site_id", source_site_id)
                                .execute()
                                .data
                                or []
                            )

                            if not source_rows:
                                st.warning("Aucun intrant trouvé dans l'usine source.")
                            else:
                                inserted_total = 0
                                updated_total = 0

                                source_by_name = {}
                                for row in source_rows:
                                    name = str(row.get("name", "")).strip()
                                    if not name:
                                        continue
                                    source_by_name[name] = {
                                        "name": name,
                                        "ms_pct": to_float(row.get("ms_pct"), 0.0),
                                        "mo_pct": to_float(row.get("mo_pct"), 0.0),
                                        "bmp_nm3_t": to_float(row.get("bmp_nm3_t"), 0.0),
                                        "masse_volumique_t_m3": to_float(row.get("masse_volumique_t_m3"), 0.0),
                                    }

                                for target_site_id in target_site_ids:
                                    existing_rows = (
                                        admin_db_client.table("referentiel_ingredients")
                                        .select("name")
                                        .eq("site_id", target_site_id)
                                        .execute()
                                        .data
                                        or []
                                    )
                                    existing_names = {str(r.get("name", "")).strip() for r in existing_rows}

                                    to_insert = []
                                    to_update = []
                                    for name, source in source_by_name.items():
                                        payload = {
                                            "site_id": target_site_id,
                                            "name": source["name"],
                                            "ms_pct": source["ms_pct"],
                                            "mo_pct": source["mo_pct"],
                                            "bmp_nm3_t": source["bmp_nm3_t"],
                                            "masse_volumique_t_m3": source["masse_volumique_t_m3"],
                                        }
                                        if name in existing_names:
                                            to_update.append(payload)
                                        else:
                                            to_insert.append(payload)

                                    if to_insert:
                                        admin_db_client.table("referentiel_ingredients").insert(to_insert).execute()
                                        inserted_total += len(to_insert)

                                    for row in to_update:
                                        (
                                            admin_db_client.table("referentiel_ingredients")
                                            .update(
                                                {
                                                    "ms_pct": row["ms_pct"],
                                                    "mo_pct": row["mo_pct"],
                                                    "bmp_nm3_t": row["bmp_nm3_t"],
                                                    "masse_volumique_t_m3": row["masse_volumique_t_m3"],
                                                }
                                            )
                                            .eq("site_id", row["site_id"])
                                            .eq("name", row["name"])
                                            .execute()
                                        )
                                    updated_total += len(to_update)

                                st.success(
                                    f"Duplication terminée. Intrants insérés: {inserted_total}, intrants mis à jour: {updated_total}."
                                )
                        except Exception as error:
                            st.error(f"Erreur duplication intrants: {error}")

            st.markdown("---")
            st.markdown("### Gestion des intrants")
            try:
                intrant_rows = load_intrants_global(admin_db_client)
            except Exception as error:
                intrant_rows = []
                st.error(f"Impossible de charger les intrants: {error}")

            site_id_to_label = {
                str(site.get("id", "")).strip(): f"{site.get('name', '')} ({site.get('code', '')})"
                for site in all_sites
                if str(site.get("id", "")).strip()
            }
            site_label_to_id = {label: site_id for site_id, label in site_id_to_label.items()}

            if intrant_rows:
                grouped_intrants: dict[str, dict] = {}
                for row in intrant_rows:
                    name = str(row.get("name", "")).strip()
                    site_id = str(row.get("site_id", "")).strip()
                    if not name:
                        continue
                    if name not in grouped_intrants:
                        grouped_intrants[name] = {
                            "Intrant": name,
                            "MS (%)": round(to_float(row.get("ms_pct"), 0.0), 3),
                            "MO (%)": round(to_float(row.get("mo_pct"), 0.0), 3),
                            "BMP (Nm3/t)": round(to_float(row.get("bmp_nm3_t"), 0.0), 3),
                            "Densité (t/m3)": round(to_float(row.get("masse_volumique_t_m3"), 0.0), 3),
                            "_sites": set(),
                        }
                    if site_id:
                        grouped_intrants[name]["_sites"].add(site_id_to_label.get(site_id, site_id))

                intrants_display = []
                for value in grouped_intrants.values():
                    linked_sites = sorted(list(value["_sites"]))
                    intrants_display.append(
                        {
                            "Intrant": value["Intrant"],
                            "MS (%)": format_fr_number(value["MS (%)"], 3),
                            "MO (%)": format_fr_number(value["MO (%)"], 3),
                            "BMP (Nm3/t)": format_fr_number(value["BMP (Nm3/t)"], 3),
                            "Densité (t/m3)": format_fr_number(value["Densité (t/m3)"], 3),
                            "Nb usines": len(linked_sites),
                            "Usines liées": " | ".join(linked_sites),
                        }
                    )

                intrants_display.sort(key=lambda item: str(item.get("Intrant", "")))
                st.dataframe(pd.DataFrame(intrants_display), use_container_width=True, hide_index=True)
            else:
                st.info("Aucun intrant enregistré.")

            st.markdown("### Ajouter / modifier un intrant et ses liaisons usines")
            intrant_name_options = sorted(
                list(
                    {
                        str(row.get("name", "")).strip()
                        for row in intrant_rows
                        if str(row.get("name", "")).strip()
                    }
                )
            )
            selected_existing_intrant = st.selectbox(
                "Intrant existant (optionnel)",
                options=[""] + intrant_name_options,
                key="admin_intrant_existing_select",
            )

            prefill_rows = [
                row
                for row in intrant_rows
                if str(row.get("name", "")).strip() == selected_existing_intrant
            ]

            prefill_ms = round(to_float(prefill_rows[0].get("ms_pct"), 0.0), 3) if prefill_rows else 0.0
            prefill_mo = round(to_float(prefill_rows[0].get("mo_pct"), 0.0), 3) if prefill_rows else 0.0
            prefill_bmp = round(to_float(prefill_rows[0].get("bmp_nm3_t"), 0.0), 3) if prefill_rows else 0.0
            prefill_densite = round(to_float(prefill_rows[0].get("masse_volumique_t_m3"), 0.0), 3) if prefill_rows else 0.0

            linked_site_ids = {
                str(row.get("site_id", "")).strip()
                for row in prefill_rows
                if str(row.get("site_id", "")).strip()
            }
            linked_site_labels = [
                site_id_to_label[site_id]
                for site_id in linked_site_ids
                if site_id in site_id_to_label
            ]

            intrant_name_input = st.text_input(
                "Nom intrant",
                value=selected_existing_intrant,
                key="admin_intrant_name_input",
            )

            c1, c2 = st.columns(2)
            ms_input = c1.number_input("MS (%)", min_value=0.0, step=0.001, format="%.3f", value=prefill_ms, key="admin_intrant_ms")
            mo_input = c2.number_input("MO (%)", min_value=0.0, step=0.001, format="%.3f", value=prefill_mo, key="admin_intrant_mo")
            c3, c4 = st.columns(2)
            bmp_input = c3.number_input(
                "BMP (Nm3/t)",
                min_value=0.0,
                step=0.001,
                format="%.3f",
                value=prefill_bmp,
                key="admin_intrant_bmp",
            )
            densite_input = c4.number_input(
                "Densité (t/m3)",
                min_value=0.0,
                step=0.001,
                format="%.3f",
                value=prefill_densite,
                key="admin_intrant_densite",
            )

            selected_link_labels = st.multiselect(
                "Usines liées",
                options=list(site_label_to_id.keys()),
                default=linked_site_labels,
                key="admin_intrant_linked_sites",
            )
            remove_unselected = st.checkbox(
                "Retirer cet intrant des usines non sélectionnées",
                value=False,
                key="admin_intrant_remove_unselected",
            )

            if st.button("Enregistrer intrant / liaisons", key="admin_intrant_save", use_container_width=True):
                intrant_name_clean = intrant_name_input.strip()
                selected_site_ids = [site_label_to_id[label] for label in selected_link_labels if label in site_label_to_id]

                if not intrant_name_clean:
                    st.error("Le nom intrant est obligatoire.")
                elif not selected_site_ids:
                    st.error("Sélectionnez au moins une usine à lier.")
                else:
                    try:
                        inserted_count, updated_count, deleted_count = upsert_intrant_links(
                            admin_db_client,
                            intrant_name_clean,
                            ms_input,
                            mo_input,
                            bmp_input,
                            densite_input,
                            selected_site_ids,
                            remove_unselected,
                        )
                        st.success(
                            "Intrant enregistré. "
                            f"Insérés: {inserted_count}, mis à jour: {updated_count}, liens retirés: {deleted_count}."
                        )
                        st.rerun()
                    except Exception as error:
                        st.error(f"Erreur enregistrement intrant: {error}")

    with admin_tabs[1]:
        if not has_permission(selected_roles, rights, "administration", "utilisateurs"):
            st.info("Vous n'avez pas le droit de gérer les utilisateurs.")
        else:
            st.markdown("### Créer un utilisateur")
            new_user_email = st.text_input("Email nouvel utilisateur", key="admin_new_user_email")
            new_user_password = st.text_input("Mot de passe temporaire", type="password", key="admin_new_user_password")
            if st.button("Créer le compte utilisateur", key="admin_create_user", use_container_width=True):
                email_clean = new_user_email.strip().lower()
                if not email_clean or "@" not in email_clean:
                    st.error("Email invalide.")
                elif len(new_user_password) < 6:
                    st.error("Le mot de passe doit contenir au moins 6 caractères.")
                else:
                    try:
                        new_user_id = create_user_without_email(email_clean, new_user_password)

                        admin_db_client.table("app_user_profiles").upsert(
                            [{"user_id": new_user_id, "email": email_clean, "is_active": True}]
                        ).execute()
                        st.success("Utilisateur créé (ou récupéré) sans envoi d'email. Compte actif immédiatement.")
                    except Exception as error:
                        error_text = str(error)
                        if "supabase_service_role_key" in error_text.lower() or "service_role" in error_text.lower() or "service role" in error_text.lower():
                            st.error(
                                "Configurez SUPABASE_SERVICE_ROLE_KEY dans les secrets pour créer les utilisateurs sans email et sans rate-limit."
                            )
                        elif "already" in error_text.lower() or "already registered" in error_text.lower() or "already exists" in error_text.lower():
                            st.warning("Cet email existe déjà. Vous pouvez directement lui affecter un rôle/site.")
                        elif "rate limit" in error_text.lower():
                            st.error("Rate limit côté Auth détecté. Utilisez uniquement la création admin (service role key).")
                        else:
                            st.error(f"Erreur création utilisateur: {error}")

            st.markdown("### Liste des utilisateurs")
            try:
                admin_users = build_admin_users_view(admin_db_client)
            except Exception as error:
                admin_users = []
                error_text = str(error)
                if "supabase_service_role_key" in error_text.lower() or "service_role" in error_text.lower() or "service role" in error_text.lower():
                    st.error("Configurez SUPABASE_SERVICE_ROLE_KEY pour afficher et supprimer les utilisateurs.")
                else:
                    st.error(f"Impossible de charger les utilisateurs: {error}")

            if admin_users:
                users_df_rows = []
                options: dict[str, str] = {}
                current_user_id = str(st.session_state.auth_user_id).strip()

                for user_row in admin_users:
                    user_id = str(user_row.get("user_id", "")).strip()
                    email = str(user_row.get("email", "")).strip()
                    email_label = email if email else "(sans email)"
                    users_df_rows.append(
                        {
                            "Email": email_label,
                            "User ID": user_id,
                            "Actif": "Oui" if bool(user_row.get("is_active", True)) else "Non",
                            "Confirmé": "Oui" if bool(user_row.get("email_confirmed", False)) else "Non",
                            "Dernière connexion": str(user_row.get("last_sign_in_at", "")),
                        }
                    )
                    if user_id and user_id != current_user_id:
                        options[f"{email_label} — {user_id}"] = user_id

                st.dataframe(pd.DataFrame(users_df_rows), use_container_width=True, hide_index=True)

                if options:
                    selected_user_label = st.selectbox(
                        "Utilisateur à supprimer",
                        options=list(options.keys()),
                        key="admin_delete_user_select",
                    )
                    confirm_delete_user = st.checkbox(
                        "Je confirme la suppression définitive de cet utilisateur",
                        key="admin_delete_user_confirm",
                    )

                    if st.button("Supprimer l'utilisateur", key="admin_delete_user_btn", use_container_width=True):
                        if not confirm_delete_user:
                            st.error("Cochez la confirmation avant suppression.")
                        else:
                            try:
                                delete_user_everywhere(client, options[selected_user_label])
                                st.success("Utilisateur supprimé.")
                                st.rerun()
                            except Exception as error:
                                st.error(f"Erreur suppression utilisateur: {error}")
                else:
                    st.info("Aucun utilisateur supprimable (votre compte ne peut pas être supprimé ici).")
            else:
                st.info("Aucun utilisateur trouvé.")

            st.markdown("---")
            try:
                all_sites = load_sites(admin_db_client)
            except Exception:
                all_sites = []

            try:
                profiles_rows = admin_db_client.table("app_user_profiles").select("user_id, email").execute().data or []
            except Exception:
                profiles_rows = []

            for row in admin_users if 'admin_users' in locals() else []:
                row_email = str(row.get("email", "")).strip().lower()
                row_user_id = str(row.get("user_id", "")).strip()
                if row_email and row_user_id:
                    already_exists = any(
                        str(p.get("user_id", "")).strip() == row_user_id and str(p.get("email", "")).strip().lower() == row_email
                        for p in profiles_rows
                    )
                    if not already_exists:
                        profiles_rows.append({"user_id": row_user_id, "email": row_email})

            email_to_user_id = {
                str(row.get("email", "")).strip().lower(): str(row.get("user_id", "")).strip()
                for row in profiles_rows
                if str(row.get("email", "")).strip() and str(row.get("user_id", "")).strip()
            }
            user_id_to_email = {
                str(row.get("user_id", "")).strip(): str(row.get("email", "")).strip()
                for row in profiles_rows
                if str(row.get("email", "")).strip() and str(row.get("user_id", "")).strip()
            }

            for auth_row in admin_users if 'admin_users' in locals() else []:
                auth_email = str(auth_row.get("email", "")).strip().lower()
                auth_user_id = str(auth_row.get("user_id", "")).strip()
                if auth_email and auth_user_id:
                    email_to_user_id[auth_email] = auth_user_id
                    user_id_to_email[auth_user_id] = auth_email

            site_id_to_label = {
                str(s.get("id", "")): f"{s.get('name', '')} ({s.get('code', '')})"
                for s in all_sites
                if str(s.get("id", "")).strip()
            }
            site_label_to_id = {label: site_id for site_id, label in site_id_to_label.items()}

            site_options = {f"{s.get('name', '')} ({s.get('code', '')})": s.get("id", "") for s in all_sites}
            selected_site_label = st.selectbox(
                "Site pour l'affectation", options=list(site_options.keys()) if site_options else ["Aucun site"], key="admin_user_site"
            )
            user_email = st.text_input("Email utilisateur", key="admin_user_email")
            role_choice = st.selectbox("Rôle", options=ROLES, key="admin_role_choice")

            if st.button("Affecter rôle au site", key="admin_assign_role", use_container_width=True):
                target_site_id = site_options.get(selected_site_label, "")
                if not target_site_id:
                    st.error("Sélectionnez un site valide.")
                elif not is_valid_uuid(target_site_id):
                    st.error("Identifiant site invalide (UUID attendu).")
                else:
                    lookup_email = user_email.strip().lower()
                    target_user_id = email_to_user_id.get(lookup_email, "")
                    if not target_user_id:
                        try:
                            target_user_id = get_user_id_by_email_as_admin(lookup_email)
                            if target_user_id:
                                email_to_user_id[lookup_email] = target_user_id
                                if target_user_id not in user_id_to_email:
                                    user_id_to_email[target_user_id] = lookup_email
                        except Exception:
                            target_user_id = ""
                    if not target_user_id:
                        st.error("Utilisateur introuvable par email dans Supabase Auth.")
                    else:
                        payload = [
                            {
                                "user_id": target_user_id,
                                "site_id": target_site_id,
                                "role": role_choice,
                            }
                        ]
                        try:
                            admin_db_client.table("app_user_site_roles").upsert(payload).execute()
                            st.success("Rôle affecté avec succès.")
                        except Exception as error:
                            st.error(f"Erreur affectation rôle: {error}")

            st.markdown("### Affectations existantes")
            try:
                assignments = admin_db_client.table("app_user_site_roles").select("user_id, site_id, role").execute().data or []
                if assignments:
                    assignment_rows = []
                    current_set: set[tuple[str, str, str]] = set()
                    for row in assignments:
                        user_id = str(row.get("user_id", "")).strip()
                        site_id = str(row.get("site_id", "")).strip()
                        role = str(row.get("role", "")).strip().lower()
                        email = user_id_to_email.get(user_id, "")
                        site_label = site_id_to_label.get(site_id, site_id)
                        if user_id and site_id and role:
                            current_set.add((user_id, site_id, role))
                        assignment_rows.append(
                            {
                                "Email": email,
                                "Site": site_label,
                                "Rôle": role,
                                "Supprimer": False,
                            }
                        )

                    edited_df = st.data_editor(
                        pd.DataFrame(assignment_rows),
                        use_container_width=True,
                        hide_index=True,
                        key="admin_assignments_editor",
                        column_config={
                            "Site": st.column_config.SelectboxColumn("Site", options=list(site_label_to_id.keys())),
                            "Rôle": st.column_config.SelectboxColumn("Rôle", options=ROLES),
                            "Supprimer": st.column_config.CheckboxColumn("Supprimer"),
                        },
                    )

                    if st.button("Appliquer modifications de la grille", key="admin_apply_assignments", use_container_width=True):
                        desired_set: set[tuple[str, str, str]] = set()
                        errors: list[str] = []

                        for _, row in edited_df.iterrows():
                            if bool(row.get("Supprimer", False)):
                                continue
                            email = str(row.get("Email", "")).strip().lower()
                            site_label = str(row.get("Site", "")).strip()
                            role = str(row.get("Rôle", "")).strip().lower()

                            if not email:
                                errors.append("Une ligne a un email vide.")
                                continue
                            if email not in email_to_user_id:
                                errors.append(f"Utilisateur introuvable pour l'email: {email}")
                                continue
                            if site_label not in site_label_to_id:
                                errors.append(f"Site invalide: {site_label}")
                                continue
                            if role not in ROLES:
                                errors.append(f"Rôle invalide: {role}")
                                continue

                            desired_set.add((email_to_user_id[email], site_label_to_id[site_label], role))

                        if errors:
                            st.error("\n".join(sorted(set(errors))))
                        else:
                            to_delete = current_set - desired_set
                            to_insert = desired_set - current_set

                            try:
                                for user_id, site_id, role in to_delete:
                                    (
                                        admin_db_client.table("app_user_site_roles")
                                        .delete()
                                        .eq("user_id", user_id)
                                        .eq("site_id", site_id)
                                        .eq("role", role)
                                        .execute()
                                    )

                                if to_insert:
                                    payload = [
                                        {"user_id": user_id, "site_id": site_id, "role": role}
                                        for user_id, site_id, role in to_insert
                                    ]
                                    admin_db_client.table("app_user_site_roles").upsert(payload).execute()

                                st.success("Affectations mises à jour.")
                                st.rerun()
                            except Exception as error:
                                st.error(f"Erreur mise à jour des affectations: {error}")
                else:
                    st.info("Aucune affectation utilisateur/site.")
            except Exception:
                st.info("Impossible de charger les affectations.")

    with admin_tabs[2]:
        if not has_permission(selected_roles, rights, "administration", "droits"):
            st.info("Vous n'avez pas le droit de gérer les droits.")
        else:
            ensure_default_rights_rows(admin_db_client)
            role_selected = st.selectbox("Rôle à configurer", options=ROLES, key="admin_rights_role")

            existing: dict[tuple[str, str], bool] = {}
            try:
                rows = (
                    admin_db_client.table("app_role_menu_rights")
                    .select("menu_key, submenu_key, can_view")
                    .eq("role", role_selected)
                    .execute()
                    .data
                    or []
                )
                for row in rows:
                    existing[(str(row.get("menu_key", "")), str(row.get("submenu_key", "")))] = bool(row.get("can_view", False))
            except Exception:
                pass

            rights_rows = []
            for menu_key, submenu_key in RIGHTS_ITEMS:
                rights_rows.append(
                    {
                        "menu_key": menu_key,
                        "submenu_key": submenu_key,
                        "can_view": existing.get((menu_key, submenu_key), role_selected == "administrateur"),
                    }
                )

            edited = st.data_editor(
                pd.DataFrame(rights_rows),
                use_container_width=True,
                hide_index=True,
                key="admin_rights_editor",
                disabled=["menu_key", "submenu_key"],
            )

            if st.button("Enregistrer les droits", key="admin_save_rights", use_container_width=True):
                payload = []
                for _, row in edited.iterrows():
                    payload.append(
                        {
                            "role": role_selected,
                            "menu_key": str(row["menu_key"]),
                            "submenu_key": str(row["submenu_key"]),
                            "can_view": bool(row["can_view"]),
                        }
                    )
                try:
                    admin_db_client.table("app_role_menu_rights").upsert(payload).execute()
                    st.success("Droits enregistrés.")
                    st.rerun()
                except Exception as error:
                    st.error(f"Erreur enregistrement droits: {error}")


def admin_tab(client: Client, site_id: str, ingredients: list[str], ingredient_params: dict[str, dict]) -> None:
    st.subheader("Préparation de la ration")
    render_help_for_screen("ration_admin")

    selected_date = st.date_input("Date de production", value=date.today(), key="admin_date")
    selected_reacteur = st.selectbox("Réacteur", options=REACTEURS, key="admin_reacteur")

    rows = st.session_state.admin_ration_rows
    st.markdown("### Ingrédients prévus")

    for idx, _ in enumerate(rows):
        c1, c2 = st.columns([2, 1])
        ing_key = f"admin_ing_{idx}"
        ton_key = f"admin_ton_{idx}"

        default_ing = rows[idx].get("ingredient", ingredients[0])
        if default_ing not in ingredients:
            default_ing = ingredients[0]

        rows[idx]["ingredient"] = c1.selectbox(
            f"Ingrédient {idx + 1}",
            options=ingredients,
            index=ingredients.index(default_ing),
            key=ing_key,
        )
        rows[idx]["tonnage_prevu"] = c2.number_input(
            f"Prévu {idx + 1}",
            min_value=0.0,
            step=0.001,
            format="%.3f",
            key=ton_key,
        )

        params = ingredient_params.get(rows[idx]["ingredient"], {})
        st.caption(
            " | ".join(
                [
                    f"MS: {format_fr_number(to_float(params.get('ms_pct'), 0.0), 2)}%",
                    f"MO: {format_fr_number(to_float(params.get('mo_pct'), 0.0), 2)}%",
                    f"BMP: {format_fr_number(to_float(params.get('bmp_nm3_t'), 0.0), 2)} Nm3/t",
                    f"ρ: {format_fr_number(to_float(params.get('masse_volumique_t_m3'), 0.0), 3)} t/m3",
                ]
            )
        )

    st.session_state.admin_ration_rows = rows

    c_add, c_remove = st.columns(2)
    if c_add.button("➕ Ajouter une ligne", use_container_width=True):
        st.session_state.admin_ration_rows.append({"ingredient": ingredients[0], "tonnage_prevu": 0.0})
        st.rerun()

    if c_remove.button("➖ Supprimer la dernière", use_container_width=True):
        if len(st.session_state.admin_ration_rows) > 1:
            st.session_state.admin_ration_rows.pop()
            st.rerun()

    preview_rows = []
    for row in st.session_state.admin_ration_rows:
        ingredient = str(row.get("ingredient", "")).strip()
        params = ingredient_params.get(ingredient, {})
        preview_rows.append(
            {
                "ingredient": ingredient,
                "tonnage_prevu": to_float(row.get("tonnage_prevu"), 0.0),
                "ms_pct": to_float(params.get("ms_pct"), 0.0),
                "mo_pct": to_float(params.get("mo_pct"), 0.0),
                "bmp_nm3_t": to_float(params.get("bmp_nm3_t"), 0.0),
                "masse_volumique_t_m3": to_float(params.get("masse_volumique_t_m3"), 0.0),
            }
        )

    preview_totals = aggregate_kpis(preview_rows, "tonnage_prevu")
    st.markdown("### Indicateurs ration (prévu)")
    m1, m2, m3 = st.columns(3)
    m1.metric("MS totale (t)", format_fr_number(preview_totals["total_ms_t"], 3))
    m2.metric("Potentiel production (Nm3)", format_fr_number(preview_totals["total_potentiel_nm3"], 3))
    m3.metric("Volume ration (m3)", format_fr_number(preview_totals["total_volume_m3"], 3))

    if st.button("Publier la Ration", type="primary", use_container_width=True):
        rows_to_publish = st.session_state.admin_ration_rows
        invalid_tonnage = [r for r in rows_to_publish if float(r["tonnage_prevu"]) <= 0]
        if invalid_tonnage:
            st.error("Chaque ligne doit avoir un tonnage prévu strictement supérieur à 0.")
            return

        ingredient_names = [str(r.get("ingredient", "")).strip() for r in rows_to_publish]
        duplicates = [name for name, count in Counter(ingredient_names).items() if name and count > 1]
        if duplicates:
            st.error(
                "Un ingrédient ne peut apparaître qu'une seule fois dans une même ration. "
                f"Doublons détectés : {', '.join(sorted(duplicates))}"
            )
            return

        invalid_density = []
        for row in rows_to_publish:
            ingredient = str(row.get("ingredient", "")).strip()
            params = ingredient_params.get(ingredient, {})
            if to_float(params.get("masse_volumique_t_m3"), 0.0) <= 0:
                invalid_density.append(ingredient)
        if invalid_density:
            st.error(
                "Masse volumique invalide (<= 0) pour : "
                + ", ".join(sorted(list(set(invalid_density))))
                + ". Mettez à jour le référentiel ingrédients."
            )
            return

        try:
            save_ration(
                client,
                site_id,
                selected_date.isoformat(),
                selected_reacteur,
                [
                    {
                        "ingredient": row["ingredient"],
                        "tonnage_prevu": row["tonnage_prevu"],
                        "ms_pct": ingredient_params.get(row["ingredient"], {}).get("ms_pct", 0.0),
                        "mo_pct": ingredient_params.get(row["ingredient"], {}).get("mo_pct", 0.0),
                        "bmp_nm3_t": ingredient_params.get(row["ingredient"], {}).get("bmp_nm3_t", 0.0),
                        "masse_volumique_t_m3": ingredient_params.get(row["ingredient"], {}).get(
                            "masse_volumique_t_m3", 0.0
                        ),
                    }
                    for row in rows_to_publish
                ],
            )
            st.success("Ration publiée avec succès.")
        except Exception as error:
            error_text = str(error)
            if "23505" in error_text or "duplicate key" in error_text.lower():
                st.error(
                    "Publication refusée par la contrainte d'unicité. "
                    "Règle attendue: plusieurs ingrédients autorisés pour une même date/réacteur, "
                    "mais pas deux fois le même ingrédient. "
                    "Si ce message apparaît avec des ingrédients différents, appliquez le script SQL de correction."
                )
            elif "42501" in error_text or "row-level security" in error_text.lower() or "row level security" in error_text.lower():
                st.error(
                    "Publication refusée par les policies RLS de Supabase pour fiche_ration. "
                    "Appliquez le script `supabase_fiche_ration_fix.sql` puis vérifiez que votre utilisateur "
                    "a bien un rôle sur le site sélectionné dans `app_user_site_roles`. "
                    f"Détail: {error_text}"
                )
            else:
                st.error(f"Erreur lors de la publication dans Supabase (fiche_ration): {error_text}")


def operator_tab(client: Client, site_id: str, ingredients: list[str], ingredient_params: dict[str, dict]) -> None:
    st.subheader("Saisie des tonnages réels")
    render_help_for_screen("ration_operateur")

    try:
        reactor_rows = load_fiche(client, site_id=site_id)
    except Exception:
        st.error("Impossible de charger la fiche ration depuis Supabase.")
        return

    today_date = date.today()
    week_past_start = today_date - timedelta(days=7)
    week_future_end = today_date + timedelta(days=7)

    planned_by_slot: dict[tuple[str, str], list[dict]] = {}
    for row in reactor_rows:
        date_iso = normalize_date_value(row.get("date"))
        reacteur = str(row.get("reacteur", "")).strip()
        try:
            parsed = datetime.strptime(date_iso, "%Y-%m-%d").date()
        except Exception:
            continue
        if reacteur and today_date <= parsed <= week_future_end:
            planned_by_slot.setdefault((date_iso, reacteur), []).append(row)

    grid_rows: list[dict] = []
    try:
        history_rows, _ = load_ration_history(client, site_id)
    except Exception:
        history_rows = []

    for history_row in history_rows:
        reacteur = str(history_row.get("Cuve", "")).strip()
        if not reacteur:
            continue
        date_iso = normalize_date_value(history_row.get("Date"))
        try:
            parsed = datetime.strptime(date_iso, "%Y-%m-%d").date()
        except Exception:
            continue
        if week_past_start <= parsed < today_date:
            grid_rows.append(
                {
                    "Période": "Semaine précédente",
                    "Date": format_fr_date(date_iso),
                    "Réacteur": reacteur,
                    "Statut": "Chargée",
                    "Tonnage (t)": round(to_float(history_row.get("Tonnage (t)"), 0.0), 3),
                }
            )

    for date_iso, reacteur in sorted(planned_by_slot.keys()):
        rows_for_slot = planned_by_slot[(date_iso, reacteur)]
        grid_rows.append(
            {
                "Période": "Semaine à venir",
                "Date": format_fr_date(date_iso),
                "Réacteur": reacteur,
                "Statut": "À saisir",
                "Tonnage (t)": round(sum(to_float(row.get("tonnage_prevu"), 0.0) for row in rows_for_slot), 3),
            }
        )

    st.markdown("### Grille hebdomadaire")
    if grid_rows:
        st.dataframe(pd.DataFrame(grid_rows), hide_index=True, use_container_width=True)
    else:
        st.info("Aucune ration chargée la semaine précédente ni ration à venir cette semaine.")

    available_slots = sorted(planned_by_slot.keys())

    if not available_slots:
        st.info("Aucune ration à venir trouvée.")
        return

    selected_slot = available_slots[0]
    if len(available_slots) > 1:
        selected_slot = st.selectbox(
            "Ration à saisir (semaine à venir)",
            options=available_slots,
            index=0,
            format_func=lambda slot: f"{format_fr_date(slot[0])} — {slot[1]}",
            key="op_date",
        )
    else:
        st.caption(
            "Ration chargée automatiquement : "
            f"{format_fr_date(selected_slot[0])} — {selected_slot[1]}"
        )

    selected_date, selected_reacteur = selected_slot

    planned_rows = planned_by_slot.get(selected_slot, [])
    if not planned_rows:
        st.info("Aucune ligne trouvée pour cette date/réacteur.")
        return

    context_key = f"{selected_reacteur}_{selected_date}"
    extra_key = f"op_extras_{context_key}"
    if extra_key not in st.session_state:
        st.session_state[extra_key] = []

    st.markdown("### Lignes prévues")
    planned_records = []
    for idx, row in enumerate(planned_rows):
        prevu = round(float(row.get("tonnage_prevu", 0.0)), 3)
        params = {
            "ms_pct": to_float(row.get("ms_pct"), ingredient_params.get(row["ingredient"], {}).get("ms_pct", 0.0)),
            "mo_pct": to_float(row.get("mo_pct"), ingredient_params.get(row["ingredient"], {}).get("mo_pct", 0.0)),
            "bmp_nm3_t": to_float(
                row.get("bmp_nm3_t"), ingredient_params.get(row["ingredient"], {}).get("bmp_nm3_t", 0.0)
            ),
            "masse_volumique_t_m3": to_float(
                row.get("masse_volumique_t_m3"),
                ingredient_params.get(row["ingredient"], {}).get("masse_volumique_t_m3", 0.0),
            ),
        }
        input_key = f"op_reel_plan_{context_key}_{idx}"
        reel = st.number_input(
            f"{row['ingredient']} (prévu: {prevu:.3f})",
            min_value=0.0,
            step=0.001,
            format="%.3f",
            key=input_key,
        )
        ecart = round(float(reel) - prevu, 3)
        reel_kpi = compute_kpis(float(reel), params["ms_pct"], params["mo_pct"], params["bmp_nm3_t"], params["masse_volumique_t_m3"])
        st.caption(
            f"Écart: {format_fr_number(ecart, 3)} | MS: {format_fr_number(reel_kpi['tonnage_ms_t'], 3)} t | Potentiel: {format_fr_number(reel_kpi['potentiel_nm3'], 3)} Nm3 | Volume: {format_fr_number(reel_kpi['volume_m3'], 3)} m3"
        )
        planned_records.append(
            {
                "ingredient": str(row["ingredient"]),
                "tonnage_prevu": prevu,
                "tonnage_reel": round(float(reel), 3),
                "ecart": ecart,
                "ms_pct": params["ms_pct"],
                "mo_pct": params["mo_pct"],
                "bmp_nm3_t": params["bmp_nm3_t"],
                "masse_volumique_t_m3": params["masse_volumique_t_m3"],
            }
        )

    if st.button("➕ Ajouter un ingrédient imprévu", use_container_width=True):
        st.session_state[extra_key].append({"ingredient": ingredients[0]})
        st.rerun()

    st.markdown("### Ingrédients imprévus")
    extra_records = []
    for idx, _ in enumerate(st.session_state[extra_key]):
        c1, c2 = st.columns([2, 1])
        ing_key = f"op_extra_ing_{context_key}_{idx}"
        ton_key = f"op_extra_ton_{context_key}_{idx}"

        ingredient = c1.selectbox(
            f"Imprévu {idx + 1}",
            options=ingredients,
            key=ing_key,
        )
        reel = c2.number_input(
            f"Réel imprévu {idx + 1}",
            min_value=0.0,
            step=0.001,
            format="%.3f",
            key=ton_key,
        )
        ecart = round(float(reel), 3)
        params = ingredient_params.get(ingredient, {})
        reel_kpi = compute_kpis(
            float(reel),
            to_float(params.get("ms_pct"), 0.0),
            to_float(params.get("mo_pct"), 0.0),
            to_float(params.get("bmp_nm3_t"), 0.0),
            to_float(params.get("masse_volumique_t_m3"), 0.0),
        )
        st.caption(
            f"Écart: {format_fr_number(ecart, 3)} | MS: {format_fr_number(reel_kpi['tonnage_ms_t'], 3)} t | Potentiel: {format_fr_number(reel_kpi['potentiel_nm3'], 3)} Nm3 | Volume: {format_fr_number(reel_kpi['volume_m3'], 3)} m3"
        )
        extra_records.append(
            {
                "ingredient": ingredient,
                "tonnage_prevu": 0.0,
                "tonnage_reel": round(float(reel), 3),
                "ecart": ecart,
                "ms_pct": to_float(params.get("ms_pct"), 0.0),
                "mo_pct": to_float(params.get("mo_pct"), 0.0),
                "bmp_nm3_t": to_float(params.get("bmp_nm3_t"), 0.0),
                "masse_volumique_t_m3": to_float(params.get("masse_volumique_t_m3"), 0.0),
            }
        )

    planned_totals = aggregate_kpis(planned_records, "tonnage_prevu")
    real_totals = aggregate_kpis(planned_records + extra_records, "tonnage_reel")
    st.markdown("### Indicateurs calculés")
    p1, p2, p3 = st.columns(3)
    p1.metric("MS prévue (t)", format_fr_number(planned_totals["total_ms_t"], 3))
    p2.metric("Potentiel prévu (Nm3)", format_fr_number(planned_totals["total_potentiel_nm3"], 3))
    p3.metric("Volume prévu (m3)", format_fr_number(planned_totals["total_volume_m3"], 3))

    r1, r2, r3 = st.columns(3)
    r1.metric("MS réelle (t)", format_fr_number(real_totals["total_ms_t"], 3))
    r2.metric("Potentiel réel (Nm3)", format_fr_number(real_totals["total_potentiel_nm3"], 3))
    r3.metric("Volume réel (m3)", format_fr_number(real_totals["total_volume_m3"], 3))

    if st.button("Finaliser le Lot", type="primary", use_container_width=True):
        all_records = planned_records + extra_records
        if not all_records:
            st.error("Aucune ligne à enregistrer.")
            return

        invalid_density = [
            r["ingredient"] for r in all_records if to_float(r.get("masse_volumique_t_m3"), 0.0) <= 0
        ]
        if invalid_density:
            st.error(
                "Impossible de calculer le volume réel: masse volumique invalide (<= 0) pour "
                + ", ".join(sorted(list(set(invalid_density))))
                + "."
            )
            return

        try:
            batch_id = save_batch(client, site_id, selected_date, selected_reacteur, all_records)
            purge_ration(client, site_id, selected_date, selected_reacteur)
            st.session_state[extra_key] = []
            st.success(f"Lot finalisé avec succès. Batch ID: {batch_id}")
        except Exception as error:
            st.error(f"Erreur lors de la finalisation du lot dans Supabase: {error}")


init_navigation_session()
init_auth_session()

try:
    supabase = get_supabase_client()
except Exception:
    st.error(
        "Connexion Supabase impossible. Vérifiez SUPABASE_URL et SUPABASE_KEY (variables d'environnement ou st.secrets)."
    )
    st.stop()

if not st.session_state.is_authenticated:
    try_restore_auth_session(supabase)

if st.session_state.is_authenticated and st.session_state.auth_access_token and st.session_state.auth_refresh_token:
    try:
        supabase.auth.set_session(st.session_state.auth_access_token, st.session_state.auth_refresh_token)
    except Exception:
        clear_auth_session()
        clear_persisted_auth_session()

if not st.session_state.is_authenticated:
    st.subheader("Connexion")
    render_help_for_screen("connexion")
    with st.form("login_form"):
        email_input = st.text_input("Email")
        password_input = st.text_input("Mot de passe", type="password")
        remember_me_input = st.checkbox("Se souvenir de moi", value=True)
        login_clicked = st.form_submit_button("Se connecter", use_container_width=True)
    if login_clicked:
        try:
            sign_in_user(supabase, email_input.strip(), password_input, remember_me=remember_me_input)
            st.rerun()
        except Exception as error:
            st.error(f"Échec de connexion: {error}")
    st.stop()

try:
    sites = load_sites(supabase)
except Exception:
    sites = []

site_roles_map = load_user_site_roles(supabase, st.session_state.auth_user_id)
st.session_state.site_roles_map = site_roles_map

site_by_id = {str(s.get("id", "")): s for s in sites}
available_site_ids = [site_id for site_id in site_roles_map.keys() if site_id in site_by_id]

if not available_site_ids:
    st.error("Aucun site n'est affecté à votre utilisateur.")
    if st.button("Se déconnecter", use_container_width=True):
        sign_out_user(supabase)
        st.rerun()
    st.stop()
    raise SystemExit

if st.session_state.selected_site_id not in available_site_ids:
    st.session_state.selected_site_id = available_site_ids[0]

top_site, top_actions = st.columns([8, 2])
with top_site:
    site_labels = {
        site_id: f"{site_by_id[site_id].get('name', '')} ({site_by_id[site_id].get('code', '')})"
        for site_id in available_site_ids
    }
    selected_site_id = st.selectbox(
        "Usine",
        options=available_site_ids,
        format_func=lambda value: site_labels.get(value, value),
        index=available_site_ids.index(st.session_state.selected_site_id),
        label_visibility="collapsed",
    )
    st.session_state.selected_site_id = selected_site_id

with top_actions:
    action_home, action_logout = st.columns(2)
    with action_home:
        if st.button("⌂", key="top_home_btn", help="Menu"):
            go_home()
            st.rerun()
    with action_logout:
        if st.button("⎋", key="top_logout_btn", help="Déconnexion"):
            sign_out_user(supabase)
            st.rerun()

selected_roles = site_roles_map.get(st.session_state.selected_site_id, [])
effective_rights = load_role_menu_rights(supabase, selected_roles)
allowed_modules = get_allowed_modules(selected_roles, effective_rights)
can_access_admin = has_permission(selected_roles, effective_rights, "administration", "")

active_module = st.session_state.active_module

if active_module == "HOME":
    home_screen(allowed_modules, can_access_admin, supabase, site_roles_map, site_by_id)
elif active_module == "Ration":
    if not has_permission(selected_roles, effective_rights, "ration", ""):
        st.error("Accès refusé au module Ration.")
        st.stop()

    ingredients_list, ingredient_params_map = load_referentiel(supabase, st.session_state.selected_site_id)
    if not ingredients_list:
        st.warning("Le référentiel d'intrants est vide ou inaccessible pour cette usine.")
        st.stop()

    init_session(ingredients_list)

    ration_tabs = []
    if has_permission(selected_roles, effective_rights, "ration", "admin"):
        ration_tabs.append(("🛠️ Admin : Préparation", "admin"))
    if has_permission(selected_roles, effective_rights, "ration", "operateur"):
        ration_tabs.append(("👷 Opérateur : Saisie", "operateur"))
    if has_permission(selected_roles, effective_rights, "ration", "historique"):
        ration_tabs.append(("📚 Historique", "historique"))

    if not ration_tabs:
        st.info("Aucun sous-menu Ration autorisé pour votre profil.")
        st.stop()

    tab_objs = st.tabs([label for label, _ in ration_tabs])
    for tab_obj, (_, key) in zip(tab_objs, ration_tabs):
        with tab_obj:
            if key == "admin":
                admin_tab(supabase, st.session_state.selected_site_id, ingredients_list, ingredient_params_map)
            elif key == "operateur":
                operator_tab(supabase, st.session_state.selected_site_id, ingredients_list, ingredient_params_map)
            elif key == "historique":
                history_tab(supabase, st.session_state.selected_site_id)
elif active_module == "Entrées/Sorties":
    if not has_permission(selected_roles, effective_rights, "entrees_sorties", ""):
        st.error("Accès refusé au module Entrées/Sorties.")
        st.stop()

    entrees_sorties_tabs = []
    if has_permission(selected_roles, effective_rights, "entrees_sorties", "stock"):
        entrees_sorties_tabs.append(("📦 Stock", "stock"))
    if has_permission(selected_roles, effective_rights, "entrees_sorties", "registre_entrees"):
        entrees_sorties_tabs.append(("📥 Registre des entrées", "registre_entrees"))
    if has_permission(selected_roles, effective_rights, "entrees_sorties", "registre_sorties"):
        entrees_sorties_tabs.append(("📤 Registre des sorties", "registre_sorties"))

    if not entrees_sorties_tabs:
        st.info("Aucun sous-menu Entrées/Sorties autorisé pour votre profil.")
        st.stop()

    tab_objs = st.tabs([label for label, _ in entrees_sorties_tabs])
    for tab_obj, (_, key) in zip(tab_objs, entrees_sorties_tabs):
        with tab_obj:
            if key == "stock":
                stock_tab(supabase, st.session_state.selected_site_id)
            elif key == "registre_entrees":
                registre_entrees_tab(supabase, st.session_state.selected_site_id)
            elif key == "registre_sorties":
                registre_sorties_tab(supabase, st.session_state.selected_site_id)
elif active_module == "Administration":
    admin_module(supabase, st.session_state.selected_site_id, selected_roles, effective_rights)
elif active_module == "Maintenance":
    current_site = site_by_id.get(st.session_state.selected_site_id, {})
    maintenance_module(
        supabase,
        st.session_state.selected_site_id,
        str(current_site.get("code", "")),
        str(current_site.get("name", "")),
    )
elif active_module == "Sécurité":
    current_site = site_by_id.get(st.session_state.selected_site_id, {})
    securite_module(
        supabase,
        st.session_state.selected_site_id,
        str(current_site.get("code", "")),
        str(current_site.get("name", "")),
        selected_roles,
        effective_rights,
    )
elif active_module == "Energie":
    current_site = site_by_id.get(st.session_state.selected_site_id, {})
    energie_module(
        supabase,
        st.session_state.selected_site_id,
        str(current_site.get("code", "")),
        str(current_site.get("name", "")),
        selected_roles,
        effective_rights,
    )
elif active_module in MODULES:
    if not has_permission(selected_roles, effective_rights, MENU_KEYS.get(active_module, ""), ""):
        st.error("Accès refusé à ce module.")
    else:
        under_construction_screen(active_module)
else:
    go_home()
    st.rerun()

st.markdown(
    f"<div style='position:fixed; right:16px; bottom:8px; font-size:0.74rem; color:{BRAND_MUTED}; opacity:0.85; z-index:999;'>{st.session_state.auth_email}</div>",
    unsafe_allow_html=True,
)
