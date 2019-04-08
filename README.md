# Cliente/servidor Web

Trabalho prático da disciplina _Redes de Computadores_, parte do curso de mestrado em Ciência da Computação da UFSJ. A proposta do trabalho é a codificação de um navegador modo texto e de um servidor web. O alvo é apenas o estudo de uso de socket e de uma pequena parte do protocolo _HTTP_.

**Aluno:** [Ronaldo Alves Marques Júnior](http://lattes.cnpq.br/5354493148453280)
**Professor:** [Dr. Flávio Luiz Schiavoni](http://lattes.cnpq.br/1259591090948385)

## Considerações
Desenvolvidos em Python, os scripts praticamente não possuem dependências. É utilizado a biblioteca _python-magic_ (que consta no arquivo _requeriments.txt_), mas esta foi inserida na pasta library para garantir o funcionamento.

### Navegador
O código realiza o download de um recurso informado. Utiliza-se apenas o método _GET_.
```sh
$ python3 navegador.py endereco_site
```
### Servidor
Responde a métodos _GET_, implementando a listagem de diretórios.
```sh
$ python3 servidor.py porta diretorio
```

## License
Este trabalho é licenciado pela licença [![wtfpl](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-2.png)](http://www.wtfpl.net/about/)