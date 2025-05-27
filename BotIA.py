import telebot
from telebot.types import Message
import requests
import json
import time

# Bot token 
TOKEN = 'Seu Token'

bot = telebot.TeleBot(TOKEN)

# API DA IA
API_URL = "https://botfather.cloud/Apis/AI/client.php?message="

def split_message(text, max_length=4096):
    """Split a long message into chunks under max_length, preserving sentences where possible."""
    if len(text) <= max_length:
        return [text]
    
    messages = []
    current_message = ""
    sentences = text.split('. ')
    
    for sentence in sentences:
        # Add the period back to the sentence
        sentence = sentence + ('.' if sentence else '')
        if len(current_message) + len(sentence) <= max_length:
            current_message += sentence + (' ' if sentence else '')
        else:
            if current_message:
                messages.append(current_message.strip())
            current_message = sentence + (' ' if sentence else '')
    
    if current_message:
        messages.append(current_message.strip())
    
    return messages

@bot.message_handler(content_types=['text'])
def handle_text_message(message: Message):
    """Handle incoming text messages and send them to the Gemini AI API."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_message = message.text

    print(f"Received message from User ID {user_id} in Chat ID {chat_id}: {user_message}")

    
    try:
        
        encoded_message = requests.utils.quote(user_message)
        response = requests.get(API_URL + encoded_message, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        if data.get("success") and "response" in data:
            reply = data["response"]
            print(f"API response: {reply[:100]}...")

            
            message_chunks = split_message(reply)

            
            for chunk in message_chunks:
                try:
                    bot.send_message(chat_id, chunk)
                    print(f"Sent chunk to User ID {user_id}: {chunk[:50]}...")
                    time.sleep(0.5)  # Small delay to avoid rate limiting
                except telebot.apihelper.ApiTelegramException as e:
                    if "blocked by user" in str(e).lower():
                        print(f"User ID {user_id} blocked the bot.")
                        return
                    elif "chat not found" in str(e).lower():
                        print(f"Chat not found for User ID {user_id}. Please start a private chat with the bot.")
                        return
                    else:
                        print(f"Telegram API error while sending to User ID {user_id}: {str(e)}")
                        bot.send_message(chat_id, "Erro ao enviar a mensagem. Tente novamente.")
        else:
            bot.send_message(chat_id, "Desculpe, não consegui processar sua solicitação. Tente novamente mais tarde.")
            print(f"API error: Success=False or no response field in {data}")

    except requests.exceptions.RequestException as e:
        bot.send_message(chat_id, "Erro ao conectar com o serviço de IA. Tente novamente mais tarde.")
        print(f"Request error while contacting API: {str(e)}")
    except json.JSONDecodeError:
        bot.send_message(chat_id, "Erro ao processar a resposta da IA. Tente novamente mais tarde.")
        print("JSON decode error in API response")
    except Exception as e:
        bot.send_message(chat_id, "Ocorreu um erro inesperado. Tente novamente mais tarde.")
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    print("Bem vindo, Mlz77k...") 
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Erro no polling: {str(e)}")
            time.sleep(5)  # Wait before restarting to avoid rapid crash loops      try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Erro no polling: {str(e)}")
            time.sleep(5)  # Wait before restarting to avoid rapid crash loops