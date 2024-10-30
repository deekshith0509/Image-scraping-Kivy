[app]
title = ImageScraping
package.name = image
package.domain = com.scrape
android.archs = arm64-v8a
source.main = main.py
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,dm
requirements = python3,kivy,kivymd,requests,beautifulsoup4,pyjnius
orientation = portrait
fullscreen = 0
version = 0.2
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO
android.release_artifact = apk
android.presplash_color = #FFFFFF
debug = 1
android.allow_backup = True
android.logcat = True
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 31
android.ndk = 25b
log_level = 2
