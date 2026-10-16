[app]

title = Inventario Genericos
package.name = inventariogenericos
package.domain = org.inventario

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db

version = 0.1

requirements = python3,kivy,sqlite3

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_licenses = True
android.archs = arm64-v8a
android.sdk_build_tools = 34.0.0

[buildozer]
log_level = 2
warn_on_root = 0
