import argostranslate.package

# 假設檔案已下載到當前資料夾
with open("langpacks/translate-en_zt-1_9.argosmodel", "rb") as f:
    argostranslate.package.install_from_path(f)

with open("langpacks/translate-zt_en-1_9.argosmodel", "rb") as f:
    argostranslate.package.install_from_path(f)
