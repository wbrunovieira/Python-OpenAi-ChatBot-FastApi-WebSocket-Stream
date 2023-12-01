from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import openai
from openai import OpenAI
from openai import AsyncOpenAI
import boto3
from botocore.exceptions import ClientError


from helpers import carrega
from dotenv import load_dotenv

load_dotenv()

import json
import boto3
from botocore.exceptions import ClientError



app = FastAPI()


def get_secret():

    secret_name = "OPENAI_API_KEY"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    
    # Descriptografa o segredo usando a chave KMS associada
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret

minha_chave_secreta = get_secret()


client = openai.AsyncOpenAI(api_key=minha_chave_secreta)
max_tokens=3600


dados_wb_digital_solutions = carrega('dados_wb_digital_solutions.txt')

async def openai_talk(message: str):
    print("iniciando conversa ...")

    prompt_sistema = """
    Voce e um sistema para responder tudo sobre a empresa WB Digital Solutions.
    Você não deve responder perguntas que não sejam sobre a WB Digital Solutions!
    
    ##Informacoes da WB Digital Solutions:
    [Inclua aqui outras informações relevantes do arquivo]
    
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
    # Aqui você precisa definir o HTML que quer retornar. Exemplo:
    html = "<html><body><h1>Hello, World!</h1></body></html>"
    return HTMLResponse(content=html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
 
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        async for text in openai_talk(message):
            await websocket.send_text(text)
 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000 ,log_level="debug", reload=True)
