# Guia para Totós #2 — Criar a tua primeira DAG

> Pré-requisito: já tens o Airflow a correr localmente via Docker (ver
> [01-instalar-docker-e-airflow.md](01-instalar-docker-e-airflow.md)).
> Aqui vamos criar, correr e entender uma DAG do zero.

---

## 0. O que é uma DAG (a sério, em português simples)

**DAG** = "Directed Acyclic Graph" (grafo dirigido acíclico), mas esquece
o nome técnico. Pensa numa DAG como:

> Uma receita com passos, onde alguns passos só podem começar depois de
> outros terminarem, e nunca voltas atrás.

Exemplo do dia a dia: "primeiro coze a massa, depois escorre, depois
mistura com o sumo" — não podes misturar antes de escorrer. Isso é uma
DAG: `cozer → escorrer → misturar`.

No Airflow:

- Uma **DAG** é o "fluxo" completo (a receita toda).
- Uma **task** é um passo individual (ex: "cozer a massa").
- Um **operator** é o tipo de trabalho que essa task faz (ex: "correr um
  comando bash", "correr uma função Python", "correr uma query SQL"...).
- As **dependências** (`>>`) dizem qual passo vem antes de qual.

---

## 1. Onde vive uma DAG

Todos os ficheiros `.py` dentro da pasta `dags/` são lidos automaticamente
pelo Airflow. Não precisas de "registar" a DAG em lado nenhum — basta o
ficheiro estar lá.

```
airflow_project/
└── dags/
    └── a_tua_dag.py   👈 crias este ficheiro
```

---

## 2. A estrutura mínima de uma DAG

Cria um ficheiro `dags/minha_primeira_dag.py` com este conteúdo:

```python
from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def diz_ola():
    print("Olá! Esta é a minha primeira DAG.")


with DAG(
    dag_id="minha_primeira_dag",       # nome único, aparece na UI
    description="A minha primeira DAG de teste",
    start_date=datetime(2026, 1, 1),   # a partir de quando pode correr
    schedule=None,                     # None = só corre manualmente
    catchup=False,                     # não tentar "recuperar" datas passadas
    tags=["exemplos"],
) as dag:

    tarefa_ola = PythonOperator(
        task_id="diz_ola",
        python_callable=diz_ola,
    )
```

Explicação linha a linha do que importa:

| Parâmetro | O que faz |
|---|---|
| `dag_id` | O nome que vês na lista de DAGs na UI. Tem de ser único. |
| `start_date` | Data a partir da qual a DAG "existe". Não podes correr antes disto. |
| `schedule` | Quando corre automaticamente. `None` = nunca corre só, tens de a disparar à mão. Também podes pôr `"@daily"`, `"0 6 * * *"` (cron), etc. |
| `catchup` | Se `True`, ao ligar a DAG ele tenta correr todas as execuções "em falta" desde o `start_date`. Como estamos a testar, deixa `False`. |
| `task_id` | Nome único da task dentro da DAG. |
| `python_callable` | A função Python que essa task vai executar. |

---

## 3. Ligar várias tasks (dependências)

Uma DAG com uma task só não mostra o mais interessante: as dependências.
Vamos acrescentar uma segunda task que só corre depois da primeira:

```python
from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator


def diz_ola():
    print("Olá! Esta é a minha primeira DAG.")


with DAG(
    dag_id="minha_primeira_dag",
    description="A minha primeira DAG de teste",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["exemplos"],
) as dag:

    tarefa_ola = PythonOperator(
        task_id="diz_ola",
        python_callable=diz_ola,
    )

    tarefa_data = BashOperator(
        task_id="mostra_data",
        bash_command="echo 'A tarefa anterior já correu. Agora são:' && date",
    )

    # >> significa "depois disto, corre isto"
    tarefa_ola >> tarefa_data
```

`tarefa_ola >> tarefa_data` = "só corre a `tarefa_data` depois da
`tarefa_ola` terminar com sucesso". Se quisesses o contrário, seria
`tarefa_data >> tarefa_ola`.

Podes encadear mais: `tarefa_a >> tarefa_b >> tarefa_c`, ou ramificar:
`tarefa_a >> [tarefa_b, tarefa_c]` (`b` e `c` correm em paralelo, ambas
depois de `a`).

---

## 4. Ver a DAG a aparecer no Airflow

O Airflow lê a pasta `dags/` automaticamente de vez em quando (por
defeito, a cada 30 segundos), mas podes forçar e verificar já:

```bash
# confirmar que não há erros de sintaxe / import
docker compose exec airflow-scheduler airflow dags list-import-errors

# confirmar que a DAG foi detetada
docker compose exec airflow-scheduler airflow dags list | grep minha_primeira_dag
```

Se aparecer na lista sem erros, vai a `http://localhost:8080`, procura
`minha_primeira_dag` e:

1. **Liga o toggle** ao lado do nome (as DAGs novas nascem pausadas —
   enquanto estiver pausada, mesmo que a corras manualmente, ela fica
   "queued" à espera).
2. Clica no botão ▶️ (Trigger DAG) para a correr manualmente.
3. Clica na DAG → vês o "Grid" com o histórico de execuções e o estado de
   cada task (verde = sucesso, vermelho = falhou).

---

## 5. Ver os logs de uma task

Na UI: clica na DAG → clica na execução (a coluna mais recente) → clica
na task → aba **Logs**. É ali que vês o `print()` que puseste na função
Python, ou o output do comando bash.

Via terminal, sem abrir o browser:

```bash
docker compose exec airflow-scheduler airflow tasks states-for-dag-run \
  minha_primeira_dag <dag_run_id>
```

(o `dag_run_id` aparece no output do `airflow dags trigger`, ou na UI).

---

## 6. Erros comuns ao escrever uma DAG

- **A DAG não aparece na lista** → provavelmente há um erro de Python no
  ficheiro. Corre `airflow dags list-import-errors` (passo 4) para ver o
  erro exato.
- **`ModuleNotFoundError`** → estás a tentar importar uma biblioteca que
  não está instalada na imagem do Airflow (ex: `pandas`,
  `databricks-sdk`). Precisas de a adicionar às dependências da imagem
  (isto é o próximo passo quando formos integrar Azure/Databricks).
- **A DAG aparece mas nunca corre** → confirma que não está pausada
  (toggle na UI) e que o `schedule` não está a impedir a próxima execução
  (se for `None`, só corre com trigger manual — é normal).
- **Task fica "queued" para sempre** → ou a DAG está pausada, ou o
  `airflow-worker` não está saudável (`docker compose ps` para
  confirmar).

---

## 7. Resumo — checklist de uma DAG nova

- [ ] Ficheiro `.py` dentro de `dags/`
- [ ] `dag_id` único
- [ ] `start_date` no passado (não no futuro)
- [ ] Pelo menos uma task (`PythonOperator`, `BashOperator`, etc.)
- [ ] Dependências definidas com `>>` (se houver mais que uma task)
- [ ] Sem erros em `airflow dags list-import-errors`
- [ ] DAG destrancada (unpaused) na UI antes de disparar

---

Próximo passo sugerido: adaptar isto para chamar o Databricks (via
`DatabricksRunNowOperator`) ou aceder a recursos do Azure — mas isso é
tema para outro guia, depois de teres os providers instalados.
