import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ───────────────────────────────────────────────────────────────────────────────
# 1. Page Setup
# ───────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SGPA & CGPA Dashboard",
    page_icon="🎓",
    layout="centered",
)

st.title("SGPA & CGPA Dashboard")

# ───────────────────────────────────────────────────────────────────────────────
# 2. Sidebar Controls
# ───────────────────────────────────────────────────────────────────────────────

st.sidebar.header("Configuration")

num_semesters = st.sidebar.number_input(
    label="Number of Semesters",
    min_value=1,
    max_value=20,
    value=8,
    step=1,
)

view_option = st.sidebar.selectbox(
    "Select View",
    options=["Combined", "Only SGPA", "Only CGPA", "Data Table"],
)

# ───────────────────────────────────────────────────────────────────────────────
# 3. Manual Entry Form
# ───────────────────────────────────────────────────────────────────────────────

st.subheader("Enter SGPA & CGPA")

semesters = []
sgpa_values = []
cgpa_values = []

for i in range(1, num_semesters + 1):
    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.markdown(f"**Sem {i}**")
    with col2:
        sgpa = st.number_input(
            label=f"SGPA (Sem {i})",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.01,
            format="%.2f",
            key=f"sgpa_{i}"
        )
    with col3:
        cgpa = st.number_input(
            label=f"CGPA (Sem {i})",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.01,
            format="%.2f",
            key=f"cgpa_{i}"
        )
    semesters.append(f"Sem {i}")
    sgpa_values.append(sgpa)
    cgpa_values.append(cgpa)

data = pd.DataFrame({
    "Semester": semesters,
    "SGPA": sgpa_values,
    "CGPA": cgpa_values
})

# ───────────────────────────────────────────────────────────────────────────────
# 4. Validate Data
# ───────────────────────────────────────────────────────────────────────────────

if data[["SGPA", "CGPA"]].sum().sum() == 0:
    st.info("Please enter at least one SGPA or CGPA value to visualize.")
    st.stop()

# ───────────────────────────────────────────────────────────────────────────────
# 5. Plotting Functions
# ───────────────────────────────────────────────────────────────────────────────

def plot_combined(df: pd.DataFrame):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Semester"],
        y=df["SGPA"],
        name="SGPA",
        mode="lines+markers",
        line=dict(color="royalblue", width=2),
        fill="tozeroy",
        hovertemplate="Semester: %{x}<br>SGPA: %{y:.2f}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=df["Semester"],
        y=df["CGPA"],
        name="CGPA",
        mode="lines+markers",
        line=dict(color="darkorange", width=2),
        fill="tonexty",
        hovertemplate="Semester: %{x}<br>CGPA: %{y:.2f}<extra></extra>"
    ))

    fig.update_layout(
        title="Combined SGPA & CGPA Trend",
        xaxis_title="Semester",
        yaxis_title="Points",
        yaxis=dict(range=[0, max(df[["SGPA", "CGPA"]].max()) + 1]),
        template="seaborn",
        legend=dict(x=0.02, y=0.98)
    )
    return fig


def plot_single_metric(df: pd.DataFrame, metric: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Semester"],
        y=df[metric],
        name=metric,
        mode="lines+markers",
        line=dict(width=2),
        hovertemplate="Semester: %{x}<br>" + metric + ": %{y:.2f}<extra></extra>"
    ))

    fig.update_layout(
        title=f"{metric} Trend",
        xaxis_title="Semester",
        yaxis_title=metric,
        yaxis=dict(range=[0, df[metric].max() + 1]),
        template="seaborn"
    )
    return fig

# ───────────────────────────────────────────────────────────────────────────────
# 6. Display Visualization
# ───────────────────────────────────────────────────────────────────────────────

st.subheader("Visualization")

if view_option == "Combined":
    fig = plot_combined(data)
    st.plotly_chart(fig, use_container_width=True)

elif view_option == "Only SGPA":
    fig = plot_single_metric(data, "SGPA")
    st.plotly_chart(fig, use_container_width=True)

elif view_option == "Only CGPA":
    fig = plot_single_metric(data, "CGPA")
    st.plotly_chart(fig, use_container_width=True)

elif view_option == "Data Table":
    st.dataframe(data)

# ───────────────────────────────────────────────────────────────────────────────
# 7. Metrics Section
# ───────────────────────────────────────────────────────────────────────────────

with st.expander("Metrics Summary"):
    idx_max = data["SGPA"].idxmax()
    max_sgpa = data.loc[idx_max, "SGPA"]
    sem_max_sgpa = data.loc[idx_max, "Semester"]

    idx_min = data["SGPA"].idxmin()
    min_sgpa = data.loc[idx_min, "SGPA"]
    sem_min_sgpa = data.loc[idx_min, "Semester"]

    avg_sgpa = data["SGPA"].mean()

    nonzero_cgpa = data[data["CGPA"] > 0]
    if not nonzero_cgpa.empty:
        final_cgpa = nonzero_cgpa["CGPA"].iloc[-1]
        sem_final_cgpa = nonzero_cgpa["Semester"].iloc[-1]
    else:
        final_cgpa = 0.0
        sem_final_cgpa = "N/A"

    st.write(f"• **Highest SGPA**: {max_sgpa:.2f} ({sem_max_sgpa})")
    st.write(f"• **Lowest SGPA**: {min_sgpa:.2f} ({sem_min_sgpa})")
    st.write(f"• **Average SGPA**: {avg_sgpa:.2f}")
    st.write(f"• **Final CGPA**: {final_cgpa:.2f} (as of {sem_final_cgpa})")

# ───────────────────────────────────────────────────────────────────────────────
# 8. Footer
# ───────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.text("Developed for educational performance visualization.")
