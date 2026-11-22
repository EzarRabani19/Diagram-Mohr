import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# Konfigurasi Halaman (Muncul sebagai judul tab browser & link preview WhatsApp)
st.set_page_config(
    page_title="Diagram Mohr & Kriteria Keruntuhan", page_icon="🪨", layout="wide"
)

st.title("Diagram Mohr & Kriteria Keruntuhan Batuan - By Ezar")
st.caption(
    "Aplikasi interaktif untuk analisis tegangan bidang 2D (Lingkaran Mohr) dan"
    " data uji triaksial (Mohr-Coulomb & Hoek-Brown)."
)


# Fungsi bantu untuk mengonversi figure Matplotlib ke buffer PNG (300 DPI)
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

    ax.scatter([sx, sy], [tau_X, tau_Y], color="green", zorder=5)
    ax.text(sx + 1.5, tau_X - 2, f"X ({sx}, {tau_X})", fontsize=9, color="green")
    ax.text(
        sy + 1.5, tau_Y + 1.5, f"Y ({sy}, {tau_Y})", fontsize=9, color="green"
    )

    ax.scatter([sigma_n], [tau_n], color="red", s=60, zorder=6)
    ax.text(
        sigma_n + 2,
        tau_n + 2,
        f"Bidang AB\n(σ={sigma_n:.2f}, τ={tau_n:.2f})",
        fontsize=9.5,
        fontweight="bold",
        color="red",
    )

    ax.scatter([sigma_1_prin, sigma_3_prin], [0, 0], color="purple", zorder=5)
    ax.text(
        sigma_1_prin + 1.5,
        1.5,
        f"σ1={sigma_1_prin:.1f}",
        fontsize=9,
        color="purple",
    )
    ax.text(
        sigma_3_prin - 12,
        1.5,
        f"σ3={sigma_3_prin:.1f}",
        fontsize=9,
        color="purple",
    )

    ax.set_aspect("equal", adjustable="box")
    plot_r = max(R, 10.0)
    ax.set_xlim(min(-15, sigma_3_prin - 15), max(25, sigma_1_prin + 22))
    ax.set_ylim(-plot_r - 15, plot_r + 15)
    ax.grid(True, linestyle=":", alpha=0.7)
    ax.set_xlabel("Tegangan Normal, σ (kN/m²)", fontsize=11, fontweight="bold")
    ax.set_ylabel(
        "Tegangan Geser, τ (kN/m²) [CCW +]", fontsize=11, fontweight="bold"
    )
    ax.set_title(
        "Analisis Lingkaran Mohr 2D & Bidang AB", fontsize=13, fontweight="bold"
    )
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()

    st.pyplot(fig1)
    st.download_button(
        label="⬇️ Download Grafik Lingkaran Mohr (PNG)",
        data=fig_to_bytes(fig1),
        file_name="lingkaran_mohr.png",
        mime="image/png",
    )
    plt.close(fig1)


# ==============================================================================
# TAB 2: UJI TRIA
