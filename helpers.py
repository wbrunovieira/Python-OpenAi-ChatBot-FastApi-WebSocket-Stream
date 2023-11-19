
def carrega(nome_do_arquivo):
    try:
        with open(nome_do_arquivo, "r") as arquivo:
            dados = arquivo.read()
            print(dados)
            return dados
    except IOError as e:
        print(f"Erro no carregamento de arquivo: {e}")