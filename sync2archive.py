from pathlib import Path
import argparse
from PIL import Image, ExifTags, UnidentifiedImageError
import pendulum


nb_moved_files = {}

def is_file_archivable(file, date):
    return date < archive_limit

def count_moved_files(folder_name):
    if folder_name in nb_moved_files.keys():
        nb_moved_files[folder_name] += 1
    else:
        nb_moved_files[folder_name] = 1

parser = argparse.ArgumentParser(
                    prog='Sync2Archive',
                    description='',
                    epilog='')

parser.add_argument('syncfolder')           # positional argument
parser.add_argument('destfolder')           # positional argument
parser.add_argument('-f', '--force', action='store_false')
parser.add_argument('-l', '--limit', type = int, default = 4, help="limit in month before now for the files to be archived.")

args = parser.parse_args()

archive_limit = pendulum.now().subtract(months = args.limit)

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

    if is_file_archivable(f, date):
        folder_name = f"{date.year}-{date.month:02d}"
        archive_folder = Path(args.destfolder, folder_name)
        archive_path = Path(archive_folder, f.name)

        count_moved_files(folder_name)
        print(f"Move {f} to {archive_path}")

        if args.force:
            archive_folder.mkdir(parents = True, exist_ok=True)
            f.rename(archive_path)   

for folder, nb in nb_moved_files.items():
    print(f"Moved {nb} files to {folder}")