"""
Aplica sobre tu app.py (Inventarios ALDC) los ajustes de diseño y las
correcciones de gráficos. No toca motor_lifo.py ni la lógica de cálculo.

Uso:
    python aplicar_cambios.py app.py
Genera app_nuevo.py (tu archivo original queda intacto).
Si alguna pieza no se encuentra, la lista al final y no la aplica.
"""
import ast
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------
# LOGIN NUEVO
# ---------------------------------------------------------------
NUEVO_LOGIN = r'''def _logo_login():

    # Si pones un logo local junto a app.py (logo.png, logo.jpg ...)
    # se usa ese; si no, se usa la URL de siempre.
    base = os.path.dirname(os.path.abspath(__file__))

    for nombre in ("logo.png", "logo.jpg", "logo.jpeg", "logo.webp", "logo_aldc.png"):
        ruta = os.path.join(base, nombre)
        if os.path.exists(ruta):
            return ruta

    return LOGO_URL


def login():

    st.markdown(
        """
        <style>
        .stApp,
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 88% 8%, rgba(245,130,32,0.20) 0, rgba(245,130,32,0) 36%),
                linear-gradient(135deg, #003B7A 0%, #064B9B 60%, #0B5AAE 100%) !important;
        }

        .block-container {
            padding-top: 7vh !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.login-marker) {
            background: #FFFFFF !important;
            border: 0 !important;
            border-top: 5px solid #F58220 !important;
            border-radius: 20px !important;
            box-shadow: 0 24px 60px rgba(0,20,50,0.38) !important;
            padding: 1.6rem 1.7rem 1.2rem 1.7rem !important;
        }

        div[data-testid="stImage"] {
            display: flex;
            justify-content: center;
        }

        .login-head {
            text-align: center;
            margin: 0.5rem 0 1.3rem 0;
        }

        .login-title {
            color: #003B7A;
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            line-height: 1.15;
        }

        .login-sub {
            color: #667892;
            font-size: 0.9rem;
            margin: 0.4rem 0 0 0;
        }

        .login-accent {
            width: 44px;
            height: 4px;
            border-radius: 4px;
            background: #F58220;
            margin: 0.95rem auto 0 auto;
        }

        div[data-testid="stForm"] {
            border: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="stForm"] label p {
            color: #003B7A !important;
            font-weight: 650 !important;
            font-size: 0.82rem !important;
        }

        div[data-baseweb="input"] {
            background: #F4F7FB !important;
            border: 1px solid #D5DFEB !important;
            border-radius: 10px !important;
            min-height: 46px !important;
        }

        div[data-baseweb="base-input"] {
            background: transparent !important;
            border-radius: 10px !important;
        }

        div[data-baseweb="input"]:focus-within {
            border-color: #064B9B !important;
            box-shadow: 0 0 0 3px rgba(6,75,155,0.15) !important;
        }

        div[data-baseweb="input"] input {
            color: #0F2745 !important;
            font-size: 0.95rem !important;
        }

        div[data-testid="stFormSubmitButton"] > button {
            background: #064B9B !important;
            border: 1px solid #064B9B !important;
            color: #FFFFFF !important;
            border-radius: 10px !important;
            min-height: 48px !important;
            font-size: 0.98rem !important;
            font-weight: 700 !important;
            box-shadow: 0 6px 16px rgba(6,75,155,0.28) !important;
            margin-top: 0.35rem;
        }

        div[data-testid="stFormSubmitButton"] > button:hover {
            background: #003B7A !important;
            border-color: #003B7A !important;
            transform: translateY(-1px);
        }

        div[data-testid="stFormSubmitButton"] > button:focus-visible {
            outline: none !important;
            box-shadow: 0 0 0 3px rgba(245,130,32,0.45) !important;
        }

        .login-footer {
            margin-top: 1.1rem;
            padding-top: 0.9rem;
            border-top: 1px solid #E3EAF3;
            text-align: center;
            color: #7A8AA0;
            font-size: 0.76rem;
            line-height: 1.6;
        }

        .login-footer strong {
            color: #003B7A;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col_izq, col_centro, col_der = st.columns(
        [1, 1.15, 1]
    )

    with col_centro:

        with st.container(border=True):

            st.markdown(
                '<span class="login-marker"></span>',
                unsafe_allow_html=True
            )

            st.image(
                _logo_login(),
                width=190
            )

            st.markdown(
                """
                <div class="login-head">
                    <div class="login-title">Inventarios ALDC</div>
                    <p class="login-sub">Plataforma de gestión y analítica de inventarios</p>
                    <div class="login-accent"></div>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form("form_login", clear_on_submit=False):

                usuario = st.text_input(
                    "Usuario",
                    placeholder="Ingrese su usuario",
                    key="login_usuario"
                )

                contraseña = st.text_input(
                    "Contraseña",
                    type="password",
                    placeholder="Ingrese su contraseña",
                    key="login_contraseña"
                )

                ingresar = st.form_submit_button(
                    "Ingresar",
                    use_container_width=True
                )

            if ingresar:

                if (
                    usuario in USUARIOS
                    and USUARIOS[usuario] == contraseña
                ):

                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = usuario
                    st.session_state["inicio_sesion"] = datetime.now()

                    st.session_state.pop(
                        "login_usuario",
                        None
                    )

                    st.session_state.pop(
                        "login_contraseña",
                        None
                    )

                    st.rerun()

                else:

                    st.error(
                        "Usuario o contraseña incorrectos."
                    )

            st.markdown(
                """
                <div class="login-footer">
                    <strong>Área Limpia D.C. S.A.S. E.S.P.</strong><br>
                    🔒 Acceso protegido · Sistema de gestión y análisis de inventarios
                </div>
                """,
                unsafe_allow_html=True
            )


'''

