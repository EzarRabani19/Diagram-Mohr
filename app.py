import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# Konfigurasi Halaman (Muncul sebagai judul tab browser & link preview WhatsApp)
st.set_page_config(
    page_title="Diagram Mohr & Kriteria Keruntuhan", page_icon="🪨", layout="wide"
)

st.title("🪨 Diagram Mohr & Kriteria Keruntuhan Batuan")
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
    txy = st.number_input("Tegangan Geser, τxy (kN/m²)", value=34.1, step=1.0)
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

    ax.scatter([sigma_avg], [0], color="black", zorder=5)
    ax.text(
        sigma_avg,
        -R * 0.1,
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
    ax.set_xlim(min(0, sigma_3_prin - 15), sigma_1_prin + 22)
    ax.set_ylim(-R - 15, R + 15)
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
# TAB 2: UJI TRIAKSIAL (MOHR-COULOMB & HOEK-BROWN)
# ==============================================================================
with tab2:
  st.subheader("Kriteria Keruntuhan Mohr-Coulomb & Hoek-Brown (Uji Triaksial)")

  col_data2, col_res2 = st.columns([1, 2], gap="large")

  with col_data2:
    st.markdown("#### Tabel Data Uji Triaksial")
    st.caption(
        "Klik sel untuk mengubah angka, klik tombol **+** di bawah tabel untuk"
        " menambah baris, atau centang baris di kiri lalu tekan ikon tong"
        " sampah untuk menghapus."
    )

    default_data = pd.DataFrame({
        "σ3f (MPa)": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "σ1f (MPa)": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    })

    edited_df = st.data_editor(
        default_data,
        num_rows="dynamic",
        use_container_width=True,
        key="triaxial_editor",
    )

    s_val = st.number_input(
        "Parameter Batuan Utuh Hoek-Brown (s)",
        value=0.0,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        help="Untuk sampel core batuan utuh (intact rock), nilai default s = 1.0",
    )

  with col_res2:
    clean_df = edited_df.dropna(subset=["σ3f (MPa)", "σ1f (MPa)"])

    if len(clean_df) < 2:
      st.warning(
          "Masukkan minimal 2 titik data uji triaksial yang valid untuk"
          " menghitung regresi linear."
      )
    else:
      s3 = clean_df["σ3f (MPa)"].to_numpy(dtype=float)
      s1 = clean_df["σ1f (MPa)"].to_numpy(dtype=float)

      # --- A. Mohr-Coulomb ---
      m_mc, b_mc = np.polyfit(s3, s1, 1)
      s1_pred = m_mc * s3 + b_mc
      r2_mc = 1 - (
          np.sum((s1 - s1_pred) ** 2) / np.sum((s1 - np.mean(s1)) ** 2)
      )

      sin_phi = (m_mc - 1.0) / (m_mc + 1.0)
      sin_phi_clipped = np.clip(sin_phi, -0.9999, 0.9999)
      phi_deg = np.degrees(np.arcsin(sin_phi_clipped))
      cohesion_c = b_mc / (2.0 * np.sqrt(max(m_mc, 1e-9)))

      # --- B. Hoek-Brown ---
      y_hb = (s1 - s3) ** 2
      m_hb_slope, b_hb_intercept = np.polyfit(s3, y_hb, 1)
      y_hb_pred = m_hb_slope * s3 + b_hb_intercept
      r2_hb = 1 - (
          np.sum((y_hb - y_hb_pred) ** 2)
          / np.sum((y_hb - np.mean(y_hb)) ** 2)
      )

      if b_hb_intercept <= 0 or s_val <= 0:
        st.error(
            "Intercept regresi Hoek-Brown bernilai negatif/nol sehingga akar"
            " kuadrat σci tidak terdefinisi. Periksa kembali data input."
        )
      else:
        sigma_ci = np.sqrt(b_hb_intercept / s_val)
        mi = m_hb_slope / sigma_ci
        sigma_t = 0.5 * sigma_ci * (np.sqrt(mi**2 + 4 * s_val) - mi)

        res_c1, res_c2 = st.columns(2)
        with res_c1:
          st.markdown("##### 1. Kriteria Mohr-Coulomb")
          st.info(
              f"**Persamaan:** `σ1f = {m_mc:.4f} σ3f + {b_mc:.4f}`\n\n"
              f"**Koefisien Determinasi (R²):** `{r2_mc:.4f}`\n\n"
              f"- **Sudut Geser Dalam (φ):** `{phi_deg:.3f}°`\n"
              f"- **Kohesi (c):** `{cohesion_c:.3f} MPa`"
          )

        with res_c2:
          st.markdown("##### 2. Kriteria Hoek-Brown")
          st.success(
              f"**Persamaan:** `(σ1f - σ3f)² = {m_hb_slope:.4f} σ3f +"
              f" {b_hb_intercept:.4f}`\n\n"
              f"**Koefisien Determinasi (R²):** `{r2_hb:.4f}`\n\n"
              f"- **Kuat Tarik (σt):** `{sigma_t:.3f} MPa` *(tarik:"
              f" -{sigma_t:.3f} MPa)*\n"
              f"- **UCS (σci):** `{sigma_ci:.3f} MPa` | **mi:** `{mi:.3f}`"
          )

        fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
        x_line = np.linspace(0, max(s3) * 1.05, 100)

        ax1.scatter(
            s3, s1, color="navy", s=55, zorder=5, label="Data Uji Triaksial"
        )
        ax1.plot(
            x_line,
            m_mc * x_line + b_mc,
            "r--",
            linewidth=2,
            label=f"y = {m_mc:.2f}x + {b_mc:.2f}\nR² = {r2_mc:.4f}",
        )
        ax1.set_title(
            "Grafik Mohr-Coulomb: σ1f vs σ3f", fontsize=11.5, fontweight="bold"
        )
        ax1.set_xlabel(
            "Tegangan Terkecil, σ3f (MPa)", fontsize=10, fontweight="bold"
        )
        ax1.set_ylabel(
            "Tegangan Terbesar, σ1f (MPa)", fontsize=10, fontweight="bold"
        )
        ax1.grid(True, linestyle=":", alpha=0.7)
        ax1.legend(loc="upper left", fontsize=9.5)

        ax2.scatter(
            s3,
            y_hb,
            color="darkgreen",
            s=55,
            zorder=5,
            label="Data Transformasi HB",
        )
        ax2.plot(
            x_line,
            m_hb_slope * x_line + b_hb_intercept,
            "darkorange",
            linestyle="--",
            linewidth=2,
            label=(
                f"y = {m_hb_slope:.2f}x + {b_hb_intercept:.2f}\nR² ="
                f" {r2_hb:.4f}"
            ),
        )
        ax2.set_title(
            "Grafik Hoek-Brown: (σ1f - σ3f)² vs σ3f",
            fontsize=11.5,
            fontweight="bold",
        )
        ax2.set_xlabel(
            "Tegangan Terkecil, σ3f (MPa)", fontsize=10, fontweight="bold"
        )
        ax2.set_ylabel("(σ1f - σ3f)² (MPa²)", fontsize=10, fontweight="bold")
        ax2.grid(True, linestyle=":", alpha=0.7)
        ax2.legend(loc="upper left", fontsize=9.5)

        plt.tight_layout()
        st.pyplot(fig2)

        st.download_button(
            label="⬇️ Download Grafik Uji Triaksial (PNG)",
            data=fig_to_bytes(fig2),
            file_name="grafik_triaksial.png",
            mime="image/png",
        )
        plt.close(fig2)
