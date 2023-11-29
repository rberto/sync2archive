from pathlib import Path
import argparse
from PIL import Image, ExifTags, UnidentifiedImageError
from datetime import datetime, timezone
from dateutil.parser import parse
from datetime import timedelta
import pendulum

d = timedelta(weeks=4)

archive_limit = pendulum.instance(datetime.now() - d)
print(archive_limit)

def is_file_archivable(file, date):
    print(f"{date} < {archive_limit}")
    return date < archive_limit
        

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
    except UnidentifiedImageError as e:
        print(f"{e}")
        continue
    except (TypeError, KeyError) as e:
        print(f"Could not read exif of {f}: {e}")
        continue

    date = pendulum.parse(datestr)
    #print(f"{date}    {datestr}")
    
    print(f"{f} is archivable : {is_file_archivable(f, date)}")


