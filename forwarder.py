import discord
import requests
from flask import Flask
from threading import Thread

# Web server initialization for Render uptime monitoring
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIGURATION ---
TOKEN = 'MTUwMTE3MzcwMDA4NTY4MjIzNg.GcXDUS.-K-XxyX9BtHwoCyLiLkk-JSymgoOKj9YraYYJc'

# ID of the bot posting the drops
BOT_USER_ID = 1340117151419465868 

# ID of the channel in the Brawl Stars server to monitor
WATCH_CHANNEL_ID = 294192597939912714 

# ID of the channel in your private server where alerts will be sent
FORWARD_CHANNEL_ID = 1533116331518460106 

# Your main account's ID to be pinged
MAIN_USER_ID = 1283120164312973437 

# Keywords to match (processed as lowercase)
DROP_KEYWORDS = [
    "supply drop incoming!",
    "claim",
    "tokens!",
    "tokens",
    "supply",
    "drop",
    "incoming"
]
# ---------------------

class DropTracker(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        print('Listening for drops...')

    async def on_message(self, message):
        # Ignore messages from any other channel
        if message.channel.id != WATCH_CHANNEL_ID:
            return

        # Verify the sender is the designated drop bot
        if message.author.id == BOT_USER_ID:
            
            # Extract plain text content safely
            text_to_check = (message.content or "").lower()
            
            # Extract title and description from any attached embeds
            for embed in message.embeds:
                if embed.description:
                    text_to_check += " " + embed.description.lower()
                if embed.title:
                    text_to_check += " " + embed.title.lower()
            
            # Check if any configured keyword exists in the extracted text
            if any(keyword.lower() in text_to_check for keyword in DROP_KEYWORDS):
                print("Drop detected! Forwarding alert...")
                
                # 1. Send push notification to phone via ntfy
                try:
                    requests.post(
                        "https://ntfy.sh/nsIiUQCvdeUNyPNN",
                        data="BRAWL STARS DROP IS ACTIVE! CLAIM NOW!",
                        headers={
                            "Title": "🚨 BRAWL DROP ALERT 🚨",
                            "Priority": "high",        
                            "Tags": "warning,game"     
                        },
                        timeout=5
                    )
                except Exception as e:
                    print(f"ntfy push notification failed: {e}")
                
                # 2. Send ping to private Discord channel
                forward_channel = self.get_channel(FORWARD_CHANNEL_ID)
                if forward_channel:
                    alert_text = (
                        f"<@{MAIN_USER_ID}> 🚨 **DROP DETECTED!** 🚨\n"
                        f"[Click here to jump to the drop]({message.jump_url})"
                    )
                    await forward_channel.send(alert_text)
                else:
                    print("Error: Target forwarding channel could not be found.")

if __name__ == '__main__':
    keep_alive()
    client = DropTracker()
    client.run(TOKEN)
