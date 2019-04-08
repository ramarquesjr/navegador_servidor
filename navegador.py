#!/usr/bin/env python
# coding: utf-8

import mimetypes
import socket
import ssl
import sys
import re
import os

def processa_url(url: str):
    ''' Função que processa a url, separando dados importantes como protocolo,
        ip, porta e recurso.

        Args:
            url (str): Recebe uma URL para separação e tratamento das
            informações.

        Returns:https://tools.ietf.org/html/rfc2616#section-3.2.2
            consulta (dict): Retorna um dicionário com as seguintes chaves:

            proto (str): Procolo da requisição
            ip (str): Endereço IP do servidor a ser acessado
            porta (int): Porta requerida
            recurso (str): Recurso requerido
            host (str): Define o host requerido (para download em vhosts)
        Note:
            Os formatos possíveis de URL foram retirados de
            https://tools.ietf.org/html/rfc2616#section-3.2.2
        Example url:
            http_URL = "http:" "//" host [ ":" port ] [ abs_path [ "?" query ]]

    '''
    # Regex para validar o formato da URL recebida
    pattern = r'^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+'
    if re.match(pattern, url, 0):

        consulta = {
            'proto': 'http',
            'ip': '',
            'porta': 80,
            'recurso': '/',
            'host': ''
        }

        if 'https://' in url:
            url = url.lstrip('https://')
            consulta['porta'], consulta['proto'] = 443, 'https'
            raise ValueError("Esse método ainda não implementa conexões https")
        elif 'http://' in url:
            url = url.lstrip('http://')

        esquartejado = url.split('/')
        dom = esquartejado[0]
        if ':' in dom:
            consulta['porta'], dom = int(dom.split(':')[-1]), dom.split(':')[0]
        try:
            consulta['ip'] = socket.gethostbyname(dom)
            consulta['host'] = dom
        except Exception as e:
            raise ValueError("Não foi possível converter o nome em endereço")

        if len(esquartejado) > 1:
            consulta['recurso'] = '/' + '/'.join(esquartejado[1:])

        return consulta


if __name__ == '__main__':
    # Obtém a URL por linha de comando
    try:
        if len(sys.argv) < 2:
            raise ValueError("Modo de uso: python3 navegador.py endereco_site")

        URL = sys.argv[1]
        consulta = processa_url(URL)

        if not consulta:
            raise ValueError("Endereço fornecido com padrão incorreto")
    except Exception as e:
        print(e)
        sys.exit()

    print("Consultando o recurso {0} no host {1}, via protocolo {2}, porta {3}"
          .format(consulta["recurso"],
                  consulta["ip"],
                  consulta["proto"],
                  consulta["porta"]))

    requisicao = 'GET {0} HTTP/1.1\r\n'\
                 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) '\
                 'Gecko/20100101 Firefox/65.0\r\n'\
                 'Host: {1}\r\n'\
                 'Connection: Keep-Alive\r\n\r\n'\
                 .format(consulta["recurso"], consulta["host"]).encode()

    # Instancia o socket TCP IPv4
    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)
    try:
        s.settimeout(10)
        s.connect((consulta["ip"], consulta["porta"]))
    except socket.timeout:
        print('\nTimeout: o servidor não respondeu a requisição\n')
        sys.exit()

    # Envia a requisição
    s.send(requisicao)

    dados = b''

    try:
        while True:
            s.settimeout(1)
            resp = s.recv(2048)

            if not len(resp):
                break

            dados += resp
    except Exception as e:
        # Timeout
        pass
    finally:
        s.close()

    # Verifica e define qual o CRLF entregue para a separação do cabeçalho
    # e da parte de dados da resposta (duplo ou não)
    sep = b'\r\n\r\n'
    if sep not in dados:
        sep = b'\n\n'

    cabecalho = dados.split(sep)[0].decode()
    # Copia a partir de todo o conteúdo do cabeçalho somado aos caracteres
    # do separador
    conteudo = dados[len(cabecalho) + len(sep):]

    # A partir do header, coleta os dados mais importantes
    # (content_type, HTTP_CODE)
    content_type = False
    codigo_resposta = False
    texto_codigo_resposta = False

    for l in cabecalho.splitlines():
        if not codigo_resposta:
            partes_cod_resposta = l.strip().split(' ')
            codigo_resposta = partes_cod_resposta[1]
            texto_codigo_resposta = ' '.join(partes_cod_resposta[2:])

        if 'Content-Type' in l:
            content_type = l.split(':')[1].replace(' ', '').split(';')[0]

    try:
        extensao_arquivo = mimetypes.guess_extension(content_type)
    except Exception as e:
        extensao_arquivo = '.html'

    print('\nRetorno\n--------')
    print('Código:', codigo_resposta, '({0})'.format(texto_codigo_resposta))

    if codigo_resposta != '200':
        sys.exit()

    print('Content-Type:', content_type, '({0})'.format(extensao_arquivo))

    if consulta["recurso"] != '/':
        nome_arquivo = consulta["recurso"].split('/')[-1].split('.')[0]
    else:
        nome_arquivo = "index"

    # Salva o conteúdo em modo binário
    try:
        os.mkdir(consulta["host"])
    except Exception as e:
        pass
    with open(consulta["host"] + "/" + nome_arquivo + extensao_arquivo, 'wb') as f:
        f.write(conteudo)

    print('Nome do arquivo salvo:', consulta["host"] + "/" + 
          nome_arquivo + extensao_arquivo)
    print()
