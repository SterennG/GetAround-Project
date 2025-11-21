# 1. Image de base légère (Python 3.10)
FROM python:3.10-slim

# 2. Définir le dossier de travail dans le conteneur
WORKDIR /app

# 3. Copier les fichiers nécessaires
COPY requirements.txt .

# 4. Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier tout le reste du code (app.py, model.joblib...)
COPY . .

# 6. Exposer le port 4000
EXPOSE 4000

# 7. Lancer l'API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "4000"]