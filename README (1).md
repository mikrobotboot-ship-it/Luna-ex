# 🤖 MikroBot Pro X — LUNA NEXUS

Esta versão usa o HTML do MikroBot Pro X SUPREMO enviado pelo usuário como interface principal e acrescenta uma arquitetura híbrida:

- **HTML/JavaScript:** interface, módulos existentes, PC Console, captura UVC e experiência móvel.
- **Python/FastAPI:** API, memória local SQLite, análise estruturada e orquestração.
- **Agente local:** roda no computador autorizado e executa somente comandos de diagnóstico permitidos.
- **WebSocket:** canal de eventos para estado e telemetria.
- **Evidência:** o sistema separa informação fornecida, teste real e inferência; não inventa teste concluído.
- **Memória:** registra lições/playbooks aprovados pelo usuário; não tenta “aprender tudo” sem controle.

## Rodar no GitHub Codespaces

1. Crie um repositório e envie estes arquivos.
2. Abra o repositório em Codespaces.
3. No terminal:

```bash
pip install -r requirements.txt
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

4. Abra a porta 8000 pelo painel **PORTS** do Codespaces.

## Importante sobre o PC Console

O Codespace é um ambiente remoto. Ele não passa a ter acesso físico ao seu PC, placa HDMI/UVC ou LAN só porque o HTML está hospedado no GitHub. Para diagnóstico físico, o **agent/agent.py** deve rodar no computador autorizado que possui o hardware/rede.

No PC Windows, por exemplo:

```powershell
python agent/agent.py
```

O agente escuta apenas `127.0.0.1:8765` e tem política de comandos limitada. Não coloque senhas ou chaves no HTML.
