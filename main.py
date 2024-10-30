from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import threading
import re

# Request headers to mimic browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class ImageDownloaderScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Title
        title = MDLabel(
            text="Web Image Downloader",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=50
        )
        
        # URL Input
        self.url_input = MDTextField(
            hint_text="Enter URL",
            mode="rectangle",
            helper_text="Enter the webpage URL",
            helper_text_mode="on_error"
        )
        
        # Number Input
        self.number_input = MDTextField(
            hint_text="Number of images",
            mode="rectangle",
            helper_text="Enter number of images to download",
            helper_text_mode="on_error",
            input_filter="int"
        )
        
        # Download Button
        self.download_btn = MDRaisedButton(
            text="Download Images",
            size_hint=(None, None),
            width=200,
            height=50,
            pos_hint={'center_x': 0.5}
        )
        self.download_btn.bind(on_release=self.start_download)
        
        # Status Label
        self.status_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Secondary"
        )
        
        # Add widgets to layout
        layout.add_widget(title)
        layout.add_widget(self.url_input)
        layout.add_widget(self.number_input)
        layout.add_widget(self.download_btn)
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def validate_inputs(self):
        url = self.url_input.text.strip()
        num_images = self.number_input.text.strip()
        
        if not url:
            self.url_input.error = True
            self.url_input.helper_text = "URL is required"
            return False
            
        if not num_images:
            self.number_input.error = True
            self.number_input.helper_text = "Number is required"
            return False
            
        try:
            num = int(num_images)
            if num <= 0:
                self.number_input.error = True
                self.number_input.helper_text = "Number must be positive"
                return False
        except ValueError:
            self.number_input.error = True
            self.number_input.helper_text = "Invalid number"
            return False
            
        return True
    
    def start_download(self, instance):
        if not self.validate_inputs():
            return
            
        self.download_btn.disabled = True
        self.status_label.text = "Starting download..."
        
        # Start download in separate thread
        threading.Thread(target=self.download_images).start()
    
    def update_status(self, text):
        def update(dt):
            self.status_label.text = text
            if "completed" in text.lower() or "error" in text.lower():
                self.download_btn.disabled = False
        Clock.schedule_once(update)
    
    def download_images(self):
        try:
            url = self.url_input.text.strip()
            num_images = int(self.number_input.text.strip())
            
            # Create downloads directory
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
                download_path = '/storage/emulated/0/Download/WebImages'
            else:
                download_path = 'downloads'
                
            os.makedirs(download_path, exist_ok=True)
            
            # Get webpage content
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find image URLs
            image_urls = []
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src:
                    # Convert relative URLs to absolute
                    image_url = urljoin(url, src)
                    # Filter out small icons, base64 images, etc.
                    if (not image_url.startswith('data:') and 
                        any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])):
                        image_urls.append(image_url)
            
            if not image_urls:
                self.update_status("No images found on the webpage")
                return
                
            # Limit to requested number
            image_urls = image_urls[:num_images]
            
            # Download images
            for i, image_url in enumerate(image_urls, 1):
                try:
                    self.update_status(f"Downloading image {i}/{len(image_urls)}...")
                    
                    response = requests.get(image_url, headers=HEADERS)
                    response.raise_for_status()
                    
                    # Generate filename from URL
                    filename = os.path.basename(urlparse(image_url).path)
                    if not filename or '.' not in filename:
                        filename = f"image_{i}.jpg"
                    
                    # Ensure unique filename
                    filepath = os.path.join(download_path, filename)
                    base, ext = os.path.splitext(filepath)
                    counter = 1
                    while os.path.exists(filepath):
                        filepath = f"{base}_{counter}{ext}"
                        counter += 1
                    
                    # Save image
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                        
                except Exception as e:
                    self.update_status(f"Error downloading image {i}: {str(e)}")
                    continue
            
            self.update_status(f"Download completed! {len(image_urls)} images saved to {download_path}")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")

class ImageDownloaderApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return ImageDownloaderScreen()

if __name__ == '__main__':
    ImageDownloaderApp().run()
