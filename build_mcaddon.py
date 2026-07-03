"""Packages Baseball_BP and Baseball_RP into Baseball_Addon.mcaddon for iOS/iPadOS
(and any platform that installs packs by opening a .mcaddon file, e.g. AirDrop/Files)."""
import os
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(ROOT, 'Baseball_Addon.mcaddon')
PACKS = ('Baseball_BP', 'Baseball_RP')


def build():
    if os.path.exists(OUTPUT):
        os.remove(OUTPUT)
    with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zf:
        for pack in PACKS:
            pack_dir = os.path.join(ROOT, pack)
            for dirpath, _dirs, files in os.walk(pack_dir):
                for f in files:
                    full = os.path.join(dirpath, f)
                    arcname = os.path.relpath(full, ROOT)
                    zf.write(full, arcname)
    size = os.path.getsize(OUTPUT)
    print(f"wrote {os.path.basename(OUTPUT)}  ({size} bytes)")


if __name__ == '__main__':
    build()
