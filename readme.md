# OpenFinance Bot
## Installation
1. Clone the repository
    ```bash
    git clone <repository>
    ```
2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
3. Run the bot
    ```bash
    python3 main.py
    ```
## Configuration
1. Create a configuration file
    ```bash
    touch config.json
    ```
2. Create API Key to google sheets (reference: https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account)
3. Config should looks like this
    ```json
    {
      "access_token": "...", // telegram bot access_token
      // google api key
      "type": "service_account",
      "project_id": "...",
      "private_key_id": "...",
      "private_key": "...",
      "client_email": "...",
      "client_id": "...",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "...",
      "users": [
        {
          "user_id": "...",
          "sheet_url": "..."
        },
        {
          "user_id": "...",
          "sheet_url": "..."
        }
      ]
    }
    ```
4. Share your sheets to `client_email` as editor
5. put `sheet_url` to your config file

## Usage
### Income
```
/in <amount> <note>
```

### Outcome
```
/out <amount> <note>
```

### Info
```
/info [Sheet Name|Year in int] [Month in int]
```

### User Info
```
/user_info
```
note: use this to get `user_id`