import os
import time
from playwright.sync_api import sync_playwright

class ToutiaoPublisher:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        # Persistent context directory to save cookies/session
        self.user_data_dir = os.path.join(os.getcwd(), "toutiao_data")

    def start(self):
        """Initializes Playwright with persistent context."""
        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            viewport={"width": 1280, "height": 800}
            # args=["--start-maximized"] # Optional
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

    def stop(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()

    def login(self):
        """
        Navigates to Toutiao MP. 
        If not logged in, waits for user to scan QR code.
        """
        print("🌍 Navigating to Toutiao Media Platform...")
        self.page.goto("https://mp.toutiao.com/")
        
        # Simple check: If we are redirected to login page or see login button
        # Toutiao MP usually redirects to /auth/page/login if not logged in
        
        try:
            # Wait a moment to see if we are already logged in
            # Adjust selector for a known element present only when logged in (e.g., User Avatar, 'Home' link)
            # Example: The sidebar usually has "首页" (Home) or user name.
            print("⏳ Checking login status...")
            self.page.wait_for_selector(".index-container", timeout=5000) 
            # Note: Selector might need adjustment based on actual page structure.
            # If successful, we are logged in.
            print("✅ Already logged in!")
            return True
        except:
            print("⚠️ Not logged in. Please scan the QR code in the browser window.")
            # Verify we are on login page
            # Wait indefinitely (or long timeout) for user to log in
            # We can detect success by waiting for the dashboard element again
            try:
                self.page.wait_for_selector(".index-container", timeout=300000) # Wait 5 mins
                print("✅ Login detected!")
                # Save storage state explicitly if needed, though persistent_context handles it.
                return True
            except:
                print("❌ Login timed out.")
                return False

    def publish_article(self, title, content):
        """
        Publishes an article.
        """
        print(f"🚀 Preparing to publish: {title}")
        
        # Navigate to publish page
        # The URL for publishing article is usually:
        publish_url = "https://mp.toutiao.com/profile_v4/graphic/publish"
        self.page.goto(publish_url)
        self.page.wait_for_load_state("networkidle")
        
        time.sleep(2) # Stability wait

        # Fill Title
        # Selectors need to be inspected. Common selectors for these platforms:
        # Title input often has placeholder '请输入标题' or similar.
        print("✍️ Filling title...")
        try:
            # Try finding by placeholder or common class
            title_input = self.page.get_by_placeholder("请输入标题", exact=False)
            if title_input.count() > 0:
                title_input.nth(0).fill(title)
            else:
                # Fallback to inspecting DOM structure (needs update after first run if fails)
                # This is a guess:
                self.page.locator("input[type='text']").first.fill(title)
        except Exception as e:
            print(f"❌ Error filling title: {e}")
            return False

        # Fill Content
        print("✍️ Filling content...")
        try:
            # Content is usually a rich text editor. 
            # We might simply target the contenteditable div.
            editor = self.page.locator(".ProseMirror").first # Bytes uses ProseMirror often? or unexpected.
            # Fallback: specific class
            if not editor.is_visible():
                editor = self.page.locator("div[contenteditable='true']").first
            
            editor.click()
            editor.fill(content)
            # Or use keyboard type for simulation
            # self.page.keyboard.type(content)
        except Exception as e:
            print(f"❌ Error filling content: {e}")
            return False
            
        # Click Publish
        print("📤 Clicking Publish...")
        try:
            # Find the publish button. Usually "发布" or "发表"
            publish_btn = self.page.get_by_text("发布", exact=True)
            # Often there are multiple "Publish" (e.g. Publish, Save Draft). 
            # Needs precision.
            if publish_btn.count() > 0:
                # specific logic might be needed (e.g. confirm dialog)
                # publish_btn.click() 
                print("⚠️ Simulation mode: Publish button found but NOT clicked to avoid spam during test.")
                print("   Uncomment the click action in code to actually publish.")
            else:
                print("❌ Publish button not found.")
                
        except Exception as e:
            print(f"❌ Error clicking publish: {e}")
            return False
            
        return True

if __name__ == "__main__":
    publisher = ToutiaoPublisher(headless=False)
    try:
        publisher.start()
        if publisher.login():
            # Test Publish
            publisher.publish_article("Test Title from Agent", "This is a test content generated by AI Agent.")
            
            # Keep browser open for a bit to see result
            print("👀 Keeping browser open for 10 seconds...")
            time.sleep(10)
    finally:
        publisher.stop()
