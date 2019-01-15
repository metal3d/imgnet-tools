# Easy image-net downloader and splitter

## What is it ?

Image-net.org provides millions of images that are classified by type, names... This is a fabulous data source to be able to make machine learning and image recognition. This repositoy provides tools to download and split data coming from image-net website.

This repository contains 2 scripts:

- `dl-imgnet.py` to download a image-net.org image set using the ID found in the search engine
- `splitter.py` to split images in train and valid directories

Note that the `dl-imgnet` script makes some generic tests:

- is the image a real "image" ?
- is it a known "bad image" (for example, sometimes, flickr returns a "logo" to say that image is not found, with a 200 status code)

That's mainly why I created that script: to be able to download images and avoid bad files

Any help, ideas, fixes, and so on... are gracefully appreciated :)


## Requirements

- Python 3
- Pip 3 (to install requirements if your package manager doesn't provide `python3-requests`)
- Requests package
- Internt connection...

As you need "requests" package, it's recommended to use you package manager to install the python3 package:

```bash
# Fedora, CentOS, Red Hat Like...
sudo dnf install python3-requests

# Debian like, Ubuntu...
sudo apt install python3-requests
```

If you cannot install the required pacakge with your package manager, I provide a minimal requirements file, so just type:

```bash
pip3 install -r requirements.txt
```

# Usage

## dl-imgnet

To use that script, go to http://image-net.org, then make a search request. For example "pizza". The website will show you several image set, you may now choose one.

Going on the result page, you now see a "wnid" in the URL. For example: "http://image-net.org/synset?wnid=n07873807"

Copy that ID, and use the command line:

```bash
./dl-imgnet.py n07873807 pizzas
```

You may use a list of IDs, if you want to merge several classification (eg. French Fries on imagenet site is splitted in 2 classes):

```
./dl-imgnet.py n07711080,n07711232 fries
```

**Note** the script will create a CSV file keeping downloaded image urls, md5 sum of the file, the classname and the "id" of imagenet class. This is usefull to not download already downloeded files and to keep the source of images. This file is named `data.csv` and can be changed with `-c` argument.

**Note** also, the script save image with name template `<md5sum>.<type>`, the type is defined by `imghdr.what()` function (python3 standard). That way, it's possible to have several URL having the same image name, but not the same content.

It will create a `pizzas` directory and download all valid images inside. You can change the destination:

```bash
./dl-imgnet.py n07873807 pizzas -d base
```

This will create a `base/pizzas` directory and use it to downoad images.

You may provide others options:

- `-d` or `--dest` to indicate the destination directory where to download images (don't provide the image class, the script concatanates the classname to the destination) - default is the current directory
- `-t` or `--timeout` to indicate how many second to set on request timeout
- `-n` or `--num-worker` to indicate how many parallel download to use. Default is set to your CPU number.
- `-c` or `--csv` path to the CSV file where to keep downloaded images information

## splitter

Sometimes, you need to split train and validation images in separated directories. Splitter.py file will help you.

```bash
./splitter.py rep/to/pizzas 
```

It will create "valid" and "train" directories and copy random images from the `rep/to/pizzas` directory in both directories. The default fraction of image to send to "valid" is ".2" (20%).

`train.csv` and `valid.csv` are also written in the destination directory. If you launch again the splitter, so that files are **updated** to append others classes/files. You'll need to delete the CSV files if you want a new clean list. This is not the same behaviour with the `--all` option that removes CSV files before to recreate them.

You can tell `splitter` to split the entire classes from a "base" directory:

```bash
./splitter.py rep/without/class -a
```

This will find the entire class list and split them in "train" and "valid" directories. Note that in that case, the CSV files are **deleted** before to be rewritten !

You may want to not copy images and only want CSV files (`train.csv` and `valid.csv`), so you can use `-C` or `--csv-only` option.

One more time, you can change destination and/or fraction to split:

```bash
./splitter.py base/pizzas -d data -f .3
```

This time, it split pizza images with 30% for validation, and images are copied in `data/valid/pizzas` and `data/train/pizzas`.

**Of course, you can split several "base", it will not remove the other directories.**

You can change the options:

- `-a` or `--all` to split the whole class list found in SRC directory.
- `-C` or `--csv-only` will not copy images in destination, only create the CSV files containing filename and classname.
- `-d` or `--dest` to indicate the destination root directory where will reside "train" and "valid" directory (eg. "data", will create "data/train/pizza" for example)
- `-f` or `--frac` to a number between .1 and .9 (note that you should use recommended values: .2 or .3)
- `-c` or `--classname` to indicate another classname that the source directory name.
