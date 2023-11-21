from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import openai
from openai import OpenAI
from openai import AsyncOpenAI
import os
from google.cloud import secretmanager
import asyncio

def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload of the given secret version if it is enabled.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Exemplo de uso
project_id = "assistentesitewb"  # Substitua pelo seu project ID do Google Cloud
secret_id = "OPENAI_API_KEY"  # Substitua pelo nome do seu segredo
version_id = "1"  # Pode ser um número de versão específico ou 'latest'
minha_chave_secreta = access_secret_version(project_id, secret_id, version_id)

# Agora, 'minha_chave_secreta' contém o valor do segredo

from helpers import carrega

from dotenv import load_dotenv

load_dotenv()
app = FastAPI()



# Certifique-se de que a chave da API da OpenAI está definida como uma variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")



client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
max_tokens=3600


dados_wb_digital_solutions = carrega('dados_wb_digital_solutions.txt')

async def openai_talk(message: str):
    print("iniciando conversa ...")

    prompt_sistema = """
    Voce e um sistema para responder tudo sobre a empresa WB Digital Solutions.
    Você não deve responder perguntas que não sejam sobre a WB Digital Solutions!
    
    ##Informacoes da WB Digital Solutions:
    [Inclua aqui outras informações relevantes do arquivo]
    {dados_wb_digital_solutions}
    """
    
    prompt_usuario = f"{prompt_sistema} {dados_wb_digital_solutions} {message} \nResponda em portugues, seja educado e amigavel."
    
    print("prompt:", prompt_usuario)

    response = await client.chat.completions.create(
        model="gpt-4-1106-preview",
         messages=[
        {
            "role": "user",
            "content": prompt_usuario,
        },
    ],
         temperature=0,
         max_tokens=max_tokens,
         top_p=1,
         frequency_penalty=0,
         presence_penalty=0,
         stream=True,
    )
    

    
    all_content = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            all_content += content
            yield all_content
        
    


@app.get("/")
async def web_app() -> HTMLResponse:
    """
    Web App
    """
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
 
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        async for text in openai_talk(message):
            await websocket.send_text(text)
    

        
        # Aqui você irá implementar a lógica para enviar a mensagem para a OpenAI e receber a resposta
    
   

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.1", port=8000 ,log_level="debug", reload=True)
