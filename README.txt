============================================================
  SYSTUR SCRAPPER - Guia rapido de uso
============================================================

O QUE ESTE PROGRAMA FAZ
  Le uma lista de codigos de pessoa de um Excel, consulta cada
  um no sistema SYSTUR (systur.cvc.com.br) e grava os resultados
  em uma planilha de saida.

------------------------------------------------------------
  REQUISITOS DA MAQUINA
------------------------------------------------------------
  - Microsoft Edge instalado
  - Conexao com a internet
  - Conectado na VPN da CVC (o SYSTUR so abre pela VPN)

------------------------------------------------------------
  PASSO 1 - CONFIGURAR AS CREDENCIAIS
------------------------------------------------------------
  1. Abra a pasta "config".
  2. Abra o arquivo "credenciais.xml" no Bloco de Notas.
  3. Preencha entre as tags o seu usuario e senha do SYSTUR:

       <credenciais>
         <usuario>SEU_USUARIO_AQUI</usuario>
         <senha>SUA_SENHA_AQUI</senha>
       </credenciais>

  4. Salve o arquivo e feche.

  (Opcional) Em "config\config.xml":
     <headless>true</headless>  -> true = sem janela do Edge
                                    false = mostra o Edge na tela
     <limite>0</limite>         -> 0 = processa tudo
                                    N = processa so os N primeiros (teste)

------------------------------------------------------------
  PASSO 2 - CONFERIR O ARQUIVO DE ENTRADA
------------------------------------------------------------
  - Coloque o Excel com os codigos na pasta "entrada".
  - A coluna A deve conter o codigo da pessoa (numerico).
  - Ja vem um Excel de exemplo; substitua pelo seu se precisar.
  - Use apenas UM arquivo .xlsx/.xls na pasta "entrada".

------------------------------------------------------------
  PASSO 3 - EXECUTAR
------------------------------------------------------------
  - De um duplo-clique em "SysTur_Scrapper.exe".
  - Se aparecer aviso de VPN: conecte-se a VPN da CVC e
    pressione ENTER para continuar (ou digite "sair" para
    cancelar).
  - Acompanhe o andamento na janela. O programa pode levar
    bastante tempo dependendo da quantidade de codigos.
  - Nao desligue a maquina durante a execucao (a hibernacao
    fica desativada automaticamente enquanto roda).

------------------------------------------------------------
  PASSO 4 - ONDE FICA O RESULTADO
------------------------------------------------------------
  - Planilha de saida:
       saida\vendedores_<data_hora>.xlsx

  - Log do processamento (uma linha por codigo, abre no Excel):
       logs\processamento_<ddmmaaaa>_<hhMMss>.csv

    Colunas do log:
       Data Processamento ; codigo_pessoa ; nome ; status ; detalhe
    status pode ser: concluido | sem_resultado | erro

------------------------------------------------------------
  OBSERVACOES
------------------------------------------------------------
  - O processamento retoma de onde parou se for interrompido
    (controlado pela pasta "processamento").
  - Cada execucao gera um arquivo de log .csv novo.
  - Em caso de erro, a coluna "detalhe" do log traz a descricao.

============================================================
