
[app]
title = ImageScraping
package.name = scrape
package.domain = com.image
android.archs = arm64-v8a
source.main = main.py
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,dm
orientation = portrait
source.include_exts = py,png,jpg,jpeg,kv,atlas,dm
fullscreen = 0
version = 0.2
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.release_artifact = apk
android.presplash_color = #FFFFFF
debug = 1
android.allow_backup = True
android.logcat = True
android.ndk = 25b
log_level = 2