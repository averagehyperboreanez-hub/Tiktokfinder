import os
import json
import requests
import asyncio
import sys
import types
sys.modules['audioop'] = types.ModuleType('audioop')
import discord
from discord.ext import tasks, commands

# ------------- CONFIG -------------
TIKTOK_USERNAME = "officialhotspotsitoarmy"  # change or make dynamic later
DISCORD_CHANNEL_ID = 1435856303128838326 # replace with your channel ID
CHECK_INTERVAL = 60  # seconds (10 minutes)
# ----------------------------------

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

latest_post_id = None  # memory for the newest video ID


def fetch_latest_post(username):
    """Scrape TikTok page and return newest video ID and caption."""
    try:
        url = f"https://www.tiktok.com/@{username}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        html = r.text
        start = html.find('{"props"')
        end = html.find('</script>', start)
        data_json = html[start:end]
        data = json.loads(data_json)
        items = data["props"]["pageProps"].get("itemListData", [])
        if not items:
            return None, None
        item = items[0]["itemInfos"]
        return item["id"], item.get("text", "")
    except Exception as e:
        print("Error fetching TikTok data:", e)
        return None, None


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    check_tiktok.start()


@tasks.loop(seconds=CHECK_INTERVAL)
async def check_tiktok():
    global latest_post_id
    new_post_id, caption = fetch_latest_post(TIKTOK_USERNAME)
    if not new_post_id:
        return
    if new_post_id != latest_post_id:
        latest_post_id = new_post_id
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/{new_post_id}"
            embed = discord.Embed(
                title=f"New TikTok post by @{TIKTOK_USERNAME}",
                description=caption or "(no caption)",
                color=0xFF0050,
            )
            embed.add_field(name="Link", value=url, inline=False)
            await channel.send(embed=embed)
            print("New post detected -> sent to Discord")


if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_TOKEN")
    bot.run(TOKEN)

