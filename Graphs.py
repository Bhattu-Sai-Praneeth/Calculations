# app.py

import streamlit as st
import pandas as pd
import altair as alt

# ───────────────────────────────────────────────────────────────────────────────
# 1. Page Configuration
# ───────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SGPA & CGPA Progression Dashboard",
    page_icon="🎓",  # Icon appears in the browser tab
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("SGPA & CGPA Progression Dashboard")
st.markdown(
    """
    This application allows you to visualize your Semester Grade Point Average (SGPA)
    and Cumulative Grade Point Average (CGPA) progression over multiple semesters.
    
    **Features**:
    - Upload your own CSV file (columns: Semester, SGPA, CGPA) or use the sample dataset.
    - Select one of the following views:
      1. Combined (SGPA & CGPA over time)
      2. Only SGPA (line chart)
      3. Only CGPA (line chart)
      4. Data Table (raw values displayed in tabular form)
    - Expand the “Metrics” section to view key statistics (highest SGPA, lowest SGPA, average SGPA, final CGPA).
    
    ---
    **Instructions**:
    1. (Optional) Upload a CSV file using the sidebar.
    2. Choose a view from the “Select View” dropdown in the sidebar.
    3. To run locally: save this file as `app.py`, then execute  
       ```
       streamlit run app.py
       ```
    """
)

# ───────────────────────────────────────────────────────────────────────────────
# 2. Sidebar: Data Upload or Use Sample
# ───────────────────────────────────────────────────────────────────────────────

st.sidebar.header("Data Input")

uploaded_file = st.sidebar.file_uploader(
    label="Upload a CSV file (columns: Semester, SGPA, CGPA)",
    type=["csv"],
)

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        # Ensure required columns exist
        required_cols = {"Semester", "SGPA", "CGPA"}
        if not required_cols.issubset(set(data.columns)):
            st.sidebar.error(
                "Uploaded CSV must contain the columns: 'Semester', 'SGPA', 'CGPA'."
            )
            st.stop()
        # Convert Semester column to string in case it is numeric
        data["Semester"] = data["Semester"].astype(str)
    except Exception as e:
        st.sidebar.error(f"Error reading CSV: {e}")
        st.stop()
else:
    # Default sample dataset (Semesters 1–8)
    sample_dict = {
        "Semester": [
            "Sem 1",
            "Sem 2",
            "Sem 3",
            "Sem 4",
            "Sem 5",
            "Sem 6",
            "Sem 7",
            "Sem 8",
        ],
        "SGPA": [8.35, 8.03, 7.34, 8.29, 7.90, 7.95, 8.70, 8.33],
        "CGPA": [8.35, 8.19, 7.91, 8.01, 7.99, 7.98, 8.10, 8.13],
    }
    data = pd.DataFrame(sample_dict)

# Ensure the DataFrame is sorted by Semester in case user-provided data is out of order
# We will try to sort by the natural ordering of “Semester” strings if they follow the pattern “Sem X”
# Otherwise, keep as-is.
try:
    # Extract integer value from “Sem X”
    data["SemIndex"] = data["Semester"].str.extract(r"(\d+)").astype(int)
    data = data.sort_values(by="SemIndex").drop(columns="SemIndex")
    data = data.reset_index(drop=True)
except Exception:
    # If extraction fails, do not alter original order
    pass

# ───────────────────────────────────────────────────────────────────────────────
# 3. Sidebar: View Selection
# ───────────────────────────────────────────────────────────────────────────────

st.sidebar.header("Chart Options")
view_option = st.sidebar.selectbox(
    "Select View",
    options=["Combined", "Only SGPA", "Only CGPA", "Data Table"],
)

# ───────────────────────────────────────────────────────────────────────────────
# 4. Main Area: Display Based on Selection
# ───────────────────────────────────────────────────────────────────────────────

