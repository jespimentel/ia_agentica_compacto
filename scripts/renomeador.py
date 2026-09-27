import os
import re
import datetime
import zipfile
import xml.etree.ElementTree as ET

# Caminho para os arquivos .docx
caminho = r"D:\Du\OneDrive - Ministério Público SP\__INTERNAL_SAJ_DOCS"

def extrair_xml_docx(caminho_docx):
    with zipfile.ZipFile(caminho_docx, "r") as docx_zip:
        with docx_zip.open("word/document.xml") as xml_file:
            return xml_file.read().decode("utf-8")

def limpar_tags_xml(xml_string):
    root = ET.fromstring(xml_string)
    texto = ' '.join(root.itertext())
    return texto

def encontrar_primeiro_numero_cnj(texto):
    padrao = r"\d{7}-\d{2}\.\d{4}\.8\.26\.\d{4}"
    resultado = re.search(padrao, texto)
    if resultado:
        return resultado.group(0)

def obter_data_modificacao(caminho_docx):
    data_modificacao = os.path.getmtime(caminho_docx)
    data_modificacao = datetime.datetime.fromtimestamp(data_modificacao)
    data_formatada = data_modificacao.strftime("%Y-%m-%d-%H-%M")     
    return data_formatada

def obter_tipo_peca(xml_limpo):
    """Determina o tipo de peça com base na primeira palavra encontrada no conteúdo do XML limpo."""
    tipo_peca = xml_limpo.upper().split(' ')[0]
    mapeamento = {
        'MANIFESTAÇÃO': 'cota',
        'DECISÃO': 'arq',
        'PROMOÇÃO': 'arq',
        'CONTRARRAZÕES': 'cr',
        'RAZÕES': 'apel',
        'ALEGAÇÕES': 'af',
        'EXCELENTÍSSIMO': 'pet',
    }
    return mapeamento.get(tipo_peca, "etc") 

def obter_dados_adicionais(xml_limpo):
    """Extrai informações adicionais contidas entre duas # no XML limpo."""
    padrao = r"#(.*?)#"
    dados_adicionais = re.search(padrao, xml_limpo)
    if dados_adicionais:
        return dados_adicionais.group(1).strip()
    return ""

def limpeza_nome_arquivo(texto_original):
    """Remove espaços excedentes e substitui travessões por hífens."""
    texto_corrigido = re.sub(r'\s+', ' ', texto_original).strip()
    texto_corrigido = texto_corrigido.replace('–', '-')
    return texto_corrigido

if __name__ == "__main__":
    arquivos = os.listdir(caminho)

    for arquivo in arquivos:
        if arquivo.endswith('.docx'):
            caminho_completo = os.path.join(caminho, arquivo)
            try:
                data_modificacao = obter_data_modificacao(caminho_completo)
                xml_conteudo = extrair_xml_docx(caminho_completo)
                xml_limpo = limpar_tags_xml(xml_conteudo)
                cnj = encontrar_primeiro_numero_cnj(xml_limpo)
                tipo_peca = obter_tipo_peca(xml_limpo)
                dados_adicionais = obter_dados_adicionais(xml_limpo)

                #Renomeando arquivo
                if dados_adicionais:
                    nome_provisorio = f"{caminho}\\{cnj} - {data_modificacao} - {tipo_peca.lower()} - {dados_adicionais.lower()}.docx"
                    novo_nome = limpeza_nome_arquivo(nome_provisorio)
                else:
                    nome_provisorio = f"{caminho}\\{cnj} - {data_modificacao} - {tipo_peca.lower()}.docx"
                    novo_nome = limpeza_nome_arquivo(nome_provisorio)
                    
                os.rename(caminho_completo, novo_nome)
                print(f"{caminho_completo} renomeado para {novo_nome}")
            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")