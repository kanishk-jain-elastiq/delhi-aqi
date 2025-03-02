import os
import tweepy
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Date, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Constants
AQI_THRESHOLD = 25
REQUIRED_CLEAN_DAYS = 365
DELHI_LAT = 28.644800
DELHI_LONG = 77.216721  # Coordinates for Central Delhi
LOCATION_NAME = "Central Delhi"

# Database setup
class Base(DeclarativeBase):
    pass

# Modified database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///aqi_tracker.db')  # fallback to SQLite for local development
if DATABASE_URL.startswith("postgres://"):  # Heroku provides "postgres://" but SQLAlchemy needs "postgresql://"
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class AQIRecord(Base):
    __tablename__ = 'aqi_records'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True)
    aqi = Column(Integer)
    is_clean = Column(Boolean)
    clean_days_count = Column(Integer)

Base.metadata.create_all(engine)

# Twitter API setup
def get_twitter_api():
    client = tweepy.Client(
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    )
    return client

def get_aqi_data():
    """Fetch AQI data from IQAir API"""
    url = f"http://api.airvisual.com/v2/nearest_city"
    params = {
        'lat': DELHI_LAT,
        'lon': DELHI_LONG,
        'key': os.getenv('IQAIR_API_KEY')
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data['data']['current']['pollution']['aqius']
    except Exception as e:
        print(f"Error fetching AQI data: {e}")
        return None

def get_clean_days_count(session):
    """Get the current streak of clean days"""
    latest_record = session.query(AQIRecord).order_by(AQIRecord.date.desc()).first()
    return latest_record.clean_days_count if latest_record else 0

def create_tweet_text(aqi, clean_days):
    """Create the tweet text based on AQI and clean days count"""
    header = "Tweeting daily until New Delhi's AQI Reaches 25 for one year straight.\n\n"
    
    if aqi <= AQI_THRESHOLD:
        status = f"Today's AQI in {LOCATION_NAME}: {aqi} ✨\n"
        if clean_days == 0:
            counter = "Starting our 365-day counter today! 🌟"
        else:
            counter = f"Clean air streak: {clean_days}/365 days! 🌟"
    else:
        status = f"Today's AQI in {LOCATION_NAME}: {aqi} 😷\n"
        counter = "Counter reset. We need AQI ≤ 25 for a full year."
    
    return f"{header}{status}{counter}"

def create_rules_tweet():
    """Create a tweet explaining the rules"""
    rules = (
        "🔍 How this works:\n\n"
        "1️⃣ I tweet Delhi's AQI at 9:00 AM IST daily\n"
        "2️⃣ Counter starts when AQI ≤ 25\n"
        "3️⃣ Goal: 365 consecutive clean air days\n"
        "4️⃣ Counter resets if AQI > 25\n\n"
        "This is an automated system I made using Cursor"
    )
    return rules

def daily_task():
    """Main daily task to fetch AQI and post tweet"""
    session = Session()
    client = get_twitter_api()
    
    try:
        # Get AQI data
        aqi = get_aqi_data()
        if aqi is None:
            return
        
        # Check if record for today already exists
        today = datetime.now().date()
        existing_record = session.query(AQIRecord).filter(AQIRecord.date == today).first()
        if existing_record:
            print(f"Record for {today} already exists. Skipping...")
            return
            
        # Calculate clean days
        is_clean = aqi <= AQI_THRESHOLD
        previous_clean_days = get_clean_days_count(session)
        clean_days = previous_clean_days + 1 if is_clean else 0
        
        # Create and save record
        record = AQIRecord(
            date=today,
            aqi=aqi,
            is_clean=is_clean,
            clean_days_count=clean_days
        )
        session.add(record)
        
        # Post tweet
        tweet = client.create_tweet(text=create_tweet_text(aqi, clean_days))
        
        # Post rules as reply (for every tweet)
        client.create_tweet(
            text=create_rules_tweet(),
            in_reply_to_tweet_id=tweet.data['id']
        )
        
        session.commit()
        
    except Exception as e:
        print(f"Error in daily task: {e}")
        session.rollback()
    finally:
        session.close()

def main():
    """Main function to run the bot"""
    print("Starting Delhi AQI Twitter Bot...")
    daily_task()

if __name__ == "__main__":
    # Create tables
    Base.metadata.create_all(engine)
    # Run the task once
    main() 