import re

with open("ulaz.txt", "r", encoding="utf-8") as f:
    html = f.read()


linkovi = re.findall(r'href="([^"]+)"', html)


with open("linkovi.txt", "w", encoding="utf-8") as f:
    for link in linkovi:
        f.write(f"https://zse.hr{link}\n")

print(f"Gotovo! Nađeno {len(linkovi)} linkova i spremljeno u linkovi.txt")
