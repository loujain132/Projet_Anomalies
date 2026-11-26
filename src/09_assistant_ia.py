
import os
from dotenv import load_dotenv
from openai import OpenAI

# Charger les variables du fichier .env
load_dotenv()

# Récupérer la clé API
api_key = os.getenv("OPENAI_API_KEY")

if not api_key or api_key == "ta_cle_api":
    raise ValueError("La clé API OpenAI n'est pas configurée.")

# Créer le client OpenAI
client = OpenAI(api_key=api_key)

def demander_ia(question):
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        instructions=(
            "Tu es un assistant spécialisé dans la détection "
            "des anomalies dans les dossiers administratifs. "
            "Réponds en français de manière claire."
        ),
        input=question
    )

    return response.output_text
