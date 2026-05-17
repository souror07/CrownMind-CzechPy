[app]

# Application name
title = CrownMind Checkers

# Package name
package.name = crownmind_checkers

# Package domain
package.domain = org.souror.checkers

# Source files
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Version
version = 1.0

# Requirements
requirements = python3,kivy,pillow

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Architecture
android.archs = arm64-v8a,armeabi-v7a

# Icons and permissions
android.api = 31
android.minapi = 21
android.ndk = 25b

# Orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Android specific
android.gradle_dependencies = 
android.add_src = 

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Display warning
warn_on_root = 1
