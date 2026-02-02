#!/usr/bin/env bash
set -euo pipefail

# Flow上に input.csv を置いたまま実行し、出力も Flow に作成するためのランナー。
#
# 前提:
# - GOOGLE_API_KEY が環境変数に入っている（または scripts/.env に入っている）
# - Python環境に依存パッケージが入っている:
#   - python-dotenv
#   - langchain-google-genai
#   - langchain-core
#
# 実行例:
#   export GOOGLE_API_KEY="..."
#   bash run_in_flow.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLOW_DATE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

export CSV_IN="${CSV_IN:-${FLOW_DATE_DIR}/input.csv}"
export CSV_OUT="${CSV_OUT:-${SCRIPT_DIR}/output/generated_scripts_2026_02_01.csv}"
export PROMPT_MD="${PROMPT_MD:-${SCRIPT_DIR}/prompt_improved.md}"
export EXAMPLES_YAML="${EXAMPLES_YAML:-${SCRIPT_DIR}/examples.yaml}"

# Cursor sandbox環境ではpyc出力先が弾かれることがあるため、ワークスペース配下に逃がす
export PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-${FLOW_DATE_DIR}/.pycache_tmp}"
mkdir -p "${PYTHONPYCACHEPREFIX}"

# pyenv/.python-version の影響を避けるため、システムPythonを使用
/usr/bin/python3 "${SCRIPT_DIR}/generate_scripts_with_gemini.py"

