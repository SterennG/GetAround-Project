# GetAround Analysis & Machine Learning Project

Ce projet vise à optimiser l'activité de location de voitures GetAround à travers deux axes principaux :

- **Analyse des retards** : comprendre l'impact des retards au check-out sur les locations suivantes et proposer un seuil de délai minimum (threshold) optimal.

- **Prédiction de prix** : estimer le prix de location journalier idéal d'un véhicule en fonction de ses caractéristiques via un modèle de Machine Learning.

## Démos en ligne (Déploiement)

Les applications sont déployées et accessibles publiquement :

📊 Dashboard - Analyse des retards : [https://getaround-project-analysis-888.streamlit.app/](https://getaround-project-analysis-888.streamlit.app/)

💰 Interface de Prédiction de prix : [https://getaround-project-prediction-888.streamlit.app/](https://getaround-project-prediction-888.streamlit.app/)

⚙️ API de prédiction (documentation) : [https://sterenn-getaround-api.hf.space/docs](https://sterenn-getaround-api.hf.space/docs)

## Architecture du projet

Le dépôt est organisé en trois modules distincts :

```
GETAROUND/
├── getaround_delay_EDA.ipynb      # Notebook d'analyse exploratoire (EDA) sur les retards
├── getaround_pricing_ML.ipynb     # Notebook d'entraînement du modèle de Machine Learning
│
├── delay_dashboard_streamlit/     # 1. Dashboard d'analyse
│   ├── streamlit_app.py
│   ├── requirements.txt
│   └── get_around_delay_analysis.xlsx
│
├── pricing_prediction_API/        # 2. API de prédiction (FastAPI + Docker)
│   ├── app.py
│   ├── Dockerfile
│   ├── model.joblib               # Modèle entraîné
│   └── requirements.txt
│
└── pricing_prediction_streamlit/  # 3. Interface utilisateur pour la prédiction
    ├── streamlit_app.py
    └── requirements.txt
```

## Installation & Lancement local

Si vous souhaitez cloner et exécuter ce projet sur votre machine :

***1. Prérequis***

- Python 3.10 ou supérieur

- Docker Desktop (optionnel, pour tester l'API en conteneur)

***2. Installation***

Clonez le dépôt et installez les dépendances :

```
git clone [https://github.com/SterennG/GetAround-Project](https://github.com/SterennG/GetAround-Project)
cd GetAround-Project

# Création de l'environnement virtuel (Windows)
py -m venv venv
.\venv\Scripts\Activate.ps1

# Installation des librairies
pip install -r delay_dashboard_streamlit/requirements.txt
pip install -r pricing_prediction_API/requirements.txt
pip install -r pricing_prediction_streamlit/requirements.txt
```

***3. Lancer le Dashboard (Analyse des retards)***

```
streamlit run delay_dashboard_streamlit/streamlit_app.py
```

***4. Lancer l'API et l'interface de prédiction***

Vous devez d'abord lancer l'API, puis l'interface.

Option A : API sans Docker
```
# Terminal 1 : Lancer l'API
cd pricing_prediction_API
uvicorn app:app --reload --port 4000

# Terminal 2 : Lancer Streamlit
streamlit run pricing_prediction_streamlit/streamlit_app.py
```

Option B : API avec Docker
```
# Construire et lancer le conteneur
cd pricing_prediction_API
docker build -t getaround-api .
docker run -it -p 4000:4000 getaround-api

# Dans un autre terminal, lancer Streamlit
streamlit run pricing_prediction_streamlit/streamlit_app.py
```

## Détails Techniques

***Partie 1 : Analyse des retards (Delay Analysis)***

- Données : Données Excel fournies par GetAround (get_around_delay_analysis.xlsx).

- Objectif : Simuler l'impact de l'introduction d'un délai minimum entre deux locations.

- Résultat : Le dashboard permet de visualiser le compromis entre la perte de revenus (locations annulées) et la réduction des frictions (retards évités).

***Partie 2 : Prédiction de Prix (Pricing Optimization)***

- Données : get_around_pricing_project.csv.

- Preprocessing :

    - Nettoyage des outliers (kilométrage excessif, prix aberrants).

    - Encodage des variables catégorielles (OneHotEncoder).

    - Standardisation des variables numériques (StandardScaler).

- Modèle : Random Forest Regressor (Sélectionné via GridSearchCV pour ses meilleures performances R² vs Ridge/Lasso).

- Déploiement : API FastAPI conteneurisée avec Docker, hébergée sur Hugging Face Spaces.
