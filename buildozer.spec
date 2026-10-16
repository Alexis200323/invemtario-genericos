[app]

# (str) Title of your application
title = Inventario Genericos

# (str) Package name
package.name = inventariogenericos

# (str) Package domain (needed for android packaging)
package.domain = org.inventario

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (python files and db)
source.include_exts = py,db

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,sqlite3

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API required
android.min_api = 21

# (int) Android NDK version
android.ndk = 25b

# (bool) Accept SDK licenses automatically
android.accept_sdk_licenses = True
