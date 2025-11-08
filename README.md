# ADK Flow Compiler

このリポジトリは、Mermaid で記述したフロー図から Google Agent Development Kit (ADK) 向けの ReAct ワークフロー (`workflow.py`) を自動生成し、`adk run` で実行できるようにするためのサンプル実装です。  
最初に `docs/AgentDevelopmentKit_details.md` を読み、ADK の要件や `root_agent` 公開ルールを確認してください。

## セットアップ

1. **Python / uv**  
   ```bash
   uv python install 3.12
   uv sync
   ```
   `pyproject.toml` には `google-adk`, `jinja2`, `rich`, `pytest`, `typing-extensions` を定義済みです。

2. **API キー** (例: Google AI Studio)  
   `.env` に `GOOGLE_API_KEY` など ADK で必要な値を設定します。

## ワークフロー生成コマンド

1. Mermaid → JSON
   ```bash
   uv run python src/flow_parser.py docs/sample_flow.md > flow.json
   ```
2. JSON → ADK ワークフロー
   ```bash
   uv run python src/compiler.py flow.json src/templates src/generated/workflow.py
   ```
3. ADK 実行 (CLI ラッパー経由でも可)
   ```bash
   uv run python src/run_workflow.py
   # もしくは
   adk run src/generated/workflow.py
   ```

## 生成される workflow.py の概要

- 解析したノード/エッジ情報を `GRAPH_DEFINITION` として保持。
- 各ノードごとに `google.adk.agents.Agent` を生成し、共通の ReAct 指示 (`BASE_REACT_INSTRUCTION`) と MCP モックツール (`tools/call_mcp_tool`) を紐付け。
- ループ対象ノードは `LoopAgent(max_iterations=5)` でラップ。
- 条件分岐ノードは `SelectorAgent` スタブにルート情報を残し、将来 `SelectorAgent` 実装に差し替えやすい構造にしています。
- `SequentialAgent` がトップレベルの `root_agent` としてサブエージェントを順序実行します。

## テスト

```bash
uv run pytest -q
```

- `tests/test_parser.py` : Mermaid 解析で selector / loop を検出できるか。
- `tests/test_compiler.py` : Jinja2 テンプレートが `SequentialAgent` / `LoopAgent` / `SelectorAgent` を含むコードを生成するか。
- `tests/test_workflow.py` : `src/generated/workflow.py` がインポートでき、`root_agent` が `SequentialAgent` になっているか。

## 既知の制限

- 条件分岐は `SelectorAgent` スタブで情報を保持するのみで、実行時のルーティングは最小限です。
- ループ終了条件は LLM の指示ベースであり、`"OK"` を含む応答をアシスタントが返す想定です。
- 複雑な並列実行・確率分岐・外部イベント駆動はサポートしていません。
- 実運用時は `docs/AgentDevelopmentKit_details.md` に沿って `root_agent` の検証 (`adk web src --port 8000` など) を行ってください。
