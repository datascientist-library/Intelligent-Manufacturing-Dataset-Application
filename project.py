import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import io


st.title("Intelligent Manufacturing Dataset Analysis")
st.text("The Intelligent Manufacturing Dataset for Predictive Optimization is a dataset designed for research in smart manufacturing, AI-driven process optimization, and predictive maintenance. It simulates real-time sensor data from industrial machines, incorporating 6G network slicing for enhanced communication and resource allocation.")

file = st.file_uploader("Upload your Dataset", type = ["csv"])


if file:
    df = pd.read_csv(file)
    st.subheader("Data Preview")
    st.dataframe(df)

if file:
    st.subheader("Data Summary")
    st.write(df.describe())

# Separating date and time
if file:
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Year"] = df["Timestamp"].dt.year
    df["Month"] = df["Timestamp"].dt.month
    df["Day"] = df["Timestamp"].dt.day
    df["Time"] = df["Timestamp"].dt.time
    df['Month'] = df['Month'].map({1: 'Jan', 2: 'Feb', 3: 'Mar'})


# ANALYSIS
#SIDEBAR FILTERS
if file:
    st.sidebar.header("Filters")
    efficiency_filter = st.sidebar.multiselect("Select Efficiency", df["Efficiency_Status"].unique(), default = df["Efficiency_Status"].unique())
    month_filter = st.sidebar.multiselect("Select Month", df["Month"].unique(), default = df["Month"].unique())
    operation_filter = st.sidebar.multiselect("Select Operation Mode", df["Operation_Mode"].unique(), default = df["Operation_Mode"].unique())

# FILTERED DATA
if file:
    filtered_df = df[df["Efficiency_Status"].isin(efficiency_filter) & df["Month"].isin(month_filter) & df["Operation_Mode"].isin(operation_filter)]

# KPI Section
if file:
    st.title("ANALYSIS DASHBOARD")

    total_machines = filtered_df["Machine_ID"].count()
    avg_production = filtered_df["Production_Speed_units_per_hr"].mean()
    avg_error = filtered_df["Error_Rate_%"].mean()

    avg_temp = filtered_df["Temperature_C"].mean()
    avg_qc_defect = filtered_df["Quality_Control_Defect_Rate_%"].mean()
    avg_consumption = filtered_df["Power_Consumption_kW"].mean()

    avg_vibration = filtered_df["Vibration_Hz"].mean()
    high_risk_machines = len([i for i in filtered_df['Predictive_Maintenance_Score'] if i < 0.4])
    efficiency = (len([i for i in filtered_df['Operation_Mode'] if i == "Active"])/filtered_df["Operation_Mode"].count())


    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL MACHINES", f"{total_machines}")
    col2.metric("AVG. PRODUCTION SPEED PER HOUR", f"{avg_production:.2f}")
    col3.metric("AVG. ERROR RATE (%)", f"{avg_error:.2f}{" %"}")

    col4, col5, col6 = st.columns(3)
    col4.metric("AVG. TEMPERATURE (°C)", f"{avg_temp:.2f}{'°C'}")
    col5.metric("QUALITY CONTROL DEFECT RATE (%)", f"{avg_qc_defect:.2f}{" %"}")
    col6.metric("AVG. POWER CONSUMPTION (kW)", f"{avg_consumption:.2f}{" kW"}")

    col7, col8, col9 = st.columns(3)
    col7.metric("AVG. VIBRATION (Hz)", f"{avg_vibration:.2f}{" Hz"}")
    col8.metric("MACHINES AT HIGH RISK", f"{high_risk_machines}")
    col9.metric("EFFICIENCY (%)", f"{efficiency:.2f}{" %"}")

    st.markdown("---")

