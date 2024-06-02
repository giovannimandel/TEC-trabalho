import glob

def ler_arquivo(nome_arquivo):
    #Lê o conteúdo de um arquivo e retorna como uma lista de linhas."""
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.readlines()
    return conteudo

def altera_zero_para_inicial(linha):
    #Substitui os estados 0 para inicial
    parts = linha.split()
    if len(parts) == 0:
        return linha  
    
    if parts[0] == '0':
        parts[0] = 'inicial'
    
    if parts[-1] == '0':
        parts[-1] = 'inicial'
    
    return ' '.join(parts) + '\n'

def processar_conteudo(conteudo):
    #Substitui os estados 0 para inicial
    return [altera_zero_para_inicial(linha.strip()) for linha in conteudo]

def sipserParaDuplamente(dados):
    # altera 0 para "inicial"
    dados_alterados = processar_conteudo(dados)
    # novas linhas a serem adicionadas
    novas_linhas = [
        "0 * * l marca#\n",
        "marca# _ # r inicial\n",
        "* # # r *\n"
    ]
    # Inserir as novas linhas 
    dados = novas_linhas + dados_alterados[1:]

    
    return dados

def identificar_simbolos_e_estados(dados):
    #Identifica os estados e símbolos do alfabeto adicional
    estados = set()
    simbolos_adicionais = set()
    estados_auxiliares = {'marca&', 'leu0', 'volta#', 'leu1', 'halt-accept'}

    for linha in dados:
        partes = linha.split()
        if len(partes) >= 5:
            estado = partes[0]
            simbolo1 = partes[1]
            simbolo2 = partes[2]
            proximo_estado = partes[4]

            if estado not in estados_auxiliares:
                estados.add(estado)
            if proximo_estado not in estados_auxiliares:
                estados.add(proximo_estado)

            if simbolo1 not in {'0', '1', '_', '*', '#', '&'}:
                simbolos_adicionais.add(simbolo1)
            if simbolo2 not in {'0', '1', '_', '*', '#', '&'}:
                simbolos_adicionais.add(simbolo2)

    return estados, simbolos_adicionais

def gerar_subrotina(estado, simbolos_adicionais):
    #Gera a subrotina de mover tudo pra a direta 
    subrotina = []

    #Adicionando a sub-rotina de movimento com &
    subrotina.append(f';sub-rotina de movimento com & para o estado {estado}\n')
    subrotina.append(f'{estado} & _ r {estado}move&\n')
    subrotina.append(f'{estado}move& _ & l {estado}\n')

    # Move tudo para a direita, lembrando do estado
    subrotina.append(f'\n;move tudo pra direita, lembrando do estado {estado}\n')
    subrotina.append(f'{estado} # # r moveTudo{estado}\n')

    # Estado inicial da sub-rotina
    subrotina.append(f'\n;estado inicial da subrotina\n')
    subrotina.append(f'moveTudo{estado} 1 _ r escreve1Estado{estado}\n')
    subrotina.append(f'moveTudo{estado} 0 _ r escreve0Estado{estado}\n')
    for simbolo in simbolos_adicionais:
        subrotina.append(f'moveTudo{estado} {simbolo} _ r escreve{simbolo}Estado{estado}\n')
    subrotina.append(f'moveTudo{estado} _ _ r escreve_Estado{estado}\n')

    # Estado que escreve1
    subrotina.append(f'\n;estado que escreve1\n')
    subrotina.append(f'escreve1Estado{estado} 1 1 r escreve1Estado{estado}\n')
    subrotina.append(f'escreve1Estado{estado} 0 1 r escreve0Estado{estado}\n')
    for simbolo in simbolos_adicionais:
        subrotina.append(f'escreve1Estado{estado} {simbolo} 1 r escreve{simbolo}Estado{estado}\n')
    subrotina.append(f'escreve1Estado{estado} _ 1 r escreve_Estado{estado}\n')
    subrotina.append(f'escreve1Estado{estado} & 1 r chegou&Estado{estado}\n')

    # Estado que escreve0
    subrotina.append(f'\n;estado que escreve0\n')
    subrotina.append(f'escreve0Estado{estado} 1 0 r escreve1Estado{estado}\n')
    subrotina.append(f'escreve0Estado{estado} 0 0 r escreve0Estado{estado}\n')
    for simbolo in simbolos_adicionais:
        subrotina.append(f'escreve0Estado{estado} {simbolo} 0 r escreve{simbolo}Estado{estado}\n')
    subrotina.append(f'escreve0Estado{estado} _ 0 r escreve_Estado{estado}\n')
    subrotina.append(f'escreve0Estado{estado} & 0 r chegou&Estado{estado}\n')

    # Estados que escrevem símbolos adicionais
    for simbolo in simbolos_adicionais:
        subrotina.append(f'\n;estado que escreve{simbolo}\n')
        subrotina.append(f'escreve{simbolo}Estado{estado} 1 {simbolo} r escreve1Estado{estado}\n')
        subrotina.append(f'escreve{simbolo}Estado{estado} 0 {simbolo} r escreve0Estado{estado}\n')
        for s in simbolos_adicionais:
            subrotina.append(f'escreve{simbolo}Estado{estado} {s} {simbolo} r escreve{s}Estado{estado}\n')
        subrotina.append(f'escreve{simbolo}Estado{estado} _ {simbolo} r escreve_Estado{estado}\n')
        subrotina.append(f'escreve{simbolo}Estado{estado} & {simbolo} r chegou&Estado{estado}\n')

    # Estado que escreve_
    subrotina.append(f'\n;estado que escreve_\n')
    subrotina.append(f'escreve_Estado{estado} 1 _ r escreve1Estado{estado}\n')
    subrotina.append(f'escreve_Estado{estado} 0 _ r escreve0Estado{estado}\n')
    for simbolo in simbolos_adicionais:
        subrotina.append(f'escreve_Estado{estado} {simbolo} _ r escreve{simbolo}Estado{estado}\n')
    subrotina.append(f'escreve_Estado{estado} _ _ r escreve_Estado{estado}\n')
    subrotina.append(f'escreve_Estado{estado} & _ r chegou&Estado{estado}\n')

    # Quando chegou&, volta pro início da fita
    subrotina.append(f'\n;quando chegou&, volta pro inicio da fita\n')
    subrotina.append(f'chegou&Estado{estado} * & l voltaInicio{estado}\n')
    subrotina.append(f'voltaInicio{estado} 1 1 l voltaInicio{estado}\n')
    subrotina.append(f'voltaInicio{estado} 0 0 l voltaInicio{estado}\n')
    for simbolo in simbolos_adicionais:
        subrotina.append(f'voltaInicio{estado} {simbolo} {simbolo} l voltaInicio{estado}\n')
    subrotina.append(f'voltaInicio{estado} _ _ l voltaInicio{estado}\n')
    subrotina.append(f'voltaInicio{estado} # # r {estado}\n')

    return subrotina

