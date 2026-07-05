# Airflow local (teste pessoal)

Setup local do Apache Airflow com Docker Compose (o template oficial da
Apache), para testar antes de integrar Azure e Databricks.

## Estrutura

- `docker-compose.yaml` — template oficial do Airflow (CeleryExecutor +
  Postgres + Redis).
- `dags/` — DAGs. Tem uma `dummy_test_dag` só para validar o setup.
- `logs/`, `plugins/`, `config/` — pastas montadas nos containers.
- `.env` — `AIRFLOW_UID` (evita ficheiros criados como root nos volumes).

## Como correr

```bash
# 1. Inicializar a base de dados e o utilizador admin (só uma vez)
docker compose up airflow-init

# 2. Arrancar tudo
docker compose up -d

# 3. Ver o estado dos containers
docker compose ps
```

Acede à UI em http://localhost:8080 — user/pass por defeito: `airflow` / `airflow`.

Liga (`unpause`) a `dummy_test_dag` na UI e corre-a manualmente para
confirmar que o `PythonOperator` e o `BashOperator` executam bem.

## Parar / limpar

```bash
docker compose down          # para os containers, mantém os dados
docker compose down -v       # para e apaga também os volumes (reset total)
```

## Próximos passos

- Adicionar `apache-airflow-providers-microsoft-azure` e
  `apache-airflow-providers-databricks` (via `_PIP_ADDITIONAL_REQUIREMENTS`
  no `docker-compose.yaml`, ou melhor, num `Dockerfile` próprio).
- Criar Connections no Airflow (Admin > Connections) para o Azure e o
  Databricks workspace.
- Criar uma DAG que dispare um job no Databricks (`DatabricksRunNowOperator`
  ou `DatabricksSubmitRunOperator`).
