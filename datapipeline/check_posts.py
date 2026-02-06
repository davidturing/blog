
import xmlrpc.client
import ssl

# Config
WP_USER = "davidturing"
WP_APP_PASS = "5hyx wocr tyom lwef"
WP_DOMAIN = "microblocks0.wordpress.com"
WP_XMLRPC_URL = f"https://{WP_DOMAIN}/xmlrpc.php"

def main():
    print(f"Connecting to {WP_XMLRPC_URL}...")
    context = ssl._create_unverified_context()
    server = xmlrpc.client.ServerProxy(WP_XMLRPC_URL, context=context)
    
    try:
        # Get pages
        print("Fetching Pages...")
        posts = server.wp.getPages(0, WP_USER, WP_APP_PASS, {'number': 100})
        print(f"Found {len(posts)} pages.")
        for p in posts:
            print(f"Keys: {p.keys()}")
            print(f"ID: {p.get('page_id')} | Title: {p.get('page_title')} | Status: {p.get('page_status')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
