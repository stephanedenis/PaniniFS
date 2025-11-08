#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import sys

def test_webapp():
    console_messages = []
    page_errors = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Collect console messages
        def handle_console(msg):
            msg_type = msg.type
            text = msg.text
            console_messages.append({'type': msg_type, 'text': text})
            print(f"[CONSOLE {msg_type.upper()}] {text}")
        
        # Collect page errors
        def handle_error(error):
            page_errors.append(str(error))
            print(f"[PAGE ERROR] {error}")
        
        # Collect network errors
        def handle_request_failed(request):
            print(f"[NETWORK FAILED] {request.url} - {request.failure}")
        
        page.on("console", handle_console)
        page.on("pageerror", handle_error)
        page.on("requestfailed", handle_request_failed)
        
        try:
            print("🚀 Navigating to http://localhost:5173/")
            page.goto("http://localhost:5173/", wait_until="networkidle", timeout=10000)
            print("✅ Page loaded successfully")
            
            # Wait for any async errors
            page.wait_for_timeout(3000)
            
            # Get page info
            title = page.title()
            print(f"\n📄 Page title: {title}")
            
            # Check for React root
            has_root = page.locator("#root").count() > 0
            print(f"⚛️  React root present: {has_root}")
            
            # Check body content
            body_text = page.text_content("body")
            print(f"📝 Body has content: {len(body_text) > 100} ({len(body_text)} chars)")
            
            # Summary
            print("\n" + "="*60)
            print("📊 TEST SUMMARY")
            print("="*60)
            print(f"Console messages: {len(console_messages)}")
            print(f"  - log: {len([m for m in console_messages if m['type'] == 'log'])}")
            print(f"  - warning: {len([m for m in console_messages if m['type'] == 'warning'])}")
            print(f"  - error: {len([m for m in console_messages if m['type'] == 'error'])}")
            print(f"Page errors: {len(page_errors)}")
            
            if page_errors:
                print("\n❌ ERRORS FOUND:")
                for i, err in enumerate(page_errors, 1):
                    print(f"  {i}. {err}")
            
            error_msgs = [m for m in console_messages if m['type'] == 'error']
            if error_msgs:
                print("\n❌ CONSOLE ERRORS:")
                for i, msg in enumerate(error_msgs, 1):
                    print(f"  {i}. {msg['text']}")
            
            if not page_errors and not error_msgs:
                print("\n✅ NO ERRORS DETECTED")
                return 0
            else:
                return 1
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return 1
        finally:
            browser.close()

if __name__ == "__main__":
    sys.exit(test_webapp())
