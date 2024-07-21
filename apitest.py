import requests

# Define the API key and endpoint
api_key = 'truK64nJ2-Te-G04wZCf7mqtr4N5HmTon5VYL633jik'
api_url = 'https://api.heliumgeek.com/v0/gateways/1trSusedShTqrkW7HUxv9QtrjadcnnQEmTJFTdBLDkERUV4bb3rXjzeL7QgGS6rFnsqkHwsUVTxodx2ZtKQ4KehaVzfji6jjTKH85JjmdQUAbqakURZJrdDjCnTHkaVae2mh5asCyQnDXvFpty4eKbaupQKgFuZmzVrowuAMjV1T31yZisa5i1eux2RTuMsfyHu6emk87X3BAcHwTd6vKok1SkBGQmPUo7ThJE7qSD5bixMuKXyowzCEeLkYkrhQr1yCsBwmBmnxT5ZydsTkJQdhKvtnyVxh1kSJi59MqAbD6N4DfGzSAqBSNQZSUXKrXoHDuYZ1wL7A2MLizXcEUGqWFdKfBaJ5ekKthRZjLGpWKP/mobile/data/sum?min_time=2024-07-01T00%3A00%3A00.000Z&max_time=2024-07-16T00%3A00%3A00.000Z&bucket=day'

# Set up headers
headers = {
    'x-api-key': api_key
}

# Make the request
response = requests.get(api_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    print("API key is working. Here is the response:")
    print(response.json())
else:
    print(f"Failed to authenticate API key. Status code: {response.status_code}")
    print(response.text)
