# sprint-grupo-laranja-backend

## contexto do projeto
Este projeto busca apoiar o acompanhamento e a fiscalização do transporte público por ônibus na cidade de São Paulo. A aplicação reúne dados sobre a operação dos ônibus e a programação das linhas para gerar informações que ajudem a identificar problemas, comparar períodos e compreender melhor o serviço oferecido.

O backend é responsável por receber, organizar e disponibilizar esses dados para as demais partes da aplicação.

## Fluxo básico da aplicação
1. Coleta de dados: o sistema obtém informações sobre a posição dos ônibus e dados de referência, como linhas e horários programados.
2. Armazenamento: os dados coletados são guardados para formar um histórico da operação e permitir análises posteriores.
3. Organização e análise: o backend relaciona os dados da operação com as informações das linhas e calcula indicadores sobre o serviço.
4. Disponibilização: os dados organizados e os indicadores são enviados à interface da aplicação, que pode apresentá-los em painéis, mapas e consultas.
5. Exportação e consulta: quando disponível, o usuário pode consultar ou baixar informações para apoiar análises e relatórios.

## Objetivo
Oferecer uma base confiável para acompanhar a operação dos ônibus e transformar dados de transporte em informações úteis para cidadãos, pesquisadores e equipes de fiscalização.

## Estrutura proposta para o backend

A estrutura abaixo é uma proposta para orientar a evolução do projeto; as pastas e os arquivos serão criados conforme as funcionalidades forem implementadas.

```text
main.py                 # Criação da aplicação FastAPI e registro das rotas
app/
  api/                  # Rotas e formatos de entrada e saída da API
  services/             # Coleta, organização dos dados e cálculo de indicadores
  integrations/
    olho_vivo/          # Autenticação, requisições e conversão das respostas da API externa
  database/             # Futuramente: conexão, modelos, consultas e migrações do banco
  core/                 # Configurações e leitura das variáveis de ambiente
tests/                  # Testes das rotas, serviços e integrações
```

O fluxo previsto é: serviços solicitam dados à integração Olho Vivo, organizam os resultados e, quando o banco estiver definido, usam a camada de persistência para manter o histórico. As rotas disponibilizam os dados e indicadores ao frontend. Credenciais da API devem vir de variáveis de ambiente. A modelagem do banco ainda será definida.

## Como rodar

Na raiz do backend, crie e ative um ambiente virtual e instale as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do backend com seu token do Olho Vivo:

```env
OLHO_VIVO_TOKEN=seu_token
```

Inicie a API:

```bash
"python3 -m uvicorn main:app --reload"
```

`http://127.0.0.1:8000/posicoes` - consultar as posições dos veículos monitorados pelo Olho Vivo.  
`http://127.0.0.1:8000/docs` - documentação interativa

A aplicação coleta posições a cada 30 segundos e mantém a última resposta em memória. Até a primeira coleta bem-sucedida, `/posicoes` retorna HTTP 503. Execute uma única instância da aplicação para evitar coletas duplicadas.

Também é possível executar a consulta diretamente no terminal:

```bash
python3 -m app.integrations.olho_vivo.cliente_posicoes
```

## padrões de contribuição


### Commits

Use o formato:


`tipo: descrição curta`

Tipos permitidos:

- `feat`: adiciona uma funcionalidade.
- `fix`: corrige um problema.
- `docs`: altera a documentação.
- `refactor`: reorganiza o código sem alterar seu comportamento.
- `test`: adiciona ou altera testes.
- `chore`: realiza tarefas de manutenção ou configuração.

### Branches

Use o formato:

`tipo/descricao-curta`

O tipo deve indicar a natureza da mudança, seguindo os tipos definidos para commits.

### Pull Requests

Cada Pull Request deve tratar de uma mudança coerente e apresentar:

- o que foi alterado;
- o motivo da alteração;
- como verificar o resultado;
- observações relevantes para a revisão.

## Verificação do GTFS

A aplicação consulta o GTFS da SPTrans ao iniciar e novamente a cada hora. O endereço padrão pode ser substituído pela variável `GTFS_URL` no `.env`. A resposta deve ser um ZIP; páginas HTML ou erros não são aceitos como GTFS. O conteúdo é lido em partes e comparado por SHA-256, sem salvar o arquivo.

Consulte `GET /gtfs/verificacao` para ver o horário UTC da última verificação bem-sucedida, o hash, se houve alteração em relação à verificação anterior e eventual erro da última tentativa. A primeira verificação retorna `alterado: null`, pois não existe comparação anterior. Antes do primeiro sucesso, a rota retorna HTTP 503. Uma falha preserva o último resultado e é repetida no próximo ciclo.

Os resultados ficam somente em memória, sem banco de dados: ao reiniciar, a primeira verificação estabelece uma nova referência. Execute uma única instância da aplicação para evitar requisições duplicadas. A checagem ocorre enquanto o backend estiver em execução; o acesso à fonte depende de ela disponibilizar o ZIP diretamente.
