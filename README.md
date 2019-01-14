# Easy image-net downloader and splitter

This repository contains 2 scripts:

- `dl-imgnet.py` to download a image-net.org image set using the ID found in the search engine
- `splitter.py` to split images in train and valid directories

Note that the `dl-imgnet` script makes some generic tests:

- is the image a real "image" ?
- is it a known "bad image" (for example, sometimes, flickr returns a "logo" to say that image is not found, with a 200 status code)

That's mainly why I created that script: to be able to download images and avoid bad files

Any help, ideas, fixes, and so on... are gracefully appreciated :)

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

One more time, you can change destination and/or fraction to split:

```bash
./splitter.py base/pizzas -d data -f .3
```

This time, it split pizza images with 30% for validation, and images are copied in `data/valid/pizzas` and `data/train/pizzas`.

**Of course, you can split several "base", it will not remove the other directories.**

You can change the options:

- `-d` or `--dest` to indicate the destination root directory where will reside "train" and "valid" directory (eg. "data", will create "data/train/pizza" for example)
- `-f` or `--frac` to a number between .1 and .9 (note that you should use recommanded values: .2 or .3)
- `-c` or `--classname` to indicate another classname that the source directory name.