def plot_combined(df: pd.DataFrame):
    """
    Create an Altair area chart with both SGPA and CGPA curves.
    """
    base = alt.Chart(df).encode(
        x=alt.X("Semester:N", title="Semester")
    )

    area_sgpa = (
        base.transform_fold(
            ["SGPA"], as_=["type", "value"]
        )
        .mark_area(opacity=0.4, interpolate="monotone")
        .encode(
            y=alt.Y("value:Q", title="Grade Point"),
            color=alt.Color("type:N", legend=alt.Legend(title="Metric")),
            tooltip=["Semester", "SGPA", "CGPA"],
        )
    )

    area_cgpa = (
        base.transform_fold(
            ["CGPA"], as_=["type", "value"]
        )
        .mark_area(opacity=0.4, interpolate="monotone")
        .encode(
            y=alt.Y("value:Q"),
            color=alt.Color("type:N", legend=None),
            tooltip=["Semester", "SGPA", "CGPA"],
        )
    )

    line_sgpa = (
        base.mark_line(point=True, size=3)
        .encode(
            y=alt.Y("SGPA:Q"),
            color=alt.value("#1f77b4"),  # Default blue
            tooltip=["Semester", "SGPA"],
        )
    )

    line_cgpa = (
        base.mark_line(point=True, size=3)
        .encode(
            y=alt.Y("CGPA:Q"),
            color=alt.value("#ff7f0e"),  # Default orange
            tooltip=["Semester", "CGPA"],
        )
    )

    combined_chart = (
        alt.layer(area_sgpa, area_cgpa, line_sgpa, line_cgpa)
        .resolve_scale(y="shared")
        .properties(width=700, height=400)
    )
    return combined_chart


def plot_single_metric(df: pd.DataFrame, metric: str):
    """
    Create an Altair line chart for a single metric (either 'SGPA' or 'CGPA').
    """
    chart = (
        alt.Chart(df)
        .mark_line(point=True, size=3, interpolate="monotone")
        .encode(
            x=alt.X("Semester:N", title="Semester"),
            y=alt.Y(f"{metric}:Q", title=f"{metric}"),
            tooltip=["Semester", metric],
        )
        .properties(width=700, height=400)
    )
    return chart


# Display based on the user's selection
if view_option == "Combined":
    st.subheader("Combined SGPA & CGPA Progression")
    combined_chart = plot_combined(data)
    st.altair_chart(combined_chart, use_container_width=True)

elif view_option == "Only SGPA":
    st.subheader("SGPA Progression")
    sgpa_chart = plot_single_metric(data, "SGPA")
    st.altair_chart(sgpa_chart, use_container_width=True)

elif view_option == "Only CGPA":
    st.subheader("CGPA Progression")
    cgpa_chart = plot_single_metric(data, "CGPA")
    st.altair_chart(cgpa_chart, use_container_width=True)

elif view_option == "Data Table":
    st.subheader("Raw Data Table")
    st.dataframe(data[["Semester", "SGPA", "CGPA"]])

# ───────────────────────────────────────────────────────────────────────────────
# 5. Metrics (Optional Expander)
# ───────────────────────────────────────────────────────────────────────────────

with st.expander("📈 Metrics", expanded=False):
    st.markdown("### Key Statistics for SGPA & CGPA")

    # Highest SGPA
    idx_max_sgpa = data["SGPA"].idxmax()
    max_sgpa_value = data.loc[idx_max_sgpa, "SGPA"]
    max_sgpa_sem = data.loc[idx_max_sgpa, "Semester"]

    # Lowest SGPA
    idx_min_sgpa = data["SGPA"].idxmin()
    min_sgpa_value = data.loc[idx_min_sgpa, "SGPA"]
    min_sgpa_sem = data.loc[idx_min_sgpa, "Semester"]

    # Average SGPA
    avg_sgpa_value = data["SGPA"].mean()

    # Final CGPA (last semester in the dataset)
    final_cgpa_value = data["CGPA"].iloc[-1]
    final_cgpa_sem = data["Semester"].iloc[-1]

    st.markdown(
        f"""
        - **Highest SGPA**: {max_sgpa_value:.2f} (in {max_sgpa_sem})  
        - **Lowest SGPA**: {min_sgpa_value:.2f} (in {min_sgpa_sem})  
        - **Average SGPA**: {avg_sgpa_value:.2f}  
        - **Final CGPA**: {final_cgpa_value:.2f} (as of {final_cgpa_sem})
        """
    )

# ───────────────────────────────────────────────────────────────────────────────
# 6. Footer / Deployment Note
# ───────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    """
    **How to Deploy**  
    1. Ensure you have Python 3.7+ and Streamlit installed:  
       ```
       pip install streamlit pandas altair
       ```  
    2. Save this file as `app.py`.  
    3. Run locally:  
       ```
       streamlit run app.py
       ```  
    4. To deploy on Streamlit Cloud (or any other hosting service), connect your GitHub repository containing `app.py`, and follow the provider’s instructions for deployment.
    """
)
