import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide")

st.title("Evaluación Trimestral – Personal Shopper (Piloto Ejecutivo)")

# ---------------------------------------------------
# FUNCIONES
# ---------------------------------------------------

def normalize(series, reverse=False):
    min_val = series.min()
    max_val = series.max()
    if max_val - min_val == 0:
        return pd.Series([100]*len(series))
    norm = (series - min_val) / (max_val - min_val)
    if reverse:
        norm = 1 - norm
    return norm * 100

def performance_label(score):
    if score >= 95: return "Excelente"
    if score >= 85: return "Sobresaliente"
    if score >= 75: return "Aceptable"
    if score >= 65: return "En mejora"
    return "Plan de acción"

def feedback(scores):
    msg = []
    if scores["Ventas"] < 70:
        msg.append("Debo reforzar mi disciplina comercial diaria y fortalecer mi seguimiento.")
    if scores["Procesos"] < 70:
        msg.append("Necesito mejorar tiempos de respuesta y trazabilidad operativa.")
    if scores["Normativa"] < 70:
        msg.append("Debo alinear completamente mi gestión a la política comercial y control de descuentos.")
    if scores["Calidad"] < 75:
        msg.append("Tengo oportunidad de mejorar la experiencia y satisfacción del cliente.")
    if not msg:
        msg.append("Estoy manteniendo un desempeño sólido y consistente.")
    return " ".join(msg)

def qualitative_matrix(total_score, scores):

    if total_score >= 90:
        nivel = "Alto Desempeño"
        narrativa = (
            "He demostrado consistencia en mis resultados comerciales y disciplina en la ejecución de procesos. "
            "Mi desempeño impacta positivamente los resultados del equipo."
        )
        plan = (
            "Plan de Refuerzo:\n"
            "- Profundizar conocimiento avanzado de producto.\n"
            "- Liderar buenas prácticas internas.\n"
            "- Formación en cierre consultivo avanzado.\n"
            "- Asumir mayor volumen o cuentas estratégicas."
        )

    elif total_score >= 75:
        nivel = "Desempeño Estable"
        narrativa = (
            "Estoy cumpliendo con los estándares esperados, aunque identifico oportunidades claras "
            "para elevar mi impacto comercial y mejorar consistencia."
        )
        plan = (
            "Plan de Mejora:\n"
            "- Capacitación en técnicas de cierre.\n"
            "- Entrenamiento en aumento de ticket promedio.\n"
            "- Revisión semanal de indicadores.\n"
            "- Simulación de casos comerciales."
        )

    elif total_score >= 65:
        nivel = "Desempeño en Riesgo"
        narrativa = (
            "Reconozco que mi desempeño presenta variaciones que pueden afectar los resultados del área."
        )
        plan = (
            "Plan Correctivo:\n"
            "- Capacitación obligatoria en producto y política comercial.\n"
            "- Seguimiento semanal de metas.\n"
            "- Evaluación cada 30 días."
        )

    else:
        nivel = "Desempeño Crítico"
        narrativa = (
            "Mi desempeño actual no cumple con los estándares establecidos."
        )
        plan = (
            "Plan de Mejoramiento Formal:\n"
            "- Plan firmado con metas claras.\n"
            "- Acompañamiento directo 30 días.\n"
            "- Evaluación quincenal."
        )

    recomendaciones = []

    if scores["Ventas"] < 70:
        recomendaciones.append("Debo reforzar mi disciplina comercial y priorizar cierre efectivo.")

    if scores["Ticket"] < 70:
        recomendaciones.append("Necesito trabajar en elevar el valor promedio por cliente.")

    if scores["Procesos"] < 70:
        recomendaciones.append("Debo fortalecer cumplimiento de procesos y tiempos de respuesta.")

    if scores["Normativa"] < 75:
        recomendaciones.append("Es fundamental mejorar alineación a políticas comerciales.")

    if scores["Calidad"] < 75:
        recomendaciones.append("Debo enfocarme en mejorar satisfacción del cliente.")

    recomendacion_final = "\n".join(recomendaciones) if recomendaciones else "Mantengo consistencia y busco elevar mi impacto estratégico."

    return nivel, narrativa, recomendacion_final, plan

# ---------------------------------------------------
# CARGA EXCEL
# ---------------------------------------------------

file = st.file_uploader("Subir Excel consolidado (Nov–Feb)", type=["xlsx"])

if file:

    df = pd.read_excel(file)

    # ---------------- Indicadores ----------------

    df["Score Ventas"] = normalize(df["Ventas netas"])
    df["Score Ticket"] = normalize(df["Ticket Promedio Neto"])
    df["Score Cierre"] = normalize(df["Tasa de Conversion"])
    df["Score Calidad"] = df["Satisfaccion Cliente"]

    df["Tiempo_min"] = df["Tiempo de Respuesta"].str.extract(r'(\d+)').astype(float)
    df["Score Respuesta"] = normalize(df["Tiempo_min"], reverse=True)
    df["Score Contactos"] = normalize(df["Total contactos Asignados"])
    df["Score Procesos"] = (df["Score Respuesta"]*0.6 + df["Score Contactos"]*0.4)

    df["Ratio_desc"] = abs(df["Descuentos a nivel de pedido"] / df["Ventas totales"])
    df["Score Normativa"] = normalize(df["Ratio_desc"], reverse=True)

    # ---------------- Selección empleado ----------------

    employee = st.selectbox("Seleccionar empleado", df["Nombre del miembro del personal"])

    emp = df[df["Nombre del miembro del personal"] == employee].iloc[0]

    scores = {
        "Ventas": emp["Score Ventas"],
        "Ticket": emp["Score Ticket"],
        "Cierre": emp["Score Cierre"],
        "Procesos": emp["Score Procesos"],
        "Normativa": emp["Score Normativa"],
        "Calidad": emp["Score Calidad"]
    }

    weights = {
        "Ventas":0.30,
        "Ticket":0.10,
        "Cierre":0.10,
        "Procesos":0.20,
        "Normativa":0.15,
        "Calidad":0.15
    }

    total = sum(scores[k]*weights[k] for k in scores)
    label = performance_label(total)

    # ---------------- Score ----------------

    st.metric("Score Final", f"{total:.1f}", label)

    # ---------------- Radar ----------------

    dim_labels = list(scores.keys())
    values = list(scores.values())
    r = values + [values[0]]
    theta = dim_labels + [dim_labels[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=r, theta=theta, fill='toself'))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,100])),
        showlegend=False,
        title="Radar de Desempeño"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- Ranking ----------------

    df["Score Total"] = (
        df["Score Ventas"]*0.30 +
        df["Score Ticket"]*0.10 +
        df["Score Cierre"]*0.10 +
        df["Score Procesos"]*0.20 +
        df["Score Normativa"]*0.15 +
        df["Score Calidad"]*0.15
    )

    st.subheader("Ranking General")
    ranking = df.sort_values("Score Total", ascending=False)[
        ["Nombre del miembro del personal","Score Total"]
    ]
    st.dataframe(ranking, use_container_width=True)

    # ---------------- Evaluación Cualitativa ----------------

    st.divider()
    st.header("Evaluación Cualitativa")

    nivel, narrativa, recomendacion_final, plan = qualitative_matrix(total, scores)

    st.subheader("Nivel de Desempeño")
    st.write(nivel)

    st.subheader("Diagnóstico General")
    st.write(narrativa)

    st.subheader("Recomendaciones Específicas")
    st.write(recomendacion_final)

    st.subheader("Plan de Mejoramiento / Refuerzo")
    st.write(plan)