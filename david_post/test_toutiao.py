from toutiao import ToutiaoPublisher
import time

def run_test():
    print("🚀 Starting Toutiao Automation Test...")
    publisher = ToutiaoPublisher(headless=False)
    
    try:
        publisher.start()
        
        # 1. Login
        print("🔑 Attempting login...")
        if publisher.login():
            print("✅ Login Successful.")
            
            # 2. Publish (Draft)
            title = "Testing AI Automation"
            content = "This is a test draft created by the automation script. Please ignore."
            
            print(f"📝 Publishing: {title}")
            publisher.publish_article(title, content)
            
            print("🎉 Test Finished. Please check browser.")
        else:
            print("❌ Login Failed.")
            
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        # Keep it open for manual inspection
        # input("Press Enter to close browser...")
        time.sleep(5)
        publisher.stop()
        print("👋 Browser closed.")

if __name__ == "__main__":
    run_test()
