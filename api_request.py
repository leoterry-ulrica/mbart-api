import requests

base_url = "http://localhost:8000"  # Update with your server's URL

def test_translate_endpoint(source_lang, target_lang, text):
    url = f"{base_url}/v1/lang/translate"
    payload = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "text": text,
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        result = response.json()
        print(f"Translation Successful:\n{result}")
    else:
        print(f"Translation Failed. Status Code: {response.status_code}\nDetails: {response.text}")

# Test Case 1: Translate to English
test_translate_endpoint(source_lang="zh", target_lang="en", text="你好")
# output：Hello

