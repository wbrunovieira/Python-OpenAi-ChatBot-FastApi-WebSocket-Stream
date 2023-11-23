from google.cloud import secretmanager

def access_secret_version(project_id, secret_id, version_id):
    """
    Acessa a versão especificada de um segredo no Google Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Substitua pelos seus valores
project_id = "assistentesitewb"  # Seu Project ID do Google Cloud
secret_id = "OPENAI_API_KEY"      # O ID do seu segredo
version_id = "1"         # A versão do segredo, por exemplo, '1' ou 'latest'

# Tente acessar o segredo
try:
    secret_value = access_secret_version(project_id, secret_id, version_id)
    print("Valor do Segredo:", secret_value)
except Exception as e:
    print("Ocorreu um erro ao acessar o segredo:", e)
