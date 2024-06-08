


FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances et installer les dépendances
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers de l'application dans le conteneur
COPY ./app /app

# Exposer le port utilisé par le serveur FastAPI
EXPOSE 8000

# Commande pour démarrer l'application FastAPI
CMD ["uvicorn", "manager.main:app", "--host", "0.0.0.0", "--port", "8000"]
