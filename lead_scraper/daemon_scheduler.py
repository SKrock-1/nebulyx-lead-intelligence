"""
daemon_scheduler.py
Autonomous 24/7 Production Daemon for Nebulyx:
1. Spawns and manages the HTTP server (port 8088) in a dedicated thread.
2. Periodically executes autonomous marketplace scouting sweeps (Reels Stream, Explore, Hashtags, Dorks)
   every N minutes in the background.
3. Automatically ingests, classifies, and enriches new buyer leads with Sellbird intelligence.
"""

import os
import sys
import time
import threading
import argparse
from http.server import HTTPServer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from server import NebulyxLeadHandler, PORT
from marketplace_scout import InstagramMarketplaceScout

class NebulyxProductionDaemon:
    def __init__(self, port=8088, scout_interval_minutes=45):
        self.port = port
        self.scout_interval_seconds = scout_interval_minutes * 60
        self.is_running = True
        self.scout = InstagramMarketplaceScout(headless=True)

    def start_http_server(self):
        """Runs the HTTP REST API & Dashboard in a persistent background thread."""
        server = HTTPServer(("0.0.0.0", self.port), NebulyxLeadHandler)
        print(f"\n🚀 [Nebulyx Production Daemon]: HTTP Server listening on http://0.0.0.0:{self.port}/")
        print(f"👉 Dashboard available at: http://localhost:{self.port}/dashboard.html")
        server.serve_forever()

    def run_scout_loop(self):
        """Runs periodic autonomous sweeps in the background."""
        modes = ["omni", "dorks", "reels", "hashtags"]
        cycle = 0

        # Initial rest to allow server to bind cleanly
        time.sleep(5)

        while self.is_running:
            selected_mode = modes[cycle % len(modes)]
            print(f"\n🦅 [Daemon Scheduler Cycle #{cycle+1}]: Executing scheduled scout (Mode: {selected_mode})...")
            try:
                if selected_mode == "dorks":
                    self.scout.scout_dorks(limit=6)
                elif selected_mode == "reels":
                    self.scout.scout_reels_stream(max_reels=10)
                elif selected_mode == "hashtags":
                    self.scout.scout_demand_hashtags(max_per_tag=3)
                else:
                    self.scout.omni_scout(reels_limit=8, explore_limit=8, tags_limit=2)
                print(f"✅ [Daemon Scheduler]: Cycle #{cycle+1} completed successfully.")
            except Exception as e:
                print(f"⚠️ [Daemon Scheduler]: Cycle error: {e}")

            cycle += 1
            print(f"⏳ Next autonomous scout sweep scheduled in {self.scout_interval_seconds // 60} minutes...\n")
            time.sleep(self.scout_interval_seconds)

    def launch(self):
        # 1. Start Server Thread
        server_thread = threading.Thread(target=self.start_http_server, daemon=True)
        server_thread.start()

        # 2. Start Scout Loop
        try:
            self.run_scout_loop()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Nebulyx Production Daemon...")
            self.is_running = False

def main():
    parser = argparse.ArgumentParser(description="Nebulyx Production 24/7 Daemon")
    parser.add_argument("--port", type=int, default=8088, help="Server port")
    parser.add_argument("--interval", type=int, default=45, help="Scout interval in minutes")
    args = parser.parse_args()

    daemon = NebulyxProductionDaemon(port=args.port, scout_interval_minutes=args.interval)
    daemon.launch()

if __name__ == "__main__":
    main()
