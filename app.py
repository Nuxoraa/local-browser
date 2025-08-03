import os
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import socket
from urllib.parse import unquote
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import qrcode
from PIL import ImageTk, Image
import io

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class LocalBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("PyWeb Creator & Browser")
        
        # Configure dark theme
        self.setup_dark_theme()
        
        # Server setup
        self.server = None
        self.server_thread = None
        self.host = self.get_local_ip()
        self.port = 8000
        self.base_url = f"http://{self.host}:{self.port}"
        
        # Sites storage
        self.sites = {}
        self.load_sites()
        
        # GUI
        self.setup_gui()
        
    def setup_dark_theme(self):
        """Configure dark theme colors"""
        self.root.tk_setPalette(background='#2d2d2d', foreground='#ffffff',
                               activeBackground='#3d3d3d', activeForeground='#ffffff')
        
        style = ttk.Style()
        style.theme_use('alt')
        
        # Configure styles
        style.configure('.', background='#2d2d2d', foreground='#ffffff')
        style.configure('TFrame', background='#2d2d2d')
        style.configure('TLabel', background='#2d2d2d', foreground='#ffffff')
        style.configure('TButton', background='#3d3d3d', foreground='#ffffff', 
                        borderwidth=1, focusthickness=3, focuscolor='none')
        style.map('TButton', background=[('active', '#4d4d4d')])
        style.configure('TEntry', fieldbackground='#3d3d3d', foreground='#ffffff')
        style.configure('TCombobox', fieldbackground='#3d3d3d', foreground='#ffffff')
        style.configure('TNotebook', background='#2d2d2d', borderwidth=0)
        style.configure('TNotebook.Tab', background='#3d3d3d', foreground='#ffffff',
                        padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#1d1d1d')])
        
        # Configure text widgets
        self.root.option_add('*Text.background', '#3d3d3d')
        self.root.option_add('*Text.foreground', '#ffffff')
        self.root.option_add('*Text.insertBackground', '#ffffff')
        self.root.option_add('*Text.selectBackground', '#4d4d4d')
        self.root.option_add('*Listbox.background', '#3d3d3d')
        self.root.option_add('*Listbox.foreground', '#ffffff')
        self.root.option_add('*Listbox.selectBackground', '#4d4d4d')
        
    def get_local_ip(self):
        """Get local IP address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip
    
    def load_sites(self):
        """Load saved sites"""
        if os.path.exists('sites.json'):
            with open('sites.json', 'r', encoding='utf-8') as f:
                self.sites = json.load(f)
    
    def save_sites(self):
        """Save sites to file"""
        with open('sites.json', 'w', encoding='utf-8') as f:
            json.dump(self.sites, f, ensure_ascii=False, indent=2)
    
    def setup_gui(self):
        """Setup the interface"""
        # Navigation panel
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(nav_frame, textvariable=self.url_var, width=50)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.go_btn = ttk.Button(nav_frame, text="Go", command=self.navigate)
        self.go_btn.pack(side=tk.LEFT)
        
        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Browser
        self.browser_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.browser_frame, text="Browser")
        
        self.browser_text = scrolledtext.ScrolledText(
            self.browser_frame, wrap=tk.WORD, width=80, height=25
        )
        self.browser_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.browser_text.insert(tk.END, "Welcome to 4SDA Creator!\n\nHere you can create and view your websites.")
        
        # Site Creator
        self.creator_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.creator_frame, text="Create Site")
        
        ttk.Label(self.creator_frame, text="Site name:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        self.site_name_var = tk.StringVar()
        self.site_name_entry = ttk.Entry(self.creator_frame, textvariable=self.site_name_var)
        self.site_name_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(self.creator_frame, text="Link (no spaces or special chars):").pack(anchor=tk.W, padx=5, pady=(5, 0))
        self.site_link_var = tk.StringVar()
        self.site_link_entry = ttk.Entry(self.creator_frame, textvariable=self.site_link_var)
        self.site_link_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(self.creator_frame, text="Content (HTML):").pack(anchor=tk.W, padx=5, pady=(5, 0))
        self.site_content_text = scrolledtext.ScrolledText(
            self.creator_frame, wrap=tk.WORD, width=80, height=15
        )
        self.site_content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.site_content_text.insert(tk.END, """<!DOCTYPE html>
<html>
<head>
    <title>My Site</title>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This is my first website.</p>
</body>
</html>""")
        
        btn_frame = ttk.Frame(self.creator_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_btn = ttk.Button(btn_frame, text="Create Site", command=self.create_site)
        self.create_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.preview_btn = ttk.Button(btn_frame, text="Preview", command=self.preview_site)
        self.preview_btn.pack(side=tk.LEFT)
        
        # My Sites
        self.my_sites_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.my_sites_frame, text="My Sites")
        
        self.sites_listbox = tk.Listbox(self.my_sites_frame)
        self.sites_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.update_sites_list()
        
        btn_frame2 = ttk.Frame(self.my_sites_frame)
        btn_frame2.pack(fill=tk.X, padx=5, pady=5)
        
        self.open_btn = ttk.Button(btn_frame2, text="Open", command=self.open_site)
        self.open_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_btn = ttk.Button(btn_frame2, text="Delete", command=self.delete_site)
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.share_btn = ttk.Button(btn_frame2, text="Share", command=self.share_site)
        self.share_btn.pack(side=tk.LEFT)
        
        # Start server
        self.start_server()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def update_sites_list(self):
        """Update sites list"""
        self.sites_listbox.delete(0, tk.END)
        for site_name in self.sites:
            self.sites_listbox.insert(tk.END, f"{site_name} ({self.sites[site_name]['link']})")
    
    def start_server(self):
        """Start local server"""
        handler = lambda *args: SimpleHTTPRequestHandler(*args, directory=os.getcwd())
        self.server = ThreadedHTTPServer(('0.0.0.0', self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Create sites directory if it doesn't exist
        if not os.path.exists('sites'):
            os.makedirs('sites')
    
    def navigate(self):
        """Navigate to URL"""
        url = self.url_var.get().strip()
        if not url:
            return
            
        if url.startswith('http://') or url.startswith('https://'):
            webbrowser.open(url)
        else:
            # Check if this is a local site
            for site in self.sites.values():
                if site['link'] == url:
                    self.show_site_content(site['content'])
                    return
            
            # Try adding http://
            if '.' in url:  # Looks like a domain
                webbrowser.open(f'http://{url}')
            else:
                messagebox.showerror("Error", "Site not found. Please create it first.")
    
    def show_site_content(self, content):
        """Show site content in browser"""
        self.browser_text.delete(1.0, tk.END)
        self.browser_text.insert(tk.END, content)
    
    def create_site(self):
        """Create new site"""
        site_name = self.site_name_var.get().strip()
        site_link = self.site_link_var.get().strip()
        content = self.site_content_text.get(1.0, tk.END).strip()
        
        if not site_name or not site_link or not content:
            messagebox.showerror("Error", "All fields must be filled!")
            return
            
        if ' ' in site_link or not site_link.isalnum():
            messagebox.showerror("Error", "Link must contain only letters and numbers without spaces!")
            return
            
        # Check if site with this link already exists
        for existing_site in self.sites.values():
            if existing_site['link'] == site_link:
                messagebox.showerror("Error", "Site with this link already exists!")
                return
        
        # Save site
        self.sites[site_name] = {
            'link': site_link,
            'content': content
        }
        
        # Save HTML file
        with open(f'sites/{site_link}.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.save_sites()
        self.update_sites_list()
        messagebox.showinfo("Success", f"Site '{site_name}' created! Available at: {self.base_url}/sites/{site_link}.html")
        
        # Clear fields
        self.site_name_var.set('')
        self.site_link_var.set('')
        self.site_content_text.delete(1.0, tk.END)
    
    def preview_site(self):
        """Preview site"""
        content = self.site_content_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showerror("Error", "No content to preview!")
            return
            
        # Create temporary file
        temp_file = 'temp_preview.html'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Open in browser
        webbrowser.open(f'{self.base_url}/{temp_file}')
    
    def open_site(self):
        """Open selected site"""
        selection = self.sites_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a site from the list!")
            return
            
        site_name = self.sites_listbox.get(selection[0]).split(' (')[0]
        site = self.sites[site_name]
        
        # Show in browser
        self.url_var.set(f"{self.base_url}/sites/{site['link']}.html")
        self.show_site_content(site['content'])
    
    def delete_site(self):
        """Delete selected site"""
        selection = self.sites_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a site from the list!")
            return
            
        site_name = self.sites_listbox.get(selection[0]).split(' (')[0]
        
        # Delete file
        site_link = self.sites[site_name]['link']
        if os.path.exists(f'sites/{site_link}.html'):
            os.remove(f'sites/{site_link}.html')
        
        # Remove from list
        del self.sites[site_name]
        self.save_sites()
        self.update_sites_list()
        messagebox.showinfo("Success", "Site deleted!")
    
    def share_site(self):
        """Show QR code and link for sharing"""
        selection = self.sites_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Choose a site from the list!")
            return
            
        site_name = self.sites_listbox.get(selection[0]).split(' (')[0]
        site_link = self.sites[site_name]['link']
        
        share_url = f"{self.base_url}/sites/{site_link}.html"
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(share_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="white", back_color="#2d2d2d")
        
        # Convert for Tkinter
        img_tk = ImageTk.PhotoImage(img)
        
        # Create window to show QR code
        share_window = tk.Toplevel(self.root)
        share_window.title(f"Share: {site_name}")
        
        # QR code
        qr_label = tk.Label(share_window, image=img_tk)
        qr_label.image = img_tk  # Keep reference
        qr_label.pack(padx=10, pady=10)
        
        # Link
        link_frame = ttk.Frame(share_window)
        link_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(link_frame, text="Link:").pack(side=tk.LEFT)
        
        link_var = tk.StringVar(value=share_url)
        link_entry = ttk.Entry(link_frame, textvariable=link_var, width=40)
        link_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        copy_btn = ttk.Button(link_frame, text="Copy", command=lambda: self.root.clipboard_append(share_url))
        copy_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Instructions
        ttk.Label(share_window, text="Scan the QR code or send the link to others.").pack(padx=10, pady=(0, 10))
        ttk.Label(share_window, text="Your computer must be on the same network as other users.").pack(padx=10, pady=(0, 10))
    
    def on_close(self):
        """Handle window closing"""
        if self.server:
            self.server.shutdown()
            self.server_thread.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LocalBrowser(root)
    root.mainloop()
