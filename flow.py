import requests

def chat_with_bot(api_key, endpoint, message, user):
    url = endpoint
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'user': user,
        'inputs': {
            'query': message
        }
    }
    
    response = requests.post(url, json=data, headers=headers, allow_redirects=True)
    
    if response.status_code == 200:
        json_response = response.json()
        data = json_response['data']
        answer = data["outputs"]["text"]
        return answer
    else:
        return f"Error: {response.status_code}, {response.text}"

#必要に応じて変更してね↓
api_key = 'app-BjVa6mlXBd8Si35feuALR5n1'
endpoint = 'http://localhost/v1/workflows/run'

# チャットボットに送るメッセージ
message = "私の名前は何ですか。"

# ユーザー名
user = "1" #なんでもいい

response = chat_with_bot(api_key, endpoint, message, user)
print("Response:", response)
