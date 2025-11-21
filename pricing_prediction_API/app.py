import uvicorn
import pandas as pd 
import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal, Optional

# Description de l'API
description = """
# GetAround Pricing API 🚗💰

API prédictive pour estimer le prix de location journalier d'un véhicule.

## Fonctionnalités
* **Preview** : Route de test pour vérifier que l'API tourne.
* **Predict** : Envoie les caractéristiques d'une voiture et reçoit une estimation de prix.
"""

# Initialisation de l'application
app = FastAPI(
    title="GetAround Pricing API",
    description=description,
    version="1.0",
    contact={
        "name": "Votre Nom",
        "url": "https://github.com/votre-compte/votre-repo",
    }
)

# --- CHARGEMENT DU MODÈLE ---
# Chargement du pipeline complet (Preprocessing + Modèle)
try:
    model = joblib.load('model.joblib')
    print("✅ Modèle chargé avec succès !")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle : {e}")

# --- DÉFINITION DU FORMAT DES DONNÉES D'ENTRÉE (Pydantic) ---
# Cela permet de valider automatiquement les données envoyées par l'utilisateur
class CarFeatures(BaseModel):
    model_key: str = Field(..., description="Marque du véhicule (ex: Citroën, Renault, BMW)")
    mileage: int = Field(..., gt=0, description="Kilométrage du véhicule")
    engine_power: int = Field(..., gt=0, description="Puissance du moteur (en chevaux)")
    fuel: str = Field(..., description="Type de carburant (diesel, petrol, hybrid, electric)")
    paint_color: str = Field(..., description="Couleur de la voiture")
    car_type: str = Field(..., description="Type de carrosserie (convertible, coupe, estate, hatchback, sedan, subcompact, su, van)")
    private_parking_available: bool = Field(..., description="Disponibilité d'un parking privé")
    has_gps: bool = Field(..., description="GPS intégré")
    has_air_conditioning: bool = Field(..., description="Climatisation")
    automatic_car: bool = Field(..., description="Boîte automatique")
    has_getaround_connect: bool = Field(..., description="Boitier GetAround Connect installé")
    has_speed_regulator: bool = Field(..., description="Régulateur de vitesse")
    winter_tires: bool = Field(..., description="Pneus neige")

# --- ROUTES ---

@app.get("/")
async def index():
    """
    Message de bienvenue pour vérifier que l'API est en ligne.
    """
    return {"message": "Hello ! Bienvenue sur l'API de prédiction de prix GetAround 🚗. Allez sur /docs pour tester !"}

@app.post("/predict", tags=["Machine Learning"])
async def predict(car: CarFeatures):
    """
    Prédiction du prix de location journalier.
    """
    # 1. Conversion des données reçues en DataFrame pandas
    input_data = pd.DataFrame([car.dict()])
    
    # 2. Prédiction via le Pipeline (qui gère le OneHotEncoding et le Scaling tout seul)
    prediction = model.predict(input_data)
    
    # 3. Renvoyer la réponse au format JSON
    return {
        "prediction": round(prediction[0], 2)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)