from argparse import ArgumentParser
from pathlib import Path
import pendulum
from PIL import Image, ExifTags, UnidentifiedImageError
import s3fs
import ffmpeg
import magic

from dotenv import dotenv_values

config = dotenv_values(".env")
print(config)

s3 = s3fs.S3FileSystem(
      key=config["key"],
      secret=config["secret"],
      endpoint_url=config["endpoint_url"],
      client_kwargs={
      'region_name': 'GRA'
        },
        config_kwargs={
      'signature_version': 's3v4'
        }
   )

nb_moved_files = {}

def is_file_archivable(file, date):
    return date < archive_limit

def count_moved_files(folder_name):
    if folder_name in nb_moved_files.keys():
        nb_moved_files[folder_name] += 1
    else:
        nb_moved_files[folder_name] = 1

parser = ArgumentParser(prog='Sync2Archive',
                        description='',
                        epilog='')

parser.add_argument('syncfolder')           # positional argument
parser.add_argument('destfolder')           # positional argument
parser.add_argument('-f', '--force', action='store_true')
parser.add_argument('-l', '--limit', type = int, default = 4, help="limit in month before now for the files to be archived.")

args = parser.parse_args()

archive_limit = pendulum.now().subtract(months = args.limit)

p = Path(args.syncfolder)
files = [x for x in p.iterdir() if x.is_file()]
nbfiles = len(files)

for idx, f in enumerate(files):

    datestr = ""
    print(f"{idx}/{nbfiles}")

    mime = magic.from_file(f, mime=True)

    if "image" in mime:
        try:
            img = Image.open(f)
            datestr = str(img._getexif()[ExifTags.Base.DateTime])
        except UnidentifiedImageError as e:
            print(f"{e}")
            continue
        except (TypeError, KeyError) as e:
            print(f"Could not read exif of {f}: {e}")
            continue
    elif "video" in mime:
        try:
            datestr = ffmpeg.probe(f)["streams"][0]["tags"]["creation_time"]
        except (KeyError) as e:
            print(f"{e}")
            continue
    else:
        print(f"{mime} type not supported: {f}")

    date = pendulum.parse(datestr)

    if is_file_archivable(f, date):
        folder_name = f"{date.year}-{date.month:02d}"
        archive_folder = Path(args.destfolder, folder_name)
        archive_path = Path(archive_folder, f.name)

        count_moved_files(folder_name)
        
        print(f"Move {f} to s3:{Path('photo-archive', folder_name, f.name)}")
        if args.force:
            s3.put_file(Path(f), Path("photo-archive", folder_name, f.name))
            pass

        if s3.exists(Path("photo-archive", folder_name, f.name)):
            print(f"Move {f} to {archive_path}")
            if args.force:
                archive_folder.mkdir(parents = True, exist_ok=True)
                f.rename(archive_path)

for folder, nb in nb_moved_files.items():
    print(f"Moved {nb} files to {folder}")