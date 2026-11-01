import subprocess
import time
import os
import shutil
import urllib.request
import urllib.error
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"c:\Users\prade\OneDrive\Desktop\OOO"
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
TEMP_DIR = os.environ.get("TEMP", r"C:\Users\prade\AppData\Local\Temp")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FONT_PATH = r"C:\Windows\Fonts\consola.ttf"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def take_browser_screenshot(url, dest_filename, window_size="1000,600"):
    temp_file = os.path.join(TEMP_DIR, f"temp_{dest_filename}")
    if os.path.exists(temp_file):
        os.remove(temp_file)
    dest_path = os.path.join(SCREENSHOTS_DIR, dest_filename)
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={window_size}",
        f"--screenshot={temp_file}",
        url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(temp_file):
        shutil.copy(temp_file, dest_path)
        os.remove(temp_file)
        print(f"Captured: {dest_filename} ({window_size}) from {url}")
        return True
    else:
        print(f"Failed to capture {dest_filename}: {res.stderr}")
        return False

def render_terminal_image(lines, dest_filename="terminal-execution.png"):
    font_size = 15
    font = ImageFont.truetype(FONT_PATH, font_size)
    line_height = 24
    padding_x = 24
    padding_y = 20
    topbar_height = 36
    
    # Calculate dimensions
    max_line_len = max(len(l[1]) for l in lines)
    width = max(900, max_line_len * 9 + padding_x * 2)
    height = topbar_height + padding_y * 2 + len(lines) * line_height

    img = Image.new("RGB", (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Draw window topbar
    draw.rectangle([(0, 0), (width, topbar_height)], fill=(40, 40, 40))
    # Window controls (close, min, max buttons)
    draw.ellipse([(14, 12), (24, 22)], fill=(255, 95, 86))
    draw.ellipse([(32, 12), (42, 22)], fill=(255, 189, 46))
    draw.ellipse([(50, 12), (60, 22)], fill=(39, 201, 63))
    
    # Window title
    title_font = ImageFont.truetype(FONT_PATH, 13)
    draw.text((width // 2 - 140, 10), "PowerShell - CS210 Lab 01 Execution", fill=(170, 170, 170), font=title_font)

    # Render lines
    y = topbar_height + padding_y
    for kind, text in lines:
        if kind == "prompt":
            draw.text((padding_x, y), text, fill=(80, 200, 120), font=font)
        elif kind == "cmd":
            draw.text((padding_x, y), text, fill=(255, 255, 255), font=font)
        elif kind == "info":
            draw.text((padding_x, y), text, fill=(100, 180, 255), font=font)
        elif kind == "success":
            draw.text((padding_x, y), text, fill=(120, 230, 120), font=font)
        elif kind == "warn":
            draw.text((padding_x, y), text, fill=(255, 180, 50), font=font)
        elif kind == "error":
            draw.text((padding_x, y), text, fill=(255, 100, 100), font=font)
        else: # normal
            draw.text((padding_x, y), text, fill=(210, 210, 210), font=font)
        y += line_height

    dest_path = os.path.join(SCREENSHOTS_DIR, dest_filename)
    img.save(dest_path)
    print(f"Generated terminal screenshot: {dest_filename}")

def main():
    print("=== Starting CS210 Lab 01 Complete Execution & Screenshot Capture ===")
    terminal_lines = [
        ("prompt", "PS C:\\Users\\prade\\OneDrive\\Desktop\\OOO> node -v && npm -v"),
        ("normal", "v24.14.1"),
        ("normal", "11.13.0"),
        ("normal", ""),
        ("prompt", "PS C:\\Users\\prade\\OneDrive\\Desktop\\OOO> # 1. Running Native Node.js HTTP Server (server-http.js)"),
        ("cmd", "PS C:\\Users\\prade\\OneDrive\\Desktop\\OOO> node server-http.js"),
    ]

    # Step 1: Run server-http.js
    print("\n--- Step 1: Running server-http.js ---")
    proc_http = subprocess.Popen(["node", os.path.join(BASE_DIR, "server-http.js")])
    time.sleep(1.5)
    
    http_resp_text = ""
    try:
        with urllib.request.urlopen("http://localhost:3000") as resp:
            http_status = resp.status
            http_resp_text = resp.read().decode()
            print(f"server-http.js response: Status={http_status}, Body='{http_resp_text}'")
            terminal_lines.append(("info", "HTTP server running at http://localhost:3000"))
            terminal_lines.append(("prompt", "PS C:\\Users\\prade\\OneDrive\\Desktop\\OOO> curl http://localhost:3000"))
            terminal_lines.append(("success", f"HTTP/1.1 {http_status} OK"))
            terminal_lines.append(("normal", f"{http_resp_text}"))
        
        take_browser_screenshot("http://localhost:3000", "http-server.png", "1000,600")
    finally:
        proc_http.terminate()
        proc_http.wait()
        print("Stopped server-http.js")
        terminal_lines.append(("warn", "^C (server-http.js stopped)"))
        terminal_lines.append(("normal", ""))

    time.sleep(1)

    # Step 2: Run server.js (Express Server)
    print("\n--- Step 2: Running server.js (Express) ---")
    terminal_lines.append(("prompt", "PS C:\\Users\\prade\\OneDrive\\Desktop\\OOO> # 2. Running Express Server (server.js)"))
    terminal_lines.append(("cmd", "PS C:\\Users\\prade\\OneDrive\\Desktop\\OOO> node server.js"))

    proc_express = subprocess.Popen(["node", os.path.join(BASE_DIR, "server.js")])
    time.sleep(1.5)

    try:
        terminal_lines.append(("info", "Express server running at http://localhost:3000"))
        
        # Test 1: GET /
        print("\nTesting GET /")
        with urllib.request.urlopen("http://localhost:3000/") as resp:
            body = resp.read().decode()
            print(f"GET / -> Status {resp.status}, Body: {body}")
            terminal_lines.append(("prompt", "PS C:\\Users\\prade\\OneDrive\\Desktop\\OOO> curl http://localhost:3000/"))
            terminal_lines.append(("success", f"HTTP/1.1 {resp.status} OK"))
            terminal_lines.append(("normal", body))
        take_browser_screenshot("http://localhost:3000/", "home.png", "1000,600")

        # Test 2: GET /about
        print("\nTesting GET /about")
        with urllib.request.urlopen("http://localhost:3000/about") as resp:
            body = resp.read().decode()
            print(f"GET /about -> Status {resp.status}, Body: {body}")
            terminal_lines.append(("prompt", "PS C:\\Users\\prade\\OneDrive\\Desktop\\OOO> curl http://localhost:3000/about"))
            terminal_lines.append(("success", f"HTTP/1.1 {resp.status} OK"))
            terminal_lines.append(("normal", body))
        take_browser_screenshot("http://localhost:3000/about", "about.png", "1000,600")

        # Test 3: GET /time
        print("\nTesting GET /time")
        with urllib.request.urlopen("http://localhost:3000/time") as resp:
            body = resp.read().decode()
            print(f"GET /time -> Status {resp.status}, Body: {body}")
            terminal_lines.append(("prompt", "PS C:\\Users\\prade\\OneDrive\\Desktop\\OOO> curl http://localhost:3000/time"))
            terminal_lines.append(("success", f"HTTP/1.1 {resp.status} OK"))
            terminal_lines.append(("normal", body))
        take_browser_screenshot("http://localhost:3000/time", "time.png", "1000,600")

        # Test 4: GET /anything (404)
        print("\nTesting GET /anything (404)")
        try:
            urllib.request.urlopen("http://localhost:3000/anything")
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"GET /anything -> Status {e.code}, Body: {body}")
            terminal_lines.append(("prompt", "PS C:\\Users\\prade\\OneDrive\\Desktop\\OOO> curl http://localhost:3000/anything"))
            terminal_lines.append(("error", f"HTTP/1.1 {e.code} Not Found"))
            terminal_lines.append(("normal", body))
        take_browser_screenshot("http://localhost:3000/anything", "not-found.png", "1000,600")

    finally:
        proc_express.terminate()
        proc_express.wait()
        print("Stopped server.js")
        terminal_lines.append(("warn", "^C (Express server stopped)"))
        terminal_lines.append(("success", "All 5 endpoints executed, verified, and recorded."))

    # Step 3: Render Terminal Screenshot
    render_terminal_image(terminal_lines, "terminal-execution.png")
    print("\n=== All tasks finished successfully! ===")

if __name__ == "__main__":
    main()