# ---------------------------------------------------------------
# CSS ADICIONAL (va dentro del f-string del CSS principal: llaves dobles)
# ---------------------------------------------------------------
CSS_EXTRA = r'''    hr {{
        border-color: {GRIS_BORDE} !important;
    }}

    /* =========================================================
       AJUSTES DE MARCA Y CONSISTENCIA
       ========================================================= */
    .brand-mark {{
        background: {NARANJA} !important;
    }}

    .sidebar-menu-item.active {{
        border-left: 3px solid {NARANJA} !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {{
        border-color: rgba(245,130,32,0.55) !important;
        box-shadow: inset 3px 0 0 {NARANJA}, 0 2px 7px rgba(0,0,0,0.10) !important;
    }}

    .header-pill.accent {{
        background: {NARANJA_SUAVE};
        border-color: {NARANJA_CLARO};
        color: #B85A00 !important;
    }}

    div[data-testid="metric-container"],
    div[data-testid="stMetric"] {{
        border-top: 3px solid {AZUL} !important;
        transition: box-shadow 0.18s ease, transform 0.18s ease;
    }}

    div[data-testid="metric-container"]:hover,
    div[data-testid="stMetric"]:hover {{
        box-shadow: 0 8px 22px rgba(0,59,122,0.10);
        transform: translateY(-1px);
    }}

    /* Métricas dentro de una tarjeta: sin "tarjeta dentro de tarjeta" */
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="metric-container"],
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stMetric"] {{
        border: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
        min-height: 0 !important;
        transform: none !important;
    }}

    h3 {{
        font-size: 1.12rem !important;
    }}

    .stDownloadButton > button:hover {{
        background: {AZUL_SUAVE} !important;
        border-color: {AZUL_OSCURO} !important;
        color: {AZUL_OSCURO} !important;
    }}
    </style>'''


