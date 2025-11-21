import requests

# L'adresse de l'API (locale pour l'instant)
url = "http://localhost:4000/predict"

# Les données de la voiture à tester (exactement comme dans Swagger)
data = {
  "model_key": "Citroën",
  "mileage": 140000,
  "engine_power": 100,
  "fuel": "diesel",
  "paint_color": "black",
  "car_type": "estate",
  "private_parking_available": True,
  "has_gps": True,
  "has_air_conditioning": True,
  "automatic_car": False,
  "has_getaround_connect": True,
  "has_speed_regulator": True,
  "winter_tires": True
}

# Envoi de la requête POST
print(f"Envoi de la requête à {url}...")
response = requests.post(url, json=data)

# Affichage de la réponse
if response.status_code == 200:
    print("✅ Succès !")
    print("Réponse de l'API :", response.json())
else:
    print("❌ Erreur :", response.status_code)
    print(response.text)