# GRAPHS
if file:
    # 1
    st.subheader("DAYWISE AVG. PRODUCTION SPEED PER HOUR")
    units_time = filtered_df.groupby("Day")["Production_Speed_units_per_hr"].mean().round(2)
    st.bar_chart(units_time)

    #2
    st.subheader("AVG. VIBRATION (Hz) BY MACHINE ID")
    top_vibration = (filtered_df.groupby("Machine_ID")["Vibration_Hz"].mean().sort_values(ascending=False).head(10).reset_index().round(2))
    st.bar_chart(top_vibration, x="Machine_ID", y="Vibration_Hz", color="Vibration_Hz")

    critical_machine = top_vibration.iloc[0]

    st.warning(
        f"Machine **{critical_machine['Machine_ID']}** shows the highest "
        f"average vibration ({critical_machine['Vibration_Hz']:.2f} Hz), "
        f"indicating potential maintenance risk.", icon="⚠️"
    )


    #3
    st.subheader("AVG. ERROR (%)  BY EFFICIENCY STATUS AND MACHINE ID")
    error_df = (filtered_df.groupby(["Efficiency_Status", "Machine_ID"])["Error_Rate_%"].mean().reset_index().round(2))

    top_10_error = (error_df.sort_values("Error_Rate_%", ascending=False).head(10))

    st.bar_chart(top_10_error, x="Machine_ID", y="Error_Rate_%", color="Error_Rate_%")

    worst_machine = top_10_error.iloc[0]

    st.error(
        f"Machine **{worst_machine['Machine_ID']}** under "
        f"**{worst_machine['Efficiency_Status']}** efficiency "
        f"shows the highest average error rate "
        f"({worst_machine['Error_Rate_%']:.2f}%)."
    )


    #4
    st.subheader("TOTAL MACHINES BY EFFICIENCY STATUS")
    op_mode = filtered_df.groupby("Efficiency_Status")["Machine_ID"].count().reset_index()
    st.bar_chart(op_mode, x="Efficiency_Status", y="Machine_ID", color="Efficiency_Status")


    #5
    st.subheader("TOTAL MACHINES BY OPERATION MODE")
    op_mode = filtered_df.groupby("Operation_Mode")["Machine_ID"].count().reset_index()
    st.bar_chart(op_mode, x="Operation_Mode", y="Machine_ID", color="Operation_Mode")

    #6
    st.subheader("AVG. TEMP. (°C) BY EFFICIENCY STATUS AND MACHINE ID")
    error_df = (filtered_df.groupby(["Efficiency_Status", "Machine_ID"])["Temperature_C"].mean().reset_index().round(2))

    top_10_temperature = (error_df.sort_values("Temperature_C", ascending=False).head(10))

    st.bar_chart(top_10_temperature, x="Machine_ID", y="Temperature_C", color="Temperature_C")

    worst_machine = top_10_temperature.iloc[0]

    st.warning(
        f"Machine **{worst_machine['Machine_ID']}** under "
        f"**{worst_machine['Efficiency_Status']}** efficiency "
        f"shows the highest temperature rate "
        f"({worst_machine['Temperature_C']:.2f}°C).", icon="⚠️")
    
