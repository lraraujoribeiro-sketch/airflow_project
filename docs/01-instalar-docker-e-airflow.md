# Guia para Totós #1 — Instalar Docker + Airflow localmente

> Objetivo: no fim deste guia tens o Airflow a correr no teu PC, dentro de
> containers Docker, sem teres instalado Python do Airflow na máquina.
> Não precisas de saber nada disto de antemão — vamos passo a passo.

---

## 0. Conceitos em 30 segundos

- **Docker** = uma forma de correr programas "empacotados" (containers) sem
  teres de instalar as suas dependências à mão no teu PC. Cada container é
  como uma mini-máquina isolada.
- **Docker Compose** = um ficheiro (`docker-compose.yaml`) que descreve
  *vários* containers e como eles falam entre si. O Airflow precisa de
  vários serviços (base de dados, scheduler, webserver, worker...), por
  isso usa-se Compose em vez de um único container.
- **Airflow** = a ferramenta que vamos correr dentro desses containers.
  Serve para agendar e orquestrar tarefas (ex: "todos os dias às 6h, corre
  este script Python que vai buscar dados").

Não precisas de instalar Airflow nem Python "a sério" no teu PC — tudo
corre dentro do Docker.

---

## 1. Pré-requisitos

| O que | Como confirmar que já tens |
|---|---|
| Windows 10/11 com WSL2 | `wsl --status` no terminal |
| Docker Desktop | `docker --version` |
| Git | `git --version` |
| Um editor de código (ex: VS Code) | — |

Se `docker --version` já te dá uma resposta (ex: `Docker version 29.x`),
podes saltar para o [passo 3](#3-clonar--criar-o-projeto).

---

## 2. Instalar o Docker Desktop (se ainda não tens)

1. Vai a https://www.docker.com/products/docker-desktop/ e descarrega a
   versão para Windows.
2. Corre o instalador. Quando perguntar, deixa a opção **"Use WSL 2 instead
   of Hyper-V"** marcada — é a recomendada e mais leve.
3. Reinicia o PC se ele pedir.
4. Abre o Docker Desktop. Espera até veres o ícone da baleia 🐳 estável na
   barra de tarefas (sem estar a "carregar").
5. Confirma no terminal (PowerShell ou Git Bash):

   ```bash
   docker --version
   docker compose version
   ```

   Se ambos responderem com um número de versão, está tudo pronto.

> **Problema comum**: se o Docker Desktop disser que o WSL2 não está
> instalado, corre `wsl --install` no PowerShell como administrador,
> reinicia, e abre o Docker Desktop de novo.

---

## 3. Clonar / criar o projeto

Se já tens um repositório Git para isto (como este), começa por:

```bash
git clone <url-do-teu-repo>
cd <nome-da-pasta>
```

Se estás a começar do zero num projeto novo, a estrutura de pastas que o
Airflow espera é:

```
o-teu-projeto/
├── dags/              # aqui vivem as tuas DAGs (os "fluxos" do Airflow)
├── logs/              # logs de execução (gerado automaticamente)
├── plugins/           # plugins custom (podes deixar vazio para começar)
├── config/            # configs extra (podes deixar vazio)
├── .env               # variáveis de ambiente (ex: AIRFLOW_UID)
└── docker-compose.yaml
```

Cria as pastas que faltam:

```bash
mkdir dags logs plugins config
```

E o ficheiro `.env` com:

```
AIRFLOW_UID=50000
```

(Isto evita que os ficheiros criados dentro dos containers fiquem com o
dono "root" no teu disco.)

---

## 4. Ir buscar o `docker-compose.yaml` oficial

A própria equipa do Airflow mantém um ficheiro Compose pronto a usar.
Descarrega-o assim:

```bash
curl -fsSL 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml' -o docker-compose.yaml
```

Isto dá-te um setup completo com:

- **postgres** — a base de dados onde o Airflow guarda o estado (DAGs,
  execuções, utilizadores...)
- **redis** — fila de mensagens usada para distribuir tarefas
- **airflow-scheduler** — decide quando cada tarefa deve correr
- **airflow-dag-processor** — lê os ficheiros da pasta `dags/` e valida-os
- **airflow-apiserver** — a interface web (onde vês tudo no browser)
- **airflow-worker** — quem efetivamente executa as tarefas
- **airflow-triggerer** — trata de tarefas "assíncronas" (sensores, etc.)
- **airflow-init** — um container que só corre uma vez, para preparar tudo

Não precisas de perceber cada um destes em detalhe agora — o Compose
trata de os ligar todos.

---

## 5. Arrancar o Airflow

### 5.1. Inicializar (só precisas de fazer isto uma vez)

```bash
docker compose up airflow-init
```

Isto cria a base de dados e um utilizador admin (`airflow` / `airflow`).
Vais ver muitos logs — o normal é acabar com `exited with code 0`.

### 5.2. Arrancar tudo

```bash
docker compose up -d
```

O `-d` corre em background ("detached"), para não ficares com o terminal
preso. Isto demora entre 30s a 2 minutos a ficar tudo saudável, dependendo
do PC.

### 5.3. Confirmar que está tudo bem

```bash
docker compose ps
```

Queres ver a coluna `STATUS` com `healthy` (ou `Up`) em todos os serviços.

---

## 6. Abrir a interface web

Abre o browser em:

```
http://localhost:8080
```

Login por defeito:

- **Utilizador**: `airflow`
- **Password**: `airflow`

Se vires o dashboard do Airflow com uma lista de DAGs (algumas de
exemplo), parabéns — está tudo a funcionar. 🎉

---

## 7. Comandos do dia a dia (chuleta)

| Quero... | Comando |
|---|---|
| Ver o estado dos containers | `docker compose ps` |
| Ver logs de um serviço (ex: scheduler) | `docker compose logs airflow-scheduler --tail 50` |
| Parar tudo (mantém dados) | `docker compose down` |
| Parar tudo e apagar dados (reset total) | `docker compose down -v` |
| Correr um comando `airflow` dentro do container | `docker compose exec airflow-scheduler airflow <comando>` |
| Ver DAGs sem erros de import | `docker compose exec airflow-scheduler airflow dags list-import-errors` |

---

## 8. Erros comuns

- **"port is already allocated" (porta 8080 ocupada)** — outra coisa no
  teu PC já usa a porta 8080. Muda a porta no `docker-compose.yaml`, na
  secção do `airflow-apiserver`, de `"8080:8080"` para, por exemplo,
  `"8081:8080"`, e acede depois a `http://localhost:8081`.
- **Containers ficam sempre "unhealthy"** — corre `docker compose logs` e
  procura a primeira linha com `ERROR` ou `Traceback`. Normalmente é falta
  de memória atribuída ao Docker Desktop (Settings → Resources → aumenta
  a RAM para pelo menos 4GB).
- **A DAG não aparece na lista** — confirma que o ficheiro `.py` está
  mesmo dentro da pasta `dags/` e que não tem erros de sintaxe (ver
  guia seguinte).

---

Próximo passo: [02-criar-primeira-dag.md](02-criar-primeira-dag.md) — como
criar e correr a tua primeira DAG.
