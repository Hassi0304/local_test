import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from github import Github
import requests

# 環境変数をロードします。
load_dotenv(r"C:\Users\gouzo\OneDrive\デスクトップ\build\.env")

# 環境変数を取得します。
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DIFY_API_KEY3 = os.getenv("DIFY_API_KEY3")
DIFY_ENDPOINT = os.getenv("DIFY_ENDPOINT")

app = Flask(__name__)

# ユーザー情報を取得する関数
def get_user_info(event):
    return event["sender"]["login"]


def chat_with_dify(user):

    # LLM (Dify) にプロンプトを送信
    url = f"{DIFY_ENDPOINT}/chat-messages"
    headers = {

        'Authorization': f'Bearer {DIFY_API_KEY3}',
        'Content-Type': 'application/json'
    }

    data = {
        'query': "進捗、課題、目標などの最新のチームのまとめを出力してください。なお、出力には個人ごとのタスク一覧も出力するようにしてください。直近の進捗報告者は"f"{user}",
        'user': user,
        'inputs': {
        }
    }

    response = requests.post(url, json=data, headers=headers, allow_redirects=True)

    if response.status_code == 200:
        json_response = response.json()
        return json_response.get('answer', "Error: Missing response data")
    else:
        return f"Error: {response.status_code}, {response.text}"


# Webhookのエンドポイントです。
@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.get_json()

    # ユーザー情報を取得
    user = get_user_info(event)

    # アクセストークンを取得 (環境変数から取得)
    access_token = os.getenv(f"{user.upper()}_ACCESS_TOKEN")  # ユーザー名のケースを考慮
    if not access_token:
        return jsonify({"status": "error", "message": "Invalid user or access token"}), 401

    # GitHub API クライアントを作成
    gh = Github(access_token)

    # イベントペイロードからリポジトリ情報とユーザー情報を取得
    repo_owner = event["repository"]["owner"]["login"]
    repo_name = event["repository"]["name"]

    # リポジトリオブジェクトを取得
    try:
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to get repository: {str(e)}"}), 500

    response_message = chat_with_dify(user)
    
    # Issueのタイトルと本文を生成 (例)
    issue_title = "まとめ"
    issue_body = (f"{response_message}")

    # Issueを作成
    try:
        issue = repo.create_issue(title=issue_title, body=issue_body)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to create issue: {str(e)}"}), 500


    return jsonify({"status": "success", "message": "Issue created successfully"})


if __name__ == "__main__":
    app.run(debug=True, port=8080)