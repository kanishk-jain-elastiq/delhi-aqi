# Delhi AQI Twitter Bot

This bot tweets daily updates about New Delhi's Air Quality Index (AQI) until the city maintains an AQI of 25 or below for one year straight. The bot helps raise awareness about air quality issues in New Delhi and tracks progress towards cleaner air.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   IQAIR_API_KEY=your_iqair_api_key
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   TWITTER_ACCESS_TOKEN=your_twitter_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
   ```

4. Run the bot:
   ```bash
   python main.py
   ```

## How it works

- The bot fetches daily AQI data from IQAir API for a specific location in New Delhi
- It tweets the AQI value daily
- If AQI is 25 or below, it starts/continues a 365-day counter
- If AQI goes above 25, the counter resets
- The bot runs automatically once per day
- All data is stored locally in a SQLite database

## API Keys

1. Get your IQAir API key from: https://www.iqair.com/air-pollution-data-api
2. Get your Twitter API keys by creating a developer account at: https://developer.twitter.com/ 