import discord
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION ---
TOKEN = 'MTUwMTE3MzcwMDA4NTY4MjIzNg.GcXDUS.-K-XxyX9BtHwoCyLiLkk-JSymgoOKj9YraYYJc'

# ID of the bot that posts the drops
BOT_USER_ID = 1340117151419465868 

# ID of the channel in the Brawl Stars server to monitor
WATCH_CHANNEL_ID = 294192597939912714 

# ID of the channel in your private server where alerts will be sent
FORWARD_CHANNEL_ID = 1533116331518460106 

# Your main account's ID to be pinged
MAIN_USER_ID = 1283120164312973437 
# ---------------------

class DropTracker(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        print('Listening for drops...')

    async def on_message(self, message):
        # Ignore messages not in the watch channel
        if message.channel.id != WATCH_CHANNEL_ID:
            return

        # Check if the sender is the specific drop bot
        if message.author.id == BOT_USER_ID:
            print("Drop detected! Forwarding to mobile...")
            
            # Find the private channel
            forward_channel = self.get_channel(FORWARD_CHANNEL_ID)
            
            if forward_channel:
                # Ping your main account in the private server
                alert_text = f"<@{MAIN_USER_ID}> 🚨 **DROP DETECTED!** 🚨\n"
                
                # Include a direct link to jump to the drop message
                alert_text += f"[Click here to jump to the drop]({message.jump_url})"
                
                await forward_channel.send(alert_text)
            else:
                print("Error: Could not find the forwarding channel.")

# Run the client
client = DropTracker()
keep_alive()
client.run(TOKEN)