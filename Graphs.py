import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ───────────────────────────────────────────────────────────────────────────────
# 1. Page Configuration
# ───────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SGPA & CGPA Dashboard",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("SGPA & CGPA Dashboard")

# ───────────────────────────────────────────────────────────────────────────────
# 2. Sidebar: Number of Semesters and View Selection
# ───────────────────────────────────────────────────────────────────────────────

st.sidebar.header("Configuration")

# Allow user to specify how many semesters to enter (default 8)
num_semesters = st.sidebar.number_input(
    label="Number of Semesters",
    min_value=1,
    value=8,
    step=1,
)

# View selection: Combined, Only SGPA, Only CGPA, Data Table
view_option = st.sidebar.selectbox(
    "Select View",
    options=["Combined", "Only SGPA", "Only CGPA", "Data Table"],
)

# ───────────────────────────────────────────────────────────────────────────────
# 3. Manual Data Entry
# ───────────────────────────────────────────────────────────────────────────────

st.header("Enter SGPA & CGPA Values")

# Create empty lists to hold input values
semesters = []
sgpa_values = []
cgpa_values = []

# Loop over each semester index to create input fields
for i in range(1, int(num_semesters) + 1):
    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.markdown(f"**Sem {i}**")
    with col2:
        sgpa = st.number_input(
            label=f"SGPA (Sem {i})",
            min_value=0.00,
            max_value=10.00,
            value=0.00,
            step=0.01,
            format="%.2f",
            key=f"sgpa_{i}"
        )
    with col3:
        cgpa = st.number_input(
            label=f"CGPA (Sem {i})",
            min_value=0.00,
            max_value=10.00,
            value=0.00,
            step=0.01,
            format="%.2f",
            key=f"cgpa_{i}"
        )
    semesters.append(f"Sem {i}")
    sgpa_values.append(sgpa)
    cgpa_values.append(cgpa)

# Build DataFrame from manual inputs
data = pd.DataFrame({
    "Semester": semesters,
    "SGPA": sgpa_values,
    "CGPA": cgpa_values
})

# ───────────────────────────────────────────────────────────────────────────────
# 4. Data Validation
# ───────────────────────────────────────────────────────────────────────────────

# Check that at least one SGPA or CGPA value is non-zero before plotting
if data[["SGPA", "CGPA"]].sum().sum() == 0:
    st.info("Please enter at least one SGPA or CGPA value to generate charts.")
    st.stop()

# ───────────────────────────────────────────────────────────────────────────────
# 5. Plotting Functions (using Plotly)
# ───────────────────────────────────────────────────────────────────────────────

def plot_combined(df: pd.DataFrame):
    """
    Returns a Plotly figure with SGPA and CGPA overlaid as filled areas and lines.
    """
    fig = go.Figure()

    # SGPA area + line
    fig.add_trace(
        go.Scatter(
            x=df["Semester"],
            y=df["SGPA"],
            name="SGPA",
            mode="lines+markers",
            line=dict(color="royalblue", width=2),
            fill="tozeroy",
            hovertemplate="Semester: %{x}<br>SGPA: %{y:.2f}<extra></extra>",
        )
    )

    # CGPA area + line
    fig.add_trace(
        go.Scatter(
            x=df["Semester"],
            y=df["CGPA"],
            name="CGPA",
            mode="lines+markers",
            line=dict(color="darkorange", width=2),
            fill="tonexty",
            hovertemplate="Semester: %{x}<br>CGPA: %{y:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Combined SGPA & CGPA Progression",
        xaxis_title="Semester",
        yaxis_title="Grade Point",
        yaxis=dict(range=[0, max(df[["SGPA", "CGPA"]].max()) + 1]),
        legend=dict(x=0.02, y=0.98),
        margin=dict(l=40, r=40, t=60, b=40),
        template="seaborn"
    )
    return fig


def plot_single_metric(df: pd.DataFrame, metric: str):
    """
    Returns a Plotly line (or bar) chart for a single metric (SGPA or CGPA).
    """
    # Here we choose a line+marker chart. If you prefer a bar chart, uncomment the bar trace below.
    fig = go.Figure()

    # Line + marker
    fig.add_trace(
        go.Scatter(
            x=df["Semester"],
            y=df[metric],
            name=metric,
            mode="lines+markers",
            line=dict(width=2),
            hovertemplate="Semester: %{x}<br>" + metric + ": %{y:.2f}<extra></extra>",
        )
    )

    # If you want a bar chart instead, comment out the above and uncomment below:
    # fig.add_trace(
    #     go.Bar(
    #         x=df["Semester"],
    #         y=df[metric],
    #         name=metric,
    #         hovertemplate="Semester: %{x}<br>" + metric + ": %{y:.2f}<extra></extra>",
    #     )
    # )

    fig.update_layout(
        title=f"{metric} Progression",
        xaxis_title="Semester",
        yaxis_title=metric,
        yaxis=dict(range=[0, df[metric].max() + 1]),
        margin=dict(l=40, r=40, t=60, b=40),
        template="seaborn"
    )
    return fig


# ───────────────────────────────────────────────────────────────────────────────
# 6. Render Based on View Selection
# ───────────────────────────────────────────────────────────────────────────────

st.header("Visualization")

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
    st.subheader("Data Table")
    st.dataframe(data)

# ───────────────────────────────────────────────────────────────────────────────
# 7. Metrics (Expandable Section)
# ───────────────────────────────────────────────────────────────────────────────

with st.expander("Metrics", expanded=False):
    st.subheader("Key Statistics")

    # Highest SGPA
    idx_max = data["SGPA"].idxmax()
    max_sgpa = data.loc[idx_max, "SGPA"]
    sem_max_sgpa = data.loc[idx_max, "Semester"]

    # Lowest SGPA
    idx_min = data["SGPA"].idxmin()
    min_sgpa = data.loc[idx_min, "SGPA"]
    sem_min_sgpa = data.loc[idx_min, "Semester"]

    # Average SGPA
    avg_sgpa = data["SGPA"].mean()

    # Final CGPA (last non-zero value if CGPA is zero for some)
    nonzero_cgpa = data[data["CGPA"] > 0]
    if not nonzero_cgpa.empty:
        final_cgpa = nonzero_cgpa["CGPA"].iloc[-1]
        sem_final_cgpa = nonzero_cgpa["Semester"].iloc[-1]
    else:
        final_cgpa = 0.0
        sem_final_cgpa = "N/A"

    st.write(f"• Highest SGPA: {max_sgpa:.2f} (in {sem_max_sgpa})")
    st.write(f"• Lowest SGPA: {min_sgpa:.2f} (in {sem_min_sgpa})")
    st.write(f"• Average SGPA: {avg_sgpa:.2f}")
    st.write(f"• Final CGPA: {final_cgpa:.2f} (as of {sem_final_cgpa})")

# ───────────────────────────────────────────────────────────────────────────────
# 8. Footer / Deployment Note
# ───────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.write("Save this script as `app.py` and run with:")
st.code("streamlit run app.py")
