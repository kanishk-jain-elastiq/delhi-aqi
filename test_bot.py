import os
from datetime import datetime, timedelta
from main import AQIRecord, Base, Session, engine
from main import create_tweet_text, create_rules_tweet, get_clean_days_count

def reset_test_database():
    """Reset the test database"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def simulate_days(aqi_values):
    """Simulate running the bot with given AQI values"""
    session = Session()
    
    print("\n=== Starting AQI Bot Simulation ===\n")
    
    start_date = datetime.now().date() - timedelta(days=len(aqi_values) - 1)
    
    for i, aqi in enumerate(aqi_values):
        current_date = start_date + timedelta(days=i)
        is_clean = aqi <= 25
        
        # Calculate clean days
        previous_clean_days = get_clean_days_count(session)
        clean_days = previous_clean_days + 1 if is_clean else 0
        
        # Create and save record
        record = AQIRecord(
            date=current_date,
            aqi=aqi,
            is_clean=is_clean,
            clean_days_count=clean_days
        )
        session.add(record)
        session.commit()
        
        # Print what would be tweeted
        print(f"\nDay {i + 1} ({current_date}):")
        print("-" * 50)
        print(create_tweet_text(aqi, clean_days))
        
        if is_clean or current_date.day == 1:
            print("\nRules Reply:")
            print("-" * 50)
            print(create_rules_tweet())
    
    session.close()

def run_tests():
    """Run various test scenarios"""
    
    # Test Scenario 1: All high AQI values
    print("\n🧪 Test Scenario 1: Consistently high AQI")
    reset_test_database()
    simulate_days([150, 200, 175])
    
    # Test Scenario 2: Clean streak then reset
    print("\n🧪 Test Scenario 2: Clean streak then reset")
    reset_test_database()
    simulate_days([20, 15, 18, 30, 25])
    
    # Test Scenario 3: Multiple clean streaks
    print("\n🧪 Test Scenario 3: Multiple clean streaks")
    reset_test_database()
    simulate_days([20, 15, 30, 20, 18, 16])

if __name__ == "__main__":
    # Create a test database
    print("Running AQI Bot Tests...")
    run_tests()
    
    # Custom test
    print("\n🧪 Custom Test")
    print("You can input your own AQI values to test (comma-separated):")
    try:
        values = input("Enter AQI values (e.g., 25,30,20,15): ")
        aqi_values = [int(x.strip()) for x in values.split(",")]
        reset_test_database()
        simulate_days(aqi_values)
    except ValueError:
        print("Invalid input. Please enter numbers separated by commas.") 