def main(ruta_entrada):
    errores = []

    def rep(texto, viejo, nuevo, nombre, todos=False):
        if viejo not in texto:
            errores.append(nombre)
            return texto
        return texto.replace(viejo, nuevo) if todos else texto.replace(viejo, nuevo, 1)

    def seccion(texto, ini, fin, funcion, nombre):
        i = texto.find(ini)
        j = texto.find(fin, i + len(ini)) if i >= 0 else -1
        if i < 0 or j < 0:
            errores.append("sección " + nombre)
            return texto
        return texto[:i] + funcion(texto[i:j]) + texto[j:]

    ruta = Path(ruta_entrada)
    t = unicodedata.normalize("NFC", ruta.read_text(encoding="utf-8")).replace("\r\n", "\n")

    # 1. Paleta de marca ------------------------------------------------
    for viejo, nuevo in [
        ('AZUL = "#2D6CDF"', 'AZUL = "#064B9B"'),
        ('AZUL_OSCURO = "#102D50"', 'AZUL_OSCURO = "#003B7A"'),
        ('AZUL_MEDIO = "#1F4C7A"', 'AZUL_MEDIO = "#0B5AAE"'),
        ('AZUL_CLARO = "#6E9FE8"', 'AZUL_CLARO = "#5B93D3"'),
        ('AZUL_SUAVE = "#EAF2FF"', 'AZUL_SUAVE = "#E8F1FB"'),
        ('NARANJA = "#F29B86"', 'NARANJA = "#F58220"'),
        ('NARANJA_CLARO = "#F7B6A7"', 'NARANJA_CLARO = "#F9B56E"'),
        ('NARANJA_SUAVE = "#FFF0EC"', 'NARANJA_SUAVE = "#FFF1E3"'),
    ]:
        t = rep(t, viejo, nuevo, "paleta " + viejo)

    t = rep(t, "rgba(45,108,223", "rgba(6,75,155", "rgba azul", todos=True)
    t = rep(t, "rgba(16,45,80", "rgba(0,59,122", "rgba sombra", todos=True)

    # Colores por defecto de los gráficos px (p. ej. barras por bodega)
    t = rep(
        t,
        'BLANCO = "#FFFFFF"\n',
        'BLANCO = "#FFFFFF"\n\n'
        'px.defaults.color_discrete_sequence = [\n'
        '    AZUL, NARANJA, VERDE, MORADO, AMARILLO, AZUL_CLARO, ROJO,\n'
        '    "#4D6F91", "#9AA9BA", AZUL_OSCURO, "#2FA4A9",\n'
        '    NARANJA_CLARO, VERDE_CLARO, "#B7A8FF"\n'
        ']\n',
        "colores px",
    )

    # 2. CSS adicional --------------------------------------------------
    t = rep(
        t,
        "    hr {{\n        border-color: {GRIS_BORDE} !important;\n    }}\n    </style>",
        CSS_EXTRA,
        "css adicional",
    )

    t = rep(
        t,
        '<div class="header-pill">Corte: {ESQ["corte"]}</div>',
        '<div class="header-pill accent">Corte: {ESQ["corte"]}</div>',
        "pill corte",
    )

    # 3. Login ----------------------------------------------------------
    i = t.find("def login():")
    j = t.find("# ============================================================\n# INICIALIZAR SESIÓN")
    if i < 0 or j < 0:
        errores.append("login")
    else:
        t = t[:i] + NUEVO_LOGIN + t[j:]

    # 4. Valor total basado en la columna de costo (base de los %) ------
    t = rep(
        t,
        "stock_total, valor_total, rotacion, dias_promedio = kpis_corte(\n    df_filtrado,\n    ESQ\n)\n",
        "stock_total, valor_total, rotacion, dias_promedio = kpis_corte(\n    df_filtrado,\n    ESQ\n)\n\n"
        "# Suma de la columna de costo: base de todos los porcentajes mostrados\n"
        "valor_total_col = suma_columna(df_filtrado, COL_COSTE)\n",
        "valor_total_col",
    )

    # 5. Resumen --------------------------------------------------------
    def f_resumen(s):
        s = rep(s, "k1, k2, k3, k4, k5 = st.columns(5)", "k1, k2, k3, k4 = st.columns(4)", "resumen: columnas KPI")
        s = rep(s, "with k4:", "with k3:", "resumen: k4")
        s = rep(s, "with k5:", "with k4:", "resumen: k5")
        s = rep(s, "valor_mayor_12,\n        valor_total\n", "valor_mayor_12,\n        valor_total_col\n", "resumen: % envejecido")
        s = rep(
            s,
            "    mes_mayor_entrada = (\n",
            "    if abs(valor_total - valor_total_col) > 1:\n"
            "        st.caption(\n"
            '            "⚠️ El valor del KPI difiere de la suma de la columna de costo del corte; "\n'
            '            "los porcentajes usan la suma de la columna."\n'
            "        )\n\n"
            "    mes_mayor_entrada = (\n",
            "resumen: aviso diferencia",
        )
        s = rep(
            s,
            "        configurar_figura(\n            fig_area,\n            390\n        )",
            "        configurar_figura(\n            fig_area,\n            390\n        )\n\n"
            '        fig_area.update_yaxes(categoryorder="total ascending")',
            "resumen: orden áreas",
        )
        s = rep(s, 'title="Envejecimiento del valor",', 'title="Valor del inventario por antigüedad (LIFO)",', "resumen: título edad")
        s = rep(
            s,
            "        configurar_figura(\n            fig_edad,\n            390\n        )",
            "        configurar_figura(\n            fig_edad,\n            390\n        )\n\n"
            "        fig_edad.update_yaxes(\n"
            '            categoryorder="array",\n'
            "            categoryarray=ORDEN_ANTIGUEDAD[::-1]\n"
            "        )",
            "resumen: orden antigüedad",
        )
        return s

    t = seccion(t, 'if pagina == "Resumen":', 'elif pagina == "Inventario":', f_resumen, "Resumen")

    # 6. Inventario -----------------------------------------------------
    def f_inventario(s):
        s = rep(s, "/ valor_total\n", "/ valor_total_col\n", "inventario: base %", todos=True)
        s = rep(s, "if valor_total != 0", "if valor_total_col != 0", "inventario: condición %", todos=True)
        s = rep(
            s,
            'title="Top 12 artículos por valor de inventario",',
            "title=f\"Top 12 artículos por valor de inventario — corte {ESQ['corte']}\",",
            "inventario: título top",
        )
        return s

    t = seccion(t, 'elif pagina == "Inventario":', 'elif pagina == "Evolución":', f_inventario, "Inventario")

    # 7. Evolución ------------------------------------------------------
    def f_evolucion(s):
        s = rep(
            s,
            '    total_entradas = df_mensual["Entradas"].sum()',
            '    if antiguedad_seleccionada != "Todas":\n'
            "        st.info(\n"
            '            "La antigüedad se calcula con el corte actual: la serie mensual "\n'
            '            "muestra el histórico de los registros que hoy pertenecen a ese rango."\n'
            "        )\n\n"
            '    total_entradas = df_mensual["Entradas"].sum()',
            "evolución: aviso antigüedad",
        )
        s = rep(s, 'title="Movimientos y trayectoria del inventario",',
                'title="Entradas y salidas mensuales vs. stock de cierre",', "evolución: título")
        s = rep(s, 'title="Entradas / Salidas",', 'title="Entradas / Salidas (unidades)",', "evolución: eje y")
        s = rep(s, 'title="Stock",\n            overlaying="y",',
                'title="Stock de cierre (unidades)",\n            rangemode="tozero",\n            overlaying="y",',
                "evolución: eje y2")
        s = rep(s, 'name="Stock",', 'name="Stock de cierre",', "evolución: leyenda stock")
        s = rep(s, 'categoryarray=ESQ["etiquetas"],', 'categoryarray=df_mensual["Mes"].tolist(),', "evolución: orden meses")
        s = rep(s, 'title="Valor de los movimientos",', 'title="Valor de entradas y salidas por mes",', "evolución: título costos")
        s = rep(s, 'yaxis_title="Valor",', 'yaxis_title="Valor ($)",', "evolución: eje costos")
        s = rep(s, 'title="Comportamiento de la rotación",', 'title="Rotación promedio por registro",', "evolución: título rotación")
        return s

    t = seccion(t, 'elif pagina == "Evolución":', 'elif pagina == "Riesgos y detalle":', f_evolucion, "Evolución")

    # 8. Riesgos y detalle ----------------------------------------------
    def f_riesgos(s):
        s = rep(s, "valor_alerta,\n        valor_total\n", "valor_alerta,\n        valor_total_col\n", "riesgos: % participación")
        s = rep(
            s,
            'title="Mayor valor concentrado en inventario > 12 meses",',
            "title=f\"Mayor valor concentrado en inventario > 12 meses — corte {ESQ['corte']}\",",
            "riesgos: título",
        )
        s = rep(
            s,
            "    columnas_disponibles = [\n        columna\n        for columna in columnas_detalle\n"
            "        if columna is not None\n        and columna in df_filtrado.columns\n    ]",
            "    # COL_ROTACION puede ser una lista de columnas: se aplanan\n"
            "    columnas_planas = []\n\n"
            "    for columna in columnas_detalle:\n"
            "        if isinstance(columna, (list, tuple)):\n"
            "            columnas_planas.extend(columna)\n"
            "        else:\n"
            "            columnas_planas.append(columna)\n\n"
            "    columnas_disponibles = []\n\n"
            "    for columna in columnas_planas:\n"
            "        if (\n"
            "            columna is not None\n"
            "            and columna in df_filtrado.columns\n"
            "            and columna not in columnas_disponibles\n"
            "        ):\n"
            "            columnas_disponibles.append(columna)",
            "riesgos: columnas detalle",
        )
        s = rep(
            s,
            "    df_detalle = df_filtrado[\n        columnas_disponibles\n    ].copy()",
            "    df_detalle = df_filtrado[\n        columnas_disponibles\n    ].copy()\n\n"
            "    if COL_COSTE in df_detalle.columns:\n"
            "        df_detalle = df_detalle.sort_values(\n"
            "            COL_COSTE,\n"
            "            ascending=False\n"
            "        )",
            "riesgos: orden detalle",
        )
        return s

    t = seccion(t, 'elif pagina == "Riesgos y detalle":', "# PIE", f_riesgos, "Riesgos y detalle")

    # 9. Verificación y salida -------------------------------------------
    try:
        ast.parse(t)
        print("Sintaxis del resultado: OK")
    except SyntaxError as e:
        print("¡Ojo! El resultado tiene un error de sintaxis:", e)

    salida = ruta.with_name(ruta.stem + "_nuevo.py")
    salida.write_text(t, encoding="utf-8")
    print("Archivo generado:", salida)

    if errores:
        print("\nNo se pudieron aplicar (el texto original no coincidió):")
        for e in errores:
            print(" -", e)
    else:
        print("Todos los cambios se aplicaron.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "app.py")
