## Autoposting Bot for Telegram 

 - using Aiogram version 3.5.0
 - using CryptoBot @CryptoBot

[![N|Solid](![image](https://github.com/user-attachments/assets/ae137430-ba6c-431e-b64f-14890e93e471)](https://www.python.org/)

## INSTALL
- Install requirements:
- 
  ```sh
  pip intall -r requirements.txt
  ```
  
- Create .env file and add your BOT_TOKEN, CRYPTO_BOT_TOKEN (crypto bot token for invoices)
   .env LOOK LIKE:

  ```sh
   BOT_TOKEN='your_token'
   CRYPTO_BOT_TOKEN='your_token'
  ```
  
- Run for create config file config.json:

  ``` sh
  python main.py
  ```
  
- Exit bot
- Edit config:
   | Config | Description |
   | ------ | ------ | 
   | admin_id | admin id |
   | bot_username | bot username without @ |
   | min_top_up_amount | min top up amount |
   | chat_id | chat id where to post your posts (The bot must have administrator rights in this chat) |
   | countdown_post_check | time how often does the bot check the database for posts to post now (optimal time) |
   | countdown | time how often does the bot post new posts |
   | prices | prices for post with link and without it |
- Run bot again:

  ```sh
  python main.py
  ```
