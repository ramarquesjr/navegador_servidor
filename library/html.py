'''
Contem constantes que definem modelos padrão para as páginas do servidor HTTP
'''


HTML_BASE = '''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <html>
         <meta charset="utf-8">
         <head>
          <title>{0}</title>
         </head>
     <body>
        {1}
     <address>Meu webserver (sem versão)</address>
     </body>
    </html>
    '''

HTML_INDEX = '''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <html>
         <meta charset="utf-8">
         <head>
          <title>{0}</title>
         </head>
     <body>
       <h1> Índice de {1} </h1>
       <table>
        <tr>
            <th><a href="?C=N;O=D">Type</a></th>
            <th><a href="?C=N;O=D">Name</a></th>
            <th><a href="?C=M;O=A">Last modified</a></th>
            <th><a href="?C=S;O=A">Size</a></th>
            <th><a href="?C=D;O=A">Description</a></th>
        </tr>
        <tr><th colspan="5"><hr></th></tr>
        {2}
        <tr><th colspan="5"><hr></th></tr>
       </table>
     <address>Meu webserver (sem versão)</address>
     </body>
    </html>
             '''
