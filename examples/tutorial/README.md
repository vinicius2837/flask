# Flaskr com MVC + SQLAlchemy + Bootstrap 5

Evolução do tutorial Flaskr (Flask 3.1.3) com arquitetura MVC, persistência via
Flask-SQLAlchemy, uploads de imagens, interface em Bootstrap 5 e um painel
financeiro que roda apenas em memória.

- **Repositório:** `https://github.com/vinicius2837/flask/tree/main/examples/tutorial`
- **Aluno(a):** `Vinicius Marques Costa`

## Como executar
```bash
git clone <link-do-repositorio>
cd flaskr_mvc
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask --app flaskr run --debug
```
Acesse http://127.0.0.1:5000. O banco (`instance/flaskr.sqlite`) é criado
automaticamente na primeira execução. Requer Python 3.10+.

## Estrutura MVC
| Camada | Arquivos |
|---|---|
| **M**odel | `flaskr/models.py` (User, Post, relacionamento 1:N) |
| **C**ontroller | `flaskr/auth.py`, `flaskr/blog.py`, `flaskr/calculos.py`, `flaskr/uploads.py` |
| **V**iew | `flaskr/templates/**` (Bootstrap 5 via CDN) |

## Rotas
`/auth/register` · `/auth/login` · `/auth/logout` · `/` · `/create` ·
`/<id>/update` · `/<id>/delete` · `/painel`

## Observações técnicas
- **Uploads:** `secure_filename` + nome único (uuid) + validação real do conteúdo
  com Pillow; salvos em `flaskr/static/uploads/`. Avatar redimensionado para 256x256.
  Limite de 8 MB por requisição.
- **Painel (`calculos.py`):** cálculo em memória, sem banco. IRPF usa a tabela
  progressiva mensal + redutor da Lei 15.270/2025 (vigente em 2026), de forma
  simplificada (sem INSS/dependentes). 13º proporcional = salário ÷ 12 × meses.
- **Segurança:** a `SECRET_KEY` padrão (`"dev"`) é apenas para desenvolvimento;
  defina outra em `instance/config.py`. Os formulários não possuem proteção CSRF
  (fora do escopo da atividade).

## Capturas de tela
<!-- Adicione prints em docs/ e referencie aqui, ex.: ![Home](docs/home.png) -->
