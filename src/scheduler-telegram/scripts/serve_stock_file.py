from http.server import SimpleHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone, timedelta
import os

HOST="0.0.0.0"
PORT = 5567
FILENAME = "stock-update.txt"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(SCRIPT_DIR, FILENAME)

# Global cache variables to track state
cached_mtime = None
cached_html_response = None

# Define Indian Standard Time (IST) offset: UTC + 5:30
IST_TIMEZONE = timezone(timedelta(hours=5, minutes=30))

def convert_mtime_to_ist(mtime_float):
    """Converts OS modification time float into a formatted IST string."""
    try:
        # Create a datetime object from the OS timestamp in UTC, then shift to IST
        utc_dt = datetime.fromtimestamp(mtime_float, tz=timezone.utc)
        ist_dt = utc_dt.astimezone(IST_TIMEZONE)
        # Format: "DD-May-YYYY HH:MM:SS AM/PM IST"
        return ist_dt.strftime("%d-%b-%Y %I:%M:%S %p IST")
    except Exception:
        return "Unknown Modification Time"

class FileChangeHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global cached_mtime, cached_html_response

        if self.path == '/':
            # 1. Fallback if the file does not exist
            if not os.path.exists(FILE_PATH):
                self.send_error_response(f"Error: '{FILENAME}' not found at {FILE_PATH}.")
                return

            try:
                # 2. Get the exact OS modification timestamp of the file
                current_mtime = os.path.getmtime(FILE_PATH)

                # 3. Check if the file modification time matches our cache
                if cached_mtime is not None and current_mtime == cached_mtime:
                    print(f"[OS Match] Cache HIT - File unchanged. Serving cached layout.")
                    self.send_html_response(cached_html_response)
                    return

                # 4. Cache MISS - File was modified on disk. Re-read and rebuild HTML.
                print(f"[OS Diff] Cache MISS - File modified. Reloading content...")
                
                with open(FILE_PATH, 'r', encoding='utf-8') as file:
                    full_content = file.read()

                # Convert the OS system modification timestamp into a readable IST format
                readable_ist_time = convert_mtime_to_ist(current_mtime)

                # Build the fresh HTML response
                fresh_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <meta http-equiv="X-UA-Compatible" content="IE=edge" />
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                <meta name="description" content="Sanskrit Dictionary App" />
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <title>OS Tracking Text File Viewer</title>
                    <style>
                        body {{ font-family: sans-serif; margin: 0px; background: #eef2f3; }}
                        .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                        .meta-info {{ background: #e8f4fd; padding: 12px; border-radius: 6px; margin-bottom: 20px; font-size: 14px; border-left: 5px solid #3498db; }}
                        .timestamp-title {{ font-weight: bold; color: #2c3e50; }}
                        .time-value {{ color: #2980b9; font-weight: bold; }}
                        pre {{ white-space: pre-wrap; font-size: 16px; line-height: 1.5; color: #333; background: #f8f9fa; padding: 15px; border-radius: 4px; border: 1px solid #e1e4e6; }}
                    </style>
                    <script
                        type="module"
                        src="https://cdn.jsdelivr.net/npm/zero-md@3?register"
                    ></script>
                </head>
                <body>
                    <div class="container">
                        <h1>Stock Performance</h1>
                        
                        <div class="meta-info">
                            <span class="timestamp-title">Last Modified on Disk (IST):</span> 
                            <span class="time-value">{readable_ist_time}</span>
                        </div>                        
                        <hr>
                        <!--pre>{full_content}</pre-->
                        <pre><zero-md><script type="text/markdown">{full_content}</script></zero-md></pre>
                    </div>
                </body>
                </html>
                """

                # Update our global cache states
                cached_mtime = current_mtime
                cached_html_response = fresh_html.encode('utf-8')

                # Serve the fresh layout
                self.send_html_response(cached_html_response)

            except Exception as e:
                self.send_error_response(f"Server Error: {str(e)}")
        else:
            super().do_GET()

    def send_html_response(self, html_bytes):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        # Ensure the web browser does not keep its own copy and forces a server check
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.end_headers()
        self.wfile.write(html_bytes)

    def send_error_response(self, error_message):
        self.send_response(500)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(error_message.encode('utf-8'))

if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), FileChangeHandler)
    print(f"Server started at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
