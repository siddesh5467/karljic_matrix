import streamlit as st
import pandas as pd
import plotly.express as px

# App title
st.set_page_config(page_title="Kraljic Matrix Generator", layout="wide")
st.title("📊 Kraljic Matrix Analysis Tool")

st.markdown("""
Upload your supplier data to visualize the *Kraljic Matrix*.
Your file should contain at least these columns:
- *Supplier*
- *Profit Impact*
- *Supply Risk*
""")

# File uploader
uploaded_file = st.file_uploader("Upload your supplier data (CSV format)", type=["csv"])

if uploaded_file is not None:
    try:
        # Load data
        df = pd.read_csv(uploaded_file)

        # Check columns
        required_cols = {"Supplier", "Profit Impact", "Supply Risk"}
        if not required_cols.issubset(df.columns):
            st.error(f"❌ CSV file must contain the following columns: {', '.join(required_cols)}")
        else:
            st.success("✅ Data uploaded successfully!")
            
            # Display dataframe
            with st.expander("🔍 View Uploaded Data"):
                st.dataframe(df)

            # Normalize the values (0–100 scale)
            df["Profit Impact (Scaled)"] = (df["Profit Impact"] - df["Profit Impact"].min()) / \
                                           (df["Profit Impact"].max() - df["Profit Impact"].min()) * 100
            df["Supply Risk (Scaled)"] = (df["Supply Risk"] - df["Supply Risk"].min()) / \
                                         (df["Supply Risk"].max() - df["Supply Risk"].min()) * 100

            # Determine category based on median split
            profit_median = df["Profit Impact (Scaled)"].median()
            risk_median = df["Supply Risk (Scaled)"].median()

            def classify(row):
                if row["Profit Impact (Scaled)"] >= profit_median and row["Supply Risk (Scaled)"] < risk_median:
                    return "Leverage Items"
                elif row["Profit Impact (Scaled)"] >= profit_median and row["Supply Risk (Scaled)"] >= risk_median:
                    return "Strategic Items"
                elif row["Profit Impact (Scaled)"] < profit_median and row["Supply Risk (Scaled)"] >= risk_median:
                    return "Bottleneck Items"
                else:
                    return "Non-Critical Items"

            df["Category"] = df.apply(classify, axis=1)

            # Plot Kraljic Matrix
            fig = px.scatter(
                df,
                x="Supply Risk (Scaled)",
                y="Profit Impact (Scaled)",
                color="Category",
                hover_name="Supplier",
                title="Kraljic Matrix Visualization",
                size_max=20,
                symbol="Category"
            )

            fig.add_vline(x=risk_median, line_dash="dash", line_color="gray")
            fig.add_hline(y=profit_median, line_dash="dash", line_color="gray")

            st.plotly_chart(fig, use_container_width=True)

            # Summary table
            st.markdown("### 📋 Supplier Categorization Summary")
            summary = df.groupby("Category")["Supplier"].count().reset_index()
            summary.columns = ["Category", "Number of Suppliers"]
            st.dataframe(summary)

    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("⬆ Please upload a CSV file to get started.")
