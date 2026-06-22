# Seeban (Protótipo)

Este documento mostra como executar o protótipo localmente.

## 1) Pré-requisitos

- Python 3.10+  
- MySQL Server ativo  
- `pip` disponível

## 2) Configurar banco de dados

O app usa a configuração em `seeban/database/connection.py`:

- host: `127.0.0.4`
- user: `root`
- password: `pass123`
- database: `seeban`

Crie o banco/tabelas no MySQL Workbench 8.0 (ajustando o nome do banco para `seeban`, se necessário):

```sql
CREATE DATABASE IF NOT EXISTS seeban;
USE seeban;
```

Depois execute o script de criação de tabelas (`criar_banco.sql`).

## 3) Instalar dependências

Na raiz do projeto:

```bash
pip install -r requirements.txt
```

## 4) Rodar o protótipo

Ainda na raiz do projeto:

```bash
streamlit run seeban/app.py
```

## 5) Acessar no navegador

Abra o endereço mostrado no terminal (normalmente):

```text
http://localhost:8501
```

## 6) Observações

- O login valida usuário/senha direto na tabela `usuarios`.
- Para testar convites/projetos com mais de um usuário, cadastre contas adicionais na tela de login.
