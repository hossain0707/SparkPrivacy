"""Generate local brand icons using Pillow; no proprietary fonts or icon assets."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parents[1] / "assets"
BASE.mkdir(parents=True, exist_ok=True)


def icon(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (12, 34, 48, 255))
    draw = ImageDraw.Draw(image)
    r = size / 256
    padding = int(12*r)
    draw.rounded_rectangle((padding,padding,size-padding,size-padding),radius=int(55*r),fill=(17,48,64,255),outline=(75,211,182,255),width=max(1,int(5*r)))
    shield=[(128*r,37*r),(202*r,65*r),(198*r,157*r),(172*r,193*r),(128*r,227*r),(84*r,193*r),(58*r,157*r),(54*r,65*r)]
    draw.polygon(shield,fill=(23,84,82,255))
    draw.line(shield+[shield[0]],fill=(105,232,199,255),width=max(2,int(10*r)),joint='curve')
    draw.line([(87*r,129*r),(115*r,155*r),(175*r,101*r)],fill=(218,255,244,255),width=max(4,int(13*r)),joint='curve')
    return image


def main():
    icon(512).save(BASE/'sparkprivacy-icon.png')
    icon(256).save(BASE/'sparkprivacy-icon.ico',format='ICO',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
    icon(512).save(BASE/'sparkprivacy-icon.icns',format='ICNS')
    for name in ('sparkprivacy-icon.png','sparkprivacy-icon.ico','sparkprivacy-icon.icns'):
        assert (BASE/name).stat().st_size>1000
        print(name,(BASE/name).stat().st_size)


if __name__ == '__main__':main()
