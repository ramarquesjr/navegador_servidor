import datetime
import os
import socket
import sys
import time
from urllib.parse import quote, unquote
from library import (
    magic,
    html
    )

from threading import Thread

LOG = "./servidor.log"
DIRECTORYINDEX = "index.html"


def escrever_log(msg):
    with open(LOG, 'a') as f:
        f.write(msg)


def processa_requisicao(conexao, info_cliente):
    ''' Função que processa a requisição feita pelo navegador e retorno os
        recursos solicitados. A função roda em threads separadas para permitir
        multiplas conexões.

        Args:
            conexao (object): Recebe um objeto socket capaz de receber e enviar
            os dados.
            info_cliente (tuple): Tupla com o par ip/porta que conectou no
            servidor

        Returns:
            O recurso solicitado através do socket conforme a requisição.
    '''
    metodo, recurso, versao = '', '', ''
    req = con.recv(1024).decode()
    earquivo = False
    try:
        metodo, recurso, versao = req.split('\n')[0].split(' ')
        # Suporta apenas o método GET
        if metodo != 'GET':
            raise ValueError()
        atributos = {}
        for l in req.split('\n')[1:]:
            campo = l.split(':')[0].strip()
            valor = ':'.join(l.strip('\r').split(':')[1:]).strip()

            atributos[campo] = valor
        # Sanitizar o recurso solicitado para previnir local file inclusion a
        # partir da url informada
        # https://www.owasp.org/index.php/Testing_for_Local_File_Inclusion
        recurso = unquote(recurso.replace('..', '.').replace('//', '/'))

        # Resposta padrão, sobrecarregado se for encontrado outro recurso
        codigo_http = '200'
        menssagem_http = 'OK'
        resposta = html.HTML_BASE.format('Página Inicial',
                                         '<h1> Esta funcionando ... </h1>')
        tipo_conteudo = 'text/html'

        # Se o recurso igual a / e existe DIRECTORYINDEX, esse arquivo será
        # utilizado como arquivo padrão para exibição
        if recurso == '/' and os.path.exists((diretorio + '/' + DIRECTORYINDEX)):
            fpath = (diretorio + '/' + DIRECTORYINDEX).replace('//', '/')
        else:
            fpath = (diretorio + recurso).replace('//', '/')

        if os.path.isfile(fpath):
            tipo_conteudo = magic.from_file(fpath, mime=True)
            resposta = b''
            earquivo = True
        elif os.path.isdir(fpath):
            if not os.listdir(fpath) and recurso == '/':
                # Se o diretório é vazio, mantém a mensagem padrão
                pass
            else:
                # Senão lista tudo dentro do diretório base
                lista = ''
                # Definição da pasta pai
                anterior = '/'.join(recurso.split('/')[0:-1])
                if anterior == '':
                    anterior = '/'
                dir_pai = '<tr><td colspan=5><a href="'+ anterior + '">Diretório pai</a></td></tr>'
                if fpath.rstrip('/') != diretorio.rstrip('/'):
                        lista += dir_pai
                # Monta a lista de arquivos a ser exibidos
                for i in os.listdir(fpath):
                    frecurso = fpath.rstrip('/') + '/' + i
                    data_modificacao = time.ctime(os.path.getmtime(frecurso))
                    if os.path.isfile(frecurso):
                        bytes = str(os.path.getsize(frecurso))
                        ftype = '-'
                    else:
                        bytes = '-'
                        ftype = 'DIR'
                    lista += '<tr>'
                    lista += '<td>' + ftype +'</td>'
                    urlrecurso = recurso.rstrip('/') + '/' + i
                    lista += '<td><a href="' + quote(urlrecurso) + '">' + i + '</a></td>'
                    lista += '<td>' + data_modificacao + '</td>'
                    lista += '<td>' + bytes + '</td>'
                    lista += '</tr>'

                resposta = html.HTML_INDEX.format('Index of ' + recurso,
                                                  recurso,
                                                  lista)
        else:
            codigo_http = '404'
            menssagem_http = 'NOT FOUND'
            tipo_conteudo = 'text/html'
            resposta = html.HTML_BASE.format(
                        'Recurso não encontrado',
                        '<h1> HTTP 404 - Not found </h1>' +
                        '<p> O recurso solicitado não foi encontrado </p>')

    except ValueError as e:
        codigo_http = '400'
        menssagem_http = 'Bad request'
        tipo_conteudo = 'text/html'
        resposta = html.HTML_BASE.format('Formato de requisição inválido',
                                         '<h1> HTTP 400 - Bad request </h1>')
    finally:
        escrever_log("{0} - {1} - {2} {3} - {4}\n".format(
                        str(info_cliente[0]),
                        datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                        metodo,
                        recurso,
                        codigo_http))
        conexao.send('HTTP/1.1 {0} {1}\nContent-Type: {2}\n\n'.format(
                        codigo_http,
                        menssagem_http,
                        tipo_conteudo).encode())

        # Se a resposta não for binária, codifique para envio
        if isinstance(resposta, str):
            resposta = resposta.encode()
            for i in range(0, len(resposta), 1024):
                try:
                    conexao.send(resposta[i:i + 1024])
                except BrokenPipeError:
                    pass
        elif earquivo:
            with open(fpath, 'rb') as arquivo:
                while True:
                    data = arquivo.read(1024)
                    if not data:
                        break
                    try:
                        conexao.send(data)
                    except BrokenPipeError:
                        pass
        # Franciona o envio da resposta em blocos de 1024 bytes
        conexao.close()


if __name__ == '__main__':
    # Obtém a porta e o diretório por linha de comando
    try:
        porta = int(sys.argv[1])
        diretorio = sys.argv[2]

        if not os.path.isdir(diretorio):
            print('Forneça um diretorio base para este virtual host')
            sys.exit()
    except Exception as e:
        print('Modo de uso: python3 servidor.py porta diretorio')
        sys.exit()
    print('Preparando para receber conexões em {0}:{1}'.format('0.0.0.0', porta))

    while True:
        # Instancia o socket TCP IPv4
        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        # Opção que permite o reuso da porta, sem que seja necessário aguardar
        # a syscall para a do endereço
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            s.bind(('0.0.0.0', porta))
        except PermissionError:
            print('Você não possui permissão para utilizar essa porta.')
            sys.exit()

        s.listen(1)
        con, info_cliente = s.accept()

        print('Conexão efetuada por', ':'.join([str(i) for i in info_cliente]))

        # Processa cada conexão em uma thread diferente
        Thread(target=processa_requisicao, args=(con, info_cliente, )).start()
