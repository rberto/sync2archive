from pathlib import Path
import argparse
from PIL import Image, ExifTags, UnidentifiedImageError
from datetime import datetime, timezone
from dateutil.parser import parse

parser = argparse.ArgumentParser(
                    prog='Sync2Archive',
                    description='',
                    epilog='')

parser.add_argument('syncfolder')           # positional argument
#parser.add_argument('destfolder')           # positional argument

args = parser.parse_args()

p = Path(args.syncfolder)
files = [x for x in p.iterdir() if x.is_file()]

for f in files:
    try:
        img = Image.open(f)
        datestr = str(img._getexif()[ExifTags.Base.DateTime])
        date = parse(datestr)
    except UnidentifiedImageError as e:
        print(f"Could not open file {f}: {e}")
    except (TypeError, KeyError) as e:
        print(f"Could not read exif of {f}: {e}")

    