def duplamenteParaSipser(dados):
    # altera 0 para "inicial"
    dados_alterados = processar_conteudo(dados)
    # novas linhas a serem adicionadas
    novas_linhas = [
        "0 0 # r leu0\n",
        "0 1 # r leu1\n\n",
        "leu0 0 0 r leu0\n",
        "leu0 1 0 r leu1\n",
        "leu0 _ 0 r marca&\n\n",
        "leu1 0 1 r leu0\n",
        "leu1 1 1 r leu1\n",
        "leu1 _ 1 r marca&\n\n",
        "marca& _ & * volta#\n",
        "volta# * * l volta#\n",
        "volta# # # r inicial\n",
    ]
    # Inserir as novas linhas
    dados = novas_linhas + dados_alterados[1:]

    #Processa os dados pra adicionar as subrotinas

    estados, simbolos_adicionais = identificar_simbolos_e_estados(dados)
    dados_alterados = dados[:]
    for estado in estados:
        subrotina = gerar_subrotina(estado, simbolos_adicionais)
        dados_alterados.extend(subrotina)
    return dados_alterados



def escrever_arquivo(nome_arquivo, dados):
    """Escreve os dados em um arquivo."""
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        arquivo.writelines(dados)

def processar_arquivos():
    # Encontre todos os arquivos com extensão .in no diretório atual
    arquivos_entrada = glob.glob('*.in')
    
    for arquivo_entrada in arquivos_entrada:
        # Ler dados do arquivo de entrada
        conteudo = ler_arquivo(arquivo_entrada)
        
        if conteudo and conteudo[0].strip() == ";S":
            conteudo_alterado = sipserParaDuplamente(conteudo)
        elif conteudo and conteudo[0].strip() == ";I":
            conteudo_alterado = duplamenteParaSipser(conteudo)
        
        # Gerar o nome do arquivo de saída com a extensão .out
        arquivo_saida = arquivo_entrada.replace('.in', '.out')
        
        # Escrever os dados alterados no arquivo de saída
        escrever_arquivo(arquivo_saida, conteudo_alterado)

def main():
    processar_arquivos()


if __name__ == "__main__":
    main()
