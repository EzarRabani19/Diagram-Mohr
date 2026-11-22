import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# Konfigurasi Halaman
st.set_page_config(
    page_title="Diagram Mohr & Kriteria Keruntuhan", page_icon="🪨", layout="wide"
)

st.title("Diagram Mohr & Kriteria Keruntuhan Batuan - By Ezar")
st.caption(
    "Aplikasi interaktif untuk analisis tegangan bidang 2D (Lingkaran Mohr) dan"
    " data uji triaksial (Mohr-Coulomb & Hoek-Brown)."
)


# Fungsi bantu konversi figure Matplotlib ke PNG (300 DPI)
def fig_to_bytes(fig):
  buf = io.BytesIO()
  fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
  buf.seek(0)
  return buf


# Fungsi regresi linear analitik (bebas error SVD / LinAlgError)
def linear_regression_exact(x, y):
  x_mean = np.mean(x)
  y_mean = np.mean(y)
  denom = np.sum((x - x_mean) ** 2)
  if denom == 0:
    return 0.0, y_mean, 0.0
  slope = np.sum((x - x_mean) * (y - y_mean)) / denom
  intercept = y_mean - slope * x_mean
  y_pred = slope * x + intercept
  ss_tot = np.sum((y - y_mean) ** 2)
  r2 = 1.0 - (np.sum((y - y_pred) ** 2) / ss_tot) if ss_tot > 0 else 0.0
  return slope, intercept, r2


# Navigasi Tab
tab1, tab2 = st.tabs([
    "📐 Lingkaran Mohr 2D & Bidang AB",
    "📊 Uji Triaksial (Mohr-Coulomb & Hoek-Brown)",
])

# ==============================================================================
# TAB 1: LINGKARAN MOHR 2D
# ==============================================================================
with tab1:
  st.subheader("Analisis Tegangan Bidang 2D & Bidang Miring AB")
  st.info(
      "Konvensi Mekanika Batuan: Tegangan tekan (kompresi) bernilai **positif"
      " (+)**."
  )

  col_in1, col_out1 = st.columns([1, 2], gap="large")

  with col_in1:
    st.markdown("#### Parameter Input")
    sx = st.number_input(
        "Tegangan Normal Horizontal, σx (kN/m²)", value=0.0, step=1.0
    )
    sy = st.number_input(
        "Tegangan Normal Vertikal, σy (kN/m²)", value=0.0, step=1.0
    )
    txy = st.number_input("Tegangan Geser, τxy (kN/m²)", value=0.0, step=1.0)
    theta_d = st.number_input(
        "Sudut Bidang AB, θ (°)",
        value=0.0,
        min_value=0.0,
        max_value=180.0,
        step=1.0,
    )
    arah_rotasi = st.radio(
        "Arah Rotasi Normal Bidang AB dari Sumbu-X:",
        options=[
            "Berlawanan Jarum Jam (CCW)",
            "Searah Jarum Jam (CW)",
        ],
        index=0,
    )
    ccw = arah_rotasi == "Berlawanan Jarum Jam (CCW)"

    # Perhitungan Analitik
    sigma_avg = (sx + sy) / 2.0
    R = np.sqrt(((sx - sy) / 2.0) ** 2 + txy**2)
    sigma_1_prin = sigma_avg + R
    sigma_3_prin = sigma_avg - R

    # Konvensi plot: CCW = +tau (atas), CW = -tau (bawah)
    tau_X = -txy
    tau_Y = txy

    two_theta = np.radians(2 * theta_d) if ccw else -np.radians(2 * theta_d)
    dx = sx - sigma_avg
    dy = tau_X - 0.0

    sigma_n = sigma_avg + dx * np.cos(two_theta) - dy * np.sin(two_theta)
    tau_n = dx * np.sin(two_theta) + dy * np.cos(two_theta)

    st.markdown("---")
    st.markdown("#### Hasil Perhitungan")
    m1, m2 = st.columns(2)
    m1.metric("Pusat Lingkaran (σ_avg)", f"{sigma_avg:.2f} kN/m²")
    m2.metric("Jari-jari Lingkaran (R)", f"{R:.2f} kN/m²")

    m3, m4 = st.columns(2)
    m3.metric("Tegangan Utama Mayor (σ1)", f"{sigma_1_prin:.2f} kN/m²")
    m4.metric("Tegangan Utama Minor (σ3)", f"{sigma_3_prin:.2f} kN/m²")

    st.success(
        f"**Hasil pada Bidang AB (θ = {theta_d:.1f}°):**\n\n"
        f"- **Tegangan Normal (σₙ):** `{sigma_n:.3f} kN/m²`\n"
        f"- **Tegangan Geser (|τₙ|):** `{abs(tau_n):.3f} kN/m²` *(bertanda:"
        f" {tau_n:.3f})*"
    )

  with col_out1:
    st.markdown("#### Plot Lingkaran Mohr 2D")
    fig1, ax = plt.subplots(figsize=(8, 7))
    angles = np.linspace(0, 2 * np.pi, 360)
    circle_sigma = sigma_avg + R * np.cos(angles)
    circle_tau = R * np.sin(angles)

    ax.plot(circle_sigma, circle_tau, "b-", linewidth=2, label="Lingkaran Mohr")
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)

    ax.plot(
        [sx, sy],
        [tau_X, tau_Y],
        "k--",
        alpha=0.6,
        label="Garis Keadaan Awal (X - Y)",
    )
    ax.plot(
        [sigma_avg, sigma_n],
        [0, tau_n],
        "r-",
        linewidth=1.8,
        label=f"Bidang AB (2θ = {2 * theta_d:.0f}°)",
    )

    offset_y = max(R * 0.1, 1.5)
    ax.scatter([sigma_avg], [0], color="black", zorder=5)
    ax.text(
        sigma_avg,
        -offset_y,
        f"C ({sigma_avg:.1f}, 0)",
        fontsize=9,
        ha="center",
    )

    ax.scatter([sx, sy], [tau_X, tau_
