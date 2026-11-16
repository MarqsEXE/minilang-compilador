# Compilador-Intérprete MiniLang

Projeto final da disciplina **Linguagens Formais e Compiladores** (Cód. 125.31 — Turma GP0029V) do curso de **Ciência da Computação** da **Universidade Tiradentes (UNIT)**, ministrada pela Prof.ª Layse Santos Souza.

## Integrantes do Trio

1. Lauana de Souza Santos
2. Lucas Ricardo Aragão Azevedo
3. Marques Andrei de Jesus Oliveira

## Ferramenta de IA Generativa Utilizada

- **Ferramenta:** Google Gemini (utilizado como copiloto de desenvolvimento mediante revisão, testes e autoria formal do grupo, conforme registrado em `declaração_IA.md` e `docs/diario_de_bordo.md`).

## Estrutura do Repositório

- `src/`: código-fonte do compilador-intérprete (`lexer.py`, `parser.py`, `ast_nodes.py`, `interpreter.py`).
- `tests/`: suíte de testes automatizados dividida em `validos/` e `invalidos/`.
- `exemplos/`: programas de demonstração (`programa_valido.ml` e `programa_invalido.ml`).
- `docs/`: especificação formal (`gramatica.md`), acompanhamento semanal (`diario_de_bordo.md`), relatório final (`relatorio.pdf`) e vídeo de apresentação (`apresentacao.mp4`).

## Instruções de Execução

### 1. Configurar o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 2. Como Rodar os Testes e Resultado Esperado

No diretório `minilang-compilador/`, execute:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

---

### 3. Como Rodar Toda a Suíte de Testes e Resultado Esperado

No diretório raiz `minilang-compilador-/`, execute:

```bash
pytest -v
```
