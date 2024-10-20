from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import platform

import os
import threading
import requests
from bs4 import BeautifulSoup
import random

# Define user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
]

class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        if platform == 'linux':
            self.check_permissions()

    def setup_ui(self):
        layout = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

        title = MDLabel(
            text="Android Image Scraper",
            halign="center",
            theme_text_color="Primary",
            font_style="H5"
        )
        layout.add_widget(title)

        self.url_input = MDTextField(
            hint_text="Enter URL",
            helper_text="e.g., https://example.com",
            helper_text_mode="on_focus",
            size_hint_x=None,
            width=300
        )
        layout.add_widget(self.url_input)

        self.num_input = MDTextField(
            hint_text="Number of images",
            helper_text="Enter a positive integer",
            helper_text_mode="on_focus",
            size_hint_x=None,
            width=300
        )
        layout.add_widget(self.num_input)

        self.download_button = MDRaisedButton(
            text="Download Images",
            on_release=self.download_images,
            md_bg_color=self.theme_cls.primary_color
        )
        layout.add_widget(self.download_button)

        self.progress_bar = MDProgressBar(
            size_hint_x=1,
            max=100,
            value=0
        )
        layout.add_widget(self.progress_bar)

        self.status_label = MDLabel(
            text="Status: Ready",
            halign="center",
            theme_text_color="Secondary"
        )
        layout.add_widget(self.status_label)

        scroll = MDScrollView(size_hint=(1, None), size=(300, 200))
        self.log_label = MDLabel(
            size_hint_y=None,
            markup=True
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        scroll.add_widget(self.log_label)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def check_permissions(self):
        if platform == 'linux': ##########################experimental android has to be replaced.
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET])

    def get_download_folder(self):
        if platform == 'linux':
            return '/sdcard/Download/scraped_images'
        else:
            return os.path.join(os.path.expanduser('~'), 'Downloads', 'scraped_images')

    def download_images(self, *args):
        url = self.url_input.text.strip()
        num_images = self.num_input.text.strip()
        num_images = str(int(num_images) +1)

        if not url or not num_images.isdigit() or int(num_images) <= 0:
            self.update_log("Please enter a valid URL and number of images.", 'error')
            return

        num_images = int(num_images)
        self.update_log("Preparing to download images...", 'info')
        self.progress_bar.value = 0

        threading.Thread(target=self.download_images_thread, args=(url, num_images)).start()

    def download_images_thread(self, url, max_images):
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            headers = {
                'User-Agent': self.get_random_user_agent()
            }
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                self.update_log(f"Failed to retrieve the webpage. Status code: {response.status_code}", 'error')
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            image_urls = []

            # Find all <img> and <source> tags
            image_elements = soup.find_all('img')
            for img in image_elements:
                image_url = img.get('src')
                if image_url:
                    if not image_url.startswith(('http://', 'https://')):
                        image_url = f"{url.rstrip('/')}/{image_url.lstrip('/')}"
                    image_urls.append(image_url)

            source_elements = soup.find_all('source')
            for src in source_elements:
                image_url = src.get('srcset')
                if image_url:
                    image_urls.extend(image_url.split(','))

            if not image_urls:
                for img in image_elements:
                    image_url = img.get('data-src')
                    if image_url:
                        if not image_url.startswith(('http://', 'https://')):
                            image_url = f"{url.rstrip('/')}/{image_url.lstrip('/')}"
                        image_urls.append(image_url)

            self.update_log(f"Found {len(image_urls)} images.", 'info')

            if not image_urls:
                self.update_log("No images found at the specified URL.", 'error')
                return

            # Download images in batches
            self.download_images_in_batches(image_urls, max_images)

        except requests.exceptions.RequestException as e:
            self.update_log(f"Network error: {str(e)}", 'error')
        except Exception as e:
            self.update_log(f"An unexpected error occurred: {str(e)}", 'error')

    def download_images_in_batches(self, image_urls, max_images):
        folder = self.get_download_folder()
        if not os.path.exists(folder):
            os.makedirs(folder)

        batch_size = 10  # Define the number of images to download at once
        total_downloaded = 0
        
        # Calculate number of complete batches and remaining images
        complete_batches, remaining = divmod(max_images, batch_size)

        # Process complete batches
        for batch_index in range(complete_batches):
            batch = image_urls[total_downloaded:total_downloaded + batch_size]
            for url in batch:
                try:
                    self.download_image(url, folder)
                    total_downloaded += 1
                    self.update_log(f"Downloaded image {total_downloaded}/{max_images}", 'success')
                except Exception as e:
                    self.update_log(f"Failed to download {url}: {str(e)}", 'error')

            # Update progress bar in the Kivy UI
            self.update_progress(total_downloaded, max_images)

        # Process any remaining images individually
        for i in range(remaining):
            if total_downloaded >= max_images:
                break
            url = image_urls[total_downloaded]
            try:
                self.download_image(url, folder)
                total_downloaded += 1
                self.update_log(f"Downloaded image {total_downloaded}/{max_images-1}", 'success')
            except Exception as e:
                self.update_log(f"Failed to download {url}: {str(e)}", 'error')

            # Update progress bar in the Kivy UI
            self.update_progress(total_downloaded, max_images)

        self.update_log(f"Downloaded {total_downloaded} images successfully!", 'success')
        self.update_log(f"Images are stored at: {folder}", 'info')

    def download_image(self, url, folder):
        try:
            headers = {
                'User-Agent': self.get_random_user_agent()
            }
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()

            image_name = os.path.join(folder, os.path.basename(url))
            with open(image_name, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
        except Exception as e:
            raise RuntimeError(f"Error downloading {url}: {str(e)}")

    def update_progress(self, downloaded, total):
        progress = (downloaded / total) * 100 if total > 0 else 0
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', progress))

    def update_log(self, message, level='info'):
        log_text = self.log_label.text
        if level == 'success':
            log_text += f"[color=00FF00]{message}[/color]\n"  # Green for success
        elif level == 'error':
            log_text += f"[color=FF0000]{message}[/color]\n"  # Red for error
        else:
            log_text += f"[color=FFFFFF]{message}[/color]\n"  # White for info
        Clock.schedule_once(lambda dt: setattr(self.log_label, 'text', log_text))

    def get_random_user_agent(self):
        return random.choice(USER_AGENTS)

class ImageScraperApp(MDApp):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    ImageScraperApp().run()
