from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sales & Service Dashboard", page_icon="📊", layout="wide")

DATA = Path(__file__).resolve().parents[2] / "data"


@st.cache_data
def load_data():
    names = ["orders", "customers", "order_items", "products", "shipments", "complaints", "suppliers"]
    tables = {name: pd.read_csv(DATA / f"{name}.csv") for name in names}
    for column in ["order_date", "requested_delivery_date"]:
        tables["orders"][column] = pd.to_datetime(tables["orders"][column], errors="coerce")
    tables["complaints"]["complaint_date"] = pd.to_datetime(tables["complaints"]["complaint_date"], errors="coerce")
    orders = tables["orders"].merge(
        tables["customers"][["customer_id", "customer_segment", "country", "region"]],
        on="customer_id", how="left", validate="many_to_one"
    )
    return tables, orders


tables, orders = load_data()

st.title("Sales & Service Dashboard")
st.caption("Interaktives Beispielprojekt mit Streamlit, Pandas, Plotly und Matplotlib")

st.sidebar.header("Filter")
countries = st.sidebar.multiselect("Länder", sorted(orders["country"].dropna().unique()), default=sorted(orders["country"].dropna().unique()))
segments = st.sidebar.multiselect("Kundensegmente", sorted(orders["customer_segment"].dropna().unique()), default=sorted(orders["customer_segment"].dropna().unique()))
min_date = orders["order_date"].min().date()
max_date = orders["order_date"].max().date()
date_range = st.sidebar.date_input("Bestelldatum", value=(min_date, max_date), min_value=min_date, max_value=max_date)

filtered = orders[orders["country"].isin(countries) & orders["customer_segment"].isin(segments)].copy()
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered = filtered[filtered["order_date"].between(start, end)]

if filtered.empty:
    st.warning("Keine Daten für die ausgewählten Filter vorhanden.")
    st.stop()

order_ids = filtered["order_id"]
items = tables["order_items"][tables["order_items"]["order_id"].isin(order_ids)].copy()
shipments = tables["shipments"][tables["shipments"]["order_id"].isin(order_ids)].copy()
complaints = tables["complaints"][tables["complaints"]["order_id"].isin(order_ids)].copy()

revenue = filtered["order_value"].sum()
order_count = filtered["order_id"].nunique()
average_order = filtered["order_value"].mean()
delay_rate = shipments["delivery_delayed"].mean() if not shipments.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Umsatz", f"{revenue:,.0f} €")
c2.metric("Bestellungen", f"{order_count:,}")
c3.metric("Ø Bestellwert", f"{average_order:,.0f} €")
c4.metric("Verspätete Lieferungen", f"{delay_rate:.1%}")

tab1, tab2, tab3, tab4 = st.tabs(["Überblick", "Produkte", "Service & Logistik", "Daten entdecken"])

with tab1:
    st.subheader("Umsatzentwicklung")
    monthly = filtered.assign(month=filtered["order_date"].dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False)["order_value"].sum()
    fig = px.line(monthly, x="month", y="order_value", markers=True, labels={"month": "Monat", "order_value": "Umsatz (€)"}, template="plotly_white")
    fig.update_traces(line_color="#2563eb", line_width=3)
    st.plotly_chart(fig, width='stretch')

    left, right = st.columns(2)
    with left:
        st.subheader("Umsatz nach Segment")
        segment_data = filtered.groupby("customer_segment", as_index=False)["order_value"].sum()
        fig = px.bar(segment_data, x="customer_segment", y="order_value", color="customer_segment", labels={"customer_segment": "Segment", "order_value": "Umsatz (€)"}, template="plotly_white")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width='stretch')
    with right:
        st.subheader("Bestellstatus")
        status = filtered["status"].value_counts().reset_index()
        status.columns = ["Status", "Anzahl"]
        fig = px.pie(status, names="Status", values="Anzahl", hole=0.55)
        st.plotly_chart(fig, width='stretch')

with tab2:
    st.subheader("Produktkategorien")
    categories = items.groupby("category", as_index=False).agg(umsatz=("line_value", "sum"), menge=("quantity", "sum")).sort_values("umsatz", ascending=False)
    left, right = st.columns(2)
    with left:
        fig = px.bar(categories, x="umsatz", y="category", orientation="h", color="umsatz", labels={"umsatz": "Umsatz (€)", "category": "Kategorie"}, template="plotly_white")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch')
    with right:
        st.markdown("**Matplotlib: verkaufte Stückzahlen**")
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(categories["category"], categories["menge"], color="#0f766e")
        ax.set_ylabel("Stückzahl")
        ax.tick_params(axis="x", rotation=35)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Top-Produkte")
    product_sales = items.groupby("product_id", as_index=False).agg(umsatz=("line_value", "sum"), stueck=("quantity", "sum"))
    product_sales = product_sales.merge(tables["products"][["product_id", "product_name"]], on="product_id", how="left")
    top_n = st.slider("Anzahl Produkte", 5, 20, 10)
    st.dataframe(product_sales.nlargest(top_n, "umsatz")[["product_name", "umsatz", "stueck"]], hide_index=True, width='stretch')

with tab3:
    left, right = st.columns(2)
    with left:
        st.subheader("Lieferverzögerung nach Versanddienst")
        carrier = shipments.groupby("carrier", as_index=False)["delivery_delayed"].mean()
        carrier["delivery_delayed"] *= 100
        fig = px.bar(carrier, x="carrier", y="delivery_delayed", labels={"carrier": "Versanddienst", "delivery_delayed": "Verspätet (%)"}, template="plotly_white")
        st.plotly_chart(fig, width='stretch')
    with right:
        st.subheader("Reklamationsarten")
        if complaints.empty:
            st.info("Keine Reklamationen im gewählten Zeitraum.")
        else:
            complaint_types = complaints["complaint_type"].value_counts()
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.barh(complaint_types.index, complaint_types.values, color="#e58f46")
            ax.set_xlabel("Anzahl")
            ax.invert_yaxis()
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    st.subheader("Lieferungen im Detail")
    st.dataframe(shipments[["shipment_id", "order_id", "carrier", "delivery_status", "delivery_delayed", "delivery_days"]], hide_index=True, width='stretch')

with tab4:
    st.subheader("CSV-Daten erkunden")
    table_name = st.selectbox("Tabelle auswählen", list(tables))
    st.write(f"{len(tables[table_name]):,} Zeilen · {len(tables[table_name].columns)} Spalten")
    st.dataframe(tables[table_name].head(100), width='stretch', hide_index=True)
    st.subheader("Statistische Übersicht")
    st.dataframe(tables[table_name].describe(include="all").fillna(""), width='stretch')
    st.download_button("Gefilterte Bestellungen als CSV herunterladen", data=filtered.to_csv(index=False).encode("utf-8"), file_name="bestellungen_gefiltert.csv", mime="text/csv")
