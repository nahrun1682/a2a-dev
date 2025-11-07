# Project Name

## 概要  
本プロジェクトは Agent Development Kit(ADK) を用いて、AIエージェント／マルチエージェント・ワークフローを構築するための基盤となるものです。  
モデルアゴニスティックかつデプロイ環境を問わず使用できるよう設計されております。:contentReference[oaicite:2]{index=2}

## 前提条件  

## 導入手順  

### 1. 仮想環境の作成  
```bash
python -m venv .venv  
# Linux／macOS
source .venv/bin/activate  
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1  
```
### スタート
```bash
(a2a-dev) root:~/work/a2a-dev$ adk run src/test_agent  

#web
#プロジェクト直下で
(a2a-dev) root:~/work/a2a-dev$ adk web src/ --port 8000


```
## 📚 公式リソース・出典一覧（Agent Development Kit / ADK）

以下は Google 提供の Agent Development Kit (ADK) に関する  
公式ドキュメントおよび開発者向け参考資料です。

---

### 🧭 1. 公式ドキュメント（概要・導入・構成）
- **Agent Development Kit (ADK) — Official Docs**  
  👉 [https://google.github.io/adk-docs/](https://google.github.io/adk-docs/?utm_source=chatgpt.com)

---

### ⚙️ 2. API リファレンス（Python／Java／CLI 仕様）
- **ADK API Reference**  
  👉 [https://google.github.io/adk-docs/api-reference/](https://google.github.io/adk-docs/api-reference/?utm_source=chatgpt.com)

---

### 🚀 3. クイックスタートガイド
- **Get Started with ADK (Quickstart for Python / Java)**  
  👉 [https://google.github.io/adk-docs/get-started/quickstart/](https://google.github.io/adk-docs/get-started/quickstart/?utm_source=chatgpt.com)

---

### 🧩 4. 開発ブログ・事例紹介
- **Google Developers Blog — Easy Multi-Agent Application Development with ADK**  
  👉 [https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/](https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/?utm_source=chatgpt.com)

---

### 💻 5. GitHub リポジトリ（公式サンプル・コードベース）
- **Google / adk-docs (GitHub)**  
  👉 [https://github.com/google/adk-docs](https://github.com/google/adk-docs?utm_source=chatgpt.com)

---

> 🪶 *出典：すべて Google 公式公開情報（2025年11月時点）。  
> ドキュメントおよびリンク先は [Google Open Source](https://opensource.google/)  
> 並びに [Google Developers Blog](https://developers.googleblog.com/) より引用。*

