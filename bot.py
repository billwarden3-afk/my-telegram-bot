import requests
import time
import json

# ==========================================
# CONFIGURATION
# ==========================================
# Hardcoded credentials as requested
BOT_TOKEN = "8516700418:AAGZ-Yvn4qLNtIoSy6hll5KFQ0oO868nnZM"
EXTERNAL_API_URL = "https://anishexploits.site/anish-exploits/api.php?key=demo-testing&num="

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# User state tracker
user_states = {}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_updates(offset=None):
    """Fetches new messages from Telegram API."""
    url = BASE_URL + "getUpdates"
    params = {"timeout": 100}
    if offset:
        params["offset"] = offset
        
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        print(f"Error fetching updates: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    """Sends a message back to the user."""
    url = BASE_URL + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
        
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

# ==========================================
# MAIN BOT LOGIC
# ==========================================

def main():
    print("Bot is starting up... Press Ctrl+C to stop.")
    offset = None
    
    keyboard_markup = {
        "keyboard": [[{"text": "📱 Phone Lookup"}]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    while True:
        updates = get_updates(offset)
        
        if updates and "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                
                if "message" not in update:
                    continue
                    
                message = update["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "").strip()
                
                current_state = user_states.get(chat_id)

                # --- 1. Handling /start command ---
                if text == "/start":
                    user_states[chat_id] = None
                    welcome_text = "Welcome to Phone Lookup Bot! 👋\nClick the button below."
                    send_message(chat_id, welcome_text, reply_markup=keyboard_markup)
                
                # --- 2. Handling "Phone Lookup" button ---
                elif text == "📱 Phone Lookup":
                    user_states[chat_id] = "WAITING_FOR_NUMBER"
                    send_message(chat_id, "📞 Send 10 digit mobile number:")
                
                # --- 3. Handling Mobile Number Input ---
                elif current_state == "WAITING_FOR_NUMBER":
                    if text.isdigit() and len(text) == 10:
                        send_message(chat_id, "⏳ Fetching details... Please wait.")
                        
                        try:
                            # External API call
                            # Appending the 10-digit number directly to your URL
                            api_endpoint = f"{EXTERNAL_API_URL}{text}"
                            api_response = requests.get(api_endpoint)
                            
                            if api_response.status_code == 200:
                                data = api_response.json()
                                formatted_json = json.dumps(data, indent=4)
                                reply_text = f"<pre>{formatted_json}</pre>"
                            else:
                                reply_text = f"⚠️ API error: Received status code {api_response.status_code}"
                        
                        except Exception as e:
                            reply_text = f"⚠️ Request failed. Error: {e}"
                        
                        send_message(chat_id, reply_text)
                        user_states[chat_id] = None 
                    else:
                        send_message(chat_id, "❌ Invalid input! Please send exactly 10 numeric digits.\nTry again:")
                
                # --- 4. Handling Random Text ---
                else:
                    send_message(chat_id, "Please use the menu button or send /start.")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
