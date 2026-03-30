#!/usr/bin/env python3
"""
Graph Memory Visualizer Backend
Provides API to read graph-memory SQLite database and serve data for visualization
"""

import sqlite3
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import os

class GraphMemoryHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db_path = os.path.expanduser("~/.openclaw/graph-memory.db")
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Enable CORS for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        if path == '/api/nodes':
            self.handle_get_nodes(query)
        elif path == '/api/search':
            self.handle_search(query)
        else:
            # Serve static files
            if path == '/':
                self.path = '/index.html'
            super().do_GET()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def handle_get_nodes(self, query):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get all nodes with their communities
            cursor.execute("""
                SELECT id, name, community, content 
                FROM nodes 
                ORDER BY id
            """)
            
            nodes = []
            for row in cursor.fetchall():
                nodes.append({
                    "id": row['id'],
                    "label": row['name'],
                    "group": row['community'] if row['community'] else 1,
                    "title": row['content'][:200] if row['content'] else row['name']
                })
            
            # Get all edges
            cursor.execute("""
                SELECT source_id, target_id, predicate 
                FROM edges
            """)
            
            edges = []
            for row in cursor.fetchall():
                edges.append({
                    "from": row['source_id'],
                    "to": row['target_id'],
                    "label": row['predicate']
                })
            
            # Get community count
            cursor.execute("SELECT COUNT(DISTINCT community) as cnt FROM nodes WHERE community IS NOT NULL")
            community_count = cursor.fetchone()['cnt']
            
            conn.close()
            
            response = {
                "nodes": nodes,
                "edges": edges,
                "stats": {
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "community_count": community_count or 0
                }
            }
            
            self.send_json(response)
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_search(self, query):
        try:
            search_term = query.get('q', [''])[0]
            if not search_term:
                self.send_json({"nodes": [], "edges": [], "stats": {"node_count": 0, "edge_count": 0, "community_count": 0}})
                return
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Search nodes by name or content
            cursor.execute("""
                SELECT id, name, community, content 
                FROM nodes 
                WHERE name LIKE ? OR content LIKE ?
                ORDER BY id
            """, (f'%{search_term}%', f'%{search_term}%'))
            
            nodes = []
            found_ids = set()
            for row in cursor.fetchall():
                nodes.append({
                    "id": row['id'],
                    "label": row['name'],
                    "group": row['community'] if row['community'] else 1,
                    "title": row['content'][:200] if row['content'] else row['name']
                })
                found_ids.add(row['id'])
            
            # Get edges between found nodes
            if found_ids:
                placeholders = ','.join('?' for _ in found_ids)
                cursor.execute(f"""
                    SELECT source_id, target_id, predicate 
                    FROM edges
                    WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders})
                """, list(found_ids) + list(found_ids))
                
                edges = []
                for row in cursor.fetchall():
                    edges.append({
                        "from": row['source_id'],
                        "to": row['target_id'],
                        "label": row['predicate']
                    })
            else:
                edges = []
            
            # Get community count
            cursor.execute("SELECT COUNT(DISTINCT community) as cnt FROM nodes WHERE community IS NOT NULL AND id IN ({})".format(
                ','.join('?' for _ in found_ids)
            ), list(found_ids))
            community_count = cursor.fetchone()['cnt']
            
            conn.close()
            
            response = {
                "nodes": nodes,
                "edges": edges,
                "stats": {
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "community_count": community_count or 0
                }
            }
            
            self.send_json(response)
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

def main():
    port = 8888
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, GraphMemoryHandler)
    print(f"Graph Memory Visualizer starting on http://localhost:{port}")
    print(f"Database: {os.path.expanduser('~/.openclaw/graph-memory.db')}")
    httpd.serve_forever()

if __name__ == '__main__':
    main()
