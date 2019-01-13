# Easy image-net downloader and spliter

This repository contains 2 scripts:

- `dl-imgnet` to download a image-net.org image set using the ID found in the search engine
- `splitter` to split images in train and valid directories

## dl-imgnet

To use that script, go to http://image-net.org, then make a search request. For example "pizza". The website will show you several image set, you may now choose one.

Going on the result page, you now see a "wnid" in the URL. For example: "http://image-net.org/synset?wnid=n07873807"

Copy that ID, and use the command line:

```bash
./dl-imgnet.py n07873807 pizzas
```

You may provide 2 others options:

- `-d` or `--dest` to indicate the destination directory where to download images (don't provide the image class, the script concatanates the classname to the destination) - default is the current directory
- `-t` or `--timeout` to indicate how many second to set on request timeout
- `-n` or `--num-worker` to indicate how many parallel download to use. Default is set to your CPU number.

## splitter

Sometimes, you need to split train and validation images in separated directories. Splitter.py file will help you.

```bash
./splitter.py rep/to/pizzas 
```

It will create "valid" and "train" directories and copy random images from the `rep/to/pizzas` directory in both directories. The default fraction of image to send to "valid" is ".2" (20%).

You can change the options:

- `-d` or `--dest` to indicate the destination root directory where will reside "train" and "valid" directory (eg. "data", will create "data/train/pizza" for example)
- `-f` or `--frac` to a number between .1 and .9 (note that you should use recommanded values: .2 or .3)
- `-c` or `--classname` to indicate another classname that the source directory name.
