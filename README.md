# Nintendo Museum Ticket Monitor

Automated monitor for available tickets at the Nintendo Museum in Kyoto, Japan.

## 🎮 What is This?

This tool automatically checks for available tickets at the [Nintendo Museum in Kyoto](https://museum.nintendo.com/) and sends you a Discord notification when tickets become available. Perfect for anyone trying to visit the museum!

## ✨ Features

- 🔍 Monitors Nintendo Museum ticket availability
- 🔄 Automatic proxy rotation on every request (optional)
- 🌐 Browser impersonation using `curl_cffi` (Chrome 110)
- 💬 Discord webhook notifications
- ⏱️ Configurable check interval
- 🎯 Smart filters:
  - Only open days (excludes Tuesdays when museum is closed)
  - Only available tickets (`sale_status == 1`)
  - Only future dates
  - No duplicate notifications

## 📋 Prerequisites

Before you start, you'll need:

- **Python 3.13+** - [Download here](https://www.python.org/downloads/)
- **uv** - A fast Python package manager - [Install guide](https://docs.astral.sh/uv/getting-started/installation/)

### Installing uv (Easy!)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/nintendo-museum.git
cd nintendo-museum
```

### 2. Install Dependencies

Using `uv` makes this super simple:

```bash
uv sync
```

That's it! `uv` will automatically:
- Create a virtual environment
- Install all required packages
- Set everything up for you

### 3. Configure Your Settings

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Then edit `.env` with your settings:

```env
# Discord Webhook URL (required)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL

# Check interval in seconds (optional, default: 20)
MONITOR_INTERVAL=20

# Webshare Proxy API (optional)
API_KEY_WEBSHARE=your_api_key
USE_WEBSHARE=True
```

### 4. Set Up Discord Notifications

Don't worry, it's easy! Follow these steps:

1. Open Discord and go to your server
2. Click on **Server Settings** → **Integrations** → **Webhooks**
3. Click **New Webhook**
4. Give it a name (e.g., "Nintendo Museum Bot")
5. Choose a channel where you want notifications
6. Click **Copy Webhook URL**
7. Paste the URL in your `.env` file

**Example:**
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdefghijklmnop
```

### 5. Run the Monitor

```bash
uv run python main.py
```

The monitor will start checking for tickets automatically! 🎉

## ⚙️ Configuration Options

### Basic Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `DISCORD_WEBHOOK_URL` | Your Discord webhook URL (required) | None |
| `MONITOR_INTERVAL` | How often to check for tickets (seconds) | 20 |

### Proxy Settings (Optional)

Proxies help avoid rate limiting and IP blocks.

**Option 1: Webshare API (Recommended)**
```env
API_KEY_WEBSHARE=your_api_key_here
USE_WEBSHARE=True
```

**Option 2: Custom Proxy File**
```env
USE_WEBSHARE=False
```

Create `utils/proxies.txt`:
```
ip:port:username:password
ip:port:username:password
```

**Option 3: No Proxies**
```env
USE_WEBSHARE=False
```
Leave out the `proxies.txt` file to use direct connections.

## 📊 Example Output

When running, you'll see output like this:

```
2025-10-25 09:52:00 - nintendo_main - INFO - ==================================================
2025-10-25 09:52:00 - nintendo_main - INFO - Nintendo Museum Ticket Monitor
2025-10-25 09:52:00 - nintendo_main - INFO - ==================================================
2025-10-25 09:52:00 - nintendo_main - INFO - Monitoring: 2025-10
2025-10-25 09:52:00 - nintendo_main - INFO - Interval: 20 seconds
2025-10-25 09:52:00 - nintendo_main - INFO - ==================================================
2025-10-25 09:52:00 - nintendo_monitor - INFO - Starting Nintendo Museum Monitor for 2025-10
2025-10-25 09:52:02 - nintendo_monitor - INFO - Successfully fetched calendar for 2025-10
2025-10-25 09:52:02 - nintendo_monitor - INFO - Found available date: 2025-10-26 (sale_status=1, open_status=1)
2025-10-25 09:52:02 - nintendo_monitor - INFO - Found 1 available dates
2025-10-25 09:52:03 - nintendo_monitor - INFO - Notification sent for 2025-10-26
```

## 📁 Project Structure

```
nintendo-museum/
├── main.py                 # Main entry point - start here!
├── src/
│   └── monitor.py         # Core monitoring logic
├── utils/
│   ├── discord_utils.py   # Discord webhook handler
│   ├── load_proxies.py    # Proxy management
│   └── logging_setter.py  # Logging configuration
├── logs/                  # Log files (auto-created)
├── .env                   # Your configuration (not in git)
├── .env.example           # Example configuration
├── pyproject.toml         # Python dependencies
└── README.md              # This file!
```

## 🔧 Technical Details

### API Endpoint

The monitor uses the official Nintendo Museum API:

```
GET https://museum-tickets.nintendo.com/en/api/calendar
Parameters:
  - target_year: Year (e.g., 2025)
  - target_month: Month (e.g., 11)
```

### Response Format

```json
{
  "data": {
    "calendar": {
      "2025-11-01": {
        "apply_type": 3,
        "sale_status": 2,
        "open_status": 1,
        "holiday": null,
        "day_label": null,
        "is_temporary_closure": false,
        "temporary_closure_time": null,
        "is_holding": false
      }
    }
  }
}
```

**Status Codes:**
- `sale_status = 1` → Tickets available ✅
- `sale_status = 2` → Tickets sold out ❌
- `open_status = 1` → Museum open ✅
- `open_status = 2` → Museum closed (Tuesdays) ❌

### Dependencies

- `curl-cffi` - Browser impersonation for requests
- `python-dotenv` - Environment variable management
- `discord-webhook` - Discord notifications
- `requests` - Proxy API calls

## 📝 Logs

Logs are automatically saved in the `logs/` directory:
- `nintendo_main_monitor.log` - Main process logs
- `nintendo_monitor_monitor.log` - Monitor activity logs

## 🔥 Troubleshooting

### "No proxies available"

**Solution 1:** Use direct connection
```env
USE_WEBSHARE=False
```
Remove or don't create `utils/proxies.txt`

**Solution 2:** Check your proxy configuration
```bash
cat .env
```

### "Discord webhook URL not configured"

Make sure your `.env` file has the webhook URL:
```bash
cat .env | grep DISCORD_WEBHOOK_URL
```

### "Module not found" errors

Reinstall dependencies:
```bash
uv sync
```

### Monitor stops unexpectedly

Check the log files in `logs/` for error messages.

## ℹ️ Important Notes

**Museum Closure:**
The Nintendo Museum is **closed on Tuesdays**. The monitor automatically skips these days.

**Rate Limiting:**
Use a reasonable check interval (recommended: 20-60 seconds) to avoid overwhelming the API.

**Responsible Use:**
This tool is for personal use only. Please respect Nintendo's terms of service and don't abuse the API.

## 🔗 Useful Links

- [Nintendo Museum Official Website](https://museum.nintendo.com/)
- [Nintendo Museum Ticket Booking](https://museum-tickets.nintendo.com/en/calendar)
- [uv Documentation](https://docs.astral.sh/uv/)

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This tool is for informational purposes only. Please respect the Nintendo Museum website's terms of service. The authors are not responsible for any misuse of this tool.

---

**Made with ❤️ for Nintendo fans worldwide**

*Having trouble? [Open an issue](https://github.com/YOUR_USERNAME/nintendo-museum/issues)*
