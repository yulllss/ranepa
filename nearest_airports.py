import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import pydeck as pdk


df = pd.read_csv("airports.csv", sep='|', encoding='ISO-8859-1')
df.info()

st.set_page_config(page_title="main")


def haversine(coord1, coord2):
    lon1, lat1, lon2, lat2 = map(radians, [coord1[1], coord1[0], coord2[1], coord2[0]])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # радиус Земли в км
    return c * r


st.title("Расстояние между аэропортами")

iata_input = st.text_input("Введите IATA-код аэропорта:")

if iata_input:
    airport = df[df["iata_code"] == iata_input.upper()]
    if airport.empty:
        st.error("Аэропорт не найден.")
    else:
        origin = airport.iloc[0]
        origin_coords = (origin["latitude"], origin["longitude"])

 
        distances = []
        for _, row in df.iterrows():
            if row["iata_code"] != iata_input.upper():
                dest_coords = (row["latitude"], row["longitude"])
                try:
                    distance = haversine(origin_coords, dest_coords)
                except:
                    continue
                distances.append({
                    "iata_code": row["iata_code"],
                    "name": row["name_eng"],
                    "city": row["city_eng"],
                    "country": row["country_rus"],
                    "distance_km": round(distance, 2),
                    "latitude": row["latitude"],
                    "longitude": row["longitude"]
                })

    
        nearest_df = pd.DataFrame(sorted(distances, key=lambda x: x["distance_km"])[:5])

        st.subheader("Ближайшие аэропорты:")
        st.dataframe(nearest_df)

    
        st.subheader("Карта:")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=origin["latitude"],
                longitude=origin["longitude"],
                zoom=3,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=nearest_df,
                    get_position='[longitude, latitude]',
                    get_color='[255, 0, 0, 160]',
                    get_radius=50000,
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    data=pd.DataFrame([{
                        "latitude": origin["latitude"],
                        "longitude": origin["longitude"]
                    }]),
                    get_position='[longitude, latitude]',
                    get_color='[0, 0, 255, 160]',
                    get_radius=70000,
                )
            ]
        ))