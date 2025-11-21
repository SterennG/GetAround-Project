import streamlit as st
import requests
import json

# Configuration de la page
st.set_page_config(
    page_title="GetAround Predictor",
    page_icon="💸",
    layout="centered"
)

st.title("💸 Estimez le prix de location de votre voiture")

st.markdown("""
Remplissez les caractéristiques du véhicule ci-dessous pour obtenir une estimation du prix de location journalier.
""")

# --- FORMULAIRE DE SAISIE ---
with st.form("predict_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        model_key = st.selectbox("Marque", ["Citroën", "Renault", "BMW", "Peugeot", "Audi", "Nissan", "Mercedes-Benz", "Volkswagen", "Toyota", "SEAT"])
        mileage = st.number_input("Kilométrage", min_value=0, step=1000, value=100000)
        engine_power = st.number_input("Puissance moteur (chevaux)", min_value=50, step=5, value=120)
        fuel = st.selectbox("Carburant", ["diesel", "petrol", "hybrid", "electric"])
        paint_color = st.selectbox("Couleur", ["black", "grey", "white", "red", "silver", "blue", "beige", "brown", "orange", "green"])
        car_type = st.selectbox("Type de carrosserie", ["estate", "sedan", "suv", "hatchback", "subcompact", "coupe", "convertible", "van"])

    with col2:
        private_parking = st.checkbox("Parking privé disponible")
        gps = st.checkbox("GPS intégré")
        ac = st.checkbox("Climatisation")
        automatic = st.checkbox("Boîte automatique")
        connect = st.checkbox("GetAround Connect")
        speed_reg = st.checkbox("Régulateur de vitesse")
        winter = st.checkbox("Pneus neige")

    submit_btn = st.form_submit_button("Estimer le prix 🚀")

# --- LOGIQUE D'APPEL API ---
if submit_btn:
    # 1. Préparation des données (payload)
    # Attention : les clés doivent être EXACTEMENT les mêmes que dans l'API (pydantic)
    data = {
        "model_key": model_key,
        "mileage": mileage,
        "engine_power": engine_power,
        "fuel": fuel,
        "paint_color": paint_color,
        "car_type": car_type,
        "private_parking_available": private_parking,
        "has_gps": gps,
        "has_air_conditioning": ac,
        "automatic_car": automatic,
        "has_getaround_connect": connect,
        "has_speed_regulator": speed_reg,
        "winter_tires": winter
    }
    
    # 2. Envoi à l'API
    # Pour l'instant, je vise localhost:4000 car Docker tourne sur ma machine
    # Plus tard, je remplacerait ça par l'URL de Render
    api_url = "https://sterenn-getaround-api.hf.space/predict"

    with st.spinner("Calcul du prix en cours..."):
        try:
            response = requests.post(api_url, json=data)
            
            if response.status_code == 200:
                prediction = response.json()["prediction"]
                st.success(f"💰 Prix estimé : **{prediction} € / jour**")
                st.balloons()
            else:
                st.error(f"Erreur API : {response.status_code}")
                st.write(response.text)
                
        except requests.exceptions.ConnectionError:
            st.error("🚨 Impossible de contacter l'API. Vérifiez que votre conteneur Docker tourne bien sur le port 4000 !")