# GENERATING PDF
if file:
    def generate_pdf(kpis, chart_buffers):
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(
            "Intelligent Manufacturing Dataset – Analysis Report",
            styles["Title"]
        ))
        elements.append(Spacer(1, 12))

        # KPI Section
        elements.append(Paragraph("<b>KPI Summary</b>", styles["Heading2"]))
        for k, v in kpis.items():
            elements.append(Paragraph(f"{k}: {v}", styles["Normal"]))

        elements.append(Spacer(1, 20))

        # Charts
        elements.append(Paragraph("<b>Analysis Charts</b>", styles["Heading2"]))
        elements.append(Spacer(1, 12))

        for chart in chart_buffers:
            elements.append(Image(chart, width=400, height=250))
            elements.append(Spacer(1, 16))

        pdf.build(elements)
        buffer.seek(0)
        return buffer

    # UNITS TIME
    units_time = (
        filtered_df
        .groupby("Day")["Production_Speed_units_per_hr"]
        .mean()
        .round(2)
    )

    top_vibration_pdf = (
        filtered_df
        .groupby("Machine_ID")["Vibration_Hz"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .round(2)
        .reset_index()
    )

    error_rate_pdf = (
        filtered_df
        .groupby(["Efficiency_Status", "Machine_ID"])["Error_Rate_%"]
        .mean()
        .round(2)
        .reset_index()
    )

    top_10_error_rate = (
        error_rate_pdf
        .sort_values("Error_Rate_%", ascending=False)
        .head(10)
    )

    eff_count = filtered_df.groupby("Efficiency_Status")["Machine_ID"].count()
    op_count = filtered_df.groupby("Operation_Mode")["Machine_ID"].count()


    chart_buffers = []

    # Daywise average production
    fig1, ax1 = plt.subplots()
    units_time.plot(kind="bar", ax=ax1)
    ax1.set_title("Daywise Avg Production Speed")
    ax1.set_ylabel("Units / Hour")

    buf1 = io.BytesIO()
    fig1.savefig(buf1, format="png", bbox_inches="tight")
    buf1.seek(0)
    chart_buffers.append(buf1)

    # Top 10 Machines by Avg Vibration
    fig2, ax2 = plt.subplots()
    ax2.bar(top_vibration["Machine_ID"], top_vibration["Vibration_Hz"])
    ax2.set_title("Top 10 Machines by Avg Vibration")
    ax2.set_ylabel("Vibration (Hz)")
    ax2.tick_params(axis="x", rotation=45)

    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png", bbox_inches="tight")
    buf2.seek(0)
    chart_buffers.append(buf2)

    # Top 10 Error Rate Machines
    fig3, ax3 = plt.subplots()
    ax3.bar(top_10_error["Machine_ID"], top_10_error["Error_Rate_%"])
    ax3.set_title("Top 10 Machines by Error Rate")
    ax3.set_ylabel("Error Rate (%)")
    ax3.tick_params(axis="x", rotation=45)

    buf3 = io.BytesIO()
    fig3.savefig(buf3, format="png", bbox_inches="tight")
    buf3.seek(0)
    chart_buffers.append(buf3)

    # Machines by Efficiency Status
    eff_count = filtered_df.groupby("Efficiency_Status")["Machine_ID"].count()

    fig4, ax4 = plt.subplots()
    eff_count.plot(kind="bar", ax=ax4)
    ax4.set_title("Total Machines by Efficiency Status")
    ax4.set_ylabel("Machine Count")

    buf4 = io.BytesIO()
    fig4.savefig(buf4, format="png", bbox_inches="tight")
    buf4.seek(0)
    chart_buffers.append(buf4)

    # Machines by Operation Mode
    op_count = filtered_df.groupby("Operation_Mode")["Machine_ID"].count()

    fig5, ax5 = plt.subplots()
    op_count.plot(kind="bar", ax=ax5)
    ax5.set_title("Total Machines by Operation Mode")
    ax5.set_ylabel("Machine Count")

    buf5 = io.BytesIO()
    fig5.savefig(buf5, format="png", bbox_inches="tight")
    buf5.seek(0)
    chart_buffers.append(buf5)

    # Avg. Temperature by Machine and Efficiency
    fig6, ax6 = plt.subplots()
    ax6.bar(
        top_10_temperature["Machine_ID"],
        top_10_temperature["Temperature_C"]
    )
    ax6.set_title("Top 10 Machines by Temperature")
    ax6.set_ylabel("Temperature (°C)")
    ax6.tick_params(axis="x", rotation=45)

    buf6 = io.BytesIO()
    fig6.savefig(buf6, format="png", bbox_inches="tight")
    buf6.seek(0)
    chart_buffers.append(buf6)


    # KPI
    kpis = {
        "Total Machines": total_machines,
        "Avg Production Speed": round(avg_production, 2),
        "Avg Error Rate (%)": round(avg_error, 2),
        "Avg Temperature (°C)": round(avg_temp, 2),
        "Avg Vibration (Hz)": round(avg_vibration, 2),
        "High Risk Machines": high_risk_machines,
        "Efficiency (%)": round(efficiency * 100, 2)
    }

    # PDF BUTTON
    pdf = generate_pdf(kpis, chart_buffers)

    st.download_button(
        label="📄 Download Full PDF Report",
        data=pdf,
        file_name="Intelligent_Manufacturing_Report.pdf",
        mime="application/pdf"
    )



