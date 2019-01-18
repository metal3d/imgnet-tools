#! /bin/env python3
""" Helper script to download image-net.org image corresponding
to a given ID.

Author: Patrice FERLET <metal3d@gmail.com>
Licence: MIT
"""
import requests
import os
import hashlib
import imghdr
import io
import queue
import threading
import multiprocessing
import sys

CPUs = multiprocessing.cpu_count()

# LIST_URL =
# 'http://image-net.org/api/text/imagenet.synset.geturls?wnid={imid}'

LIST_URL = ''.join([
    'http://www.image-net.org/',
    'api/text/imagenet.synset.geturls.getmapping?wnid={imid}'])

SEE_URL = 'http://www.image-net.org/synset?wnid={id}'

# not wanted images, mainly for flickr bad file, hugedomain logos...
BADIMG = [
    '880a7a58e05d3e83797f27573bb6d35c',  # flickr
    '596246739a83bb45e30e13437e0810d9',  # warning sign
    '969e595182a947c7fdaaef4a34401760',  # forbiden sign
    'af5db09e39ca35d8930b4e59962e09e5',  # hugedomain logo
]
TIMEOUT = 5
DEST = './'
DATAFILE = './data.csv'


q = None
locker = threading.Lock()


def init_queue(number: int = CPUs):
    """ Initiate Queue to that number of elements """
    global q
    if q is None:
        print("Initializing Queue to %d workers" % number)
        q = queue.Queue(number)
    else:
        print('Queue already initialized')


def get_list(imid: str) -> requests.Response:
    """ Return the requests.Response containing
        the list of images for a given image-net.org
        collection ID.
    """
    imlist = requests.get(LIST_URL.format(imid=imid))
    return imlist


def logthat(content, total=None, index=None):
    """ Helper function to write logs
        with progression status.
    """
    if total is not None and index is not None:
        print('%d/%d %s' % (index+1, total, content))
    else:
        print('%s' % content)


def save_data(imname: str, url: str, classname: str, nid: str):
    locker.acquire()

    if not os.path.exists(DATAFILE):
        try:
            # append header line
            with open(DATAFILE, 'a') as f:
                f.write('Sysnet Name,Base URL,Classname,Imagenet ID\n')
        except Exception as e:
            print(e)
            sys.exit(0)

    try:
        with open(DATAFILE, 'a') as f:
            f.write('"%s",%s,"%s",%s\n' % (imname, url, classname, nid))
    except Exception as e:
        print(e)
    finally:
        locker.release()


def is_in_db(imname: str):
    """ Fetch given url in CSV file and return boolean
        saying if the file is already downloaded.
    """
    locker.acquire()
    try:
        lines = open(DATAFILE).readlines()
    except Exception:
        return False
    finally:
        locker.release()

    for l in lines:
        if imname in l:
            return True
    return False


def dl_image(
        imname: str,
        imurl: str,
        classname='unknown',
        dest='./',
        total=None,
        index=None,
        nid=None):
    """ Download image from the given url, save it as classname
        and check if the image is correct.
    """
    # imname = os.path.basename(imurl)
    # imname = imname.decode()

    # prepare the desitnation directory
    os.makedirs(os.path.join(dest, classname), exist_ok=True)

    # deactivate, use md5
    # if os.path.exists(fileto):
    #    print('File %s already downloaded, skippiing' % fileto)
    #    return

    # check if image is in csv database
    if is_in_db(imname):
        logthat('Image already downloaded, skipping', total, index)
        return

    # download image, and check status_code
    try:
        im = requests.get(imurl, timeout=TIMEOUT)
        if im.status_code != 200:
            logthat(
                'Status code is not OK for %s, %d' % (
                    imurl, im.status_code),
                total,
                index
            )
            return
    except Exception as e:
        logthat(
            'Error, connot download %s %s' % (imurl, e),
            total,
            index
        )
        return

    # is it a valid image ?
    b = io.BytesIO()
    b.write(im.content)
    b.seek(0)
    ext = imghdr.what(b)
    if ext is None:
        logthat(
            "%s seems to not be a valid image file, skipping" % imname,
            total,
            index
        )
        return

    # is it a bad image ?
    md5 = hashlib.md5(im.content).hexdigest()
    if md5 in BADIMG:
        logthat(
            imname + ' md5 corresponds to a bad image, skipping',
            total,
            index)
        return

    fileto = os.path.join(dest, classname, imname + '.' + ext)
    # md5 is ok, downloaded file is not empty, we can save it
    with open(fileto, 'wb') as f:
        f.write(im.content)
        save_data(imname, imurl, classname, nid)
        logthat("%s file saved" % imname, total, index)


def task_download():
    """ Helper function that is launched by threading.Thread.
        It reads Queue and call dl_image() in parallel.
    """
    init_queue()
    while True:
        imname, item, classname, total, index, nid = q.get()
        if item is None:
            break
        dl_image(imname, item, classname, DEST, total, index, nid)
        q.task_done()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'nid',
        help='Id of the imagenet group to download. '
             'It can be a coma separated of ids. It\'s an optionnal '
             'argument, if leaved empty, so a search is made on imagenet '
             'with the class name argument and nothing is downloaded.',
        nargs='?'
    )
    parser.add_argument(
        'name',
        help='Real classname of the images to '
             'download (it will create the corresponding directory name)'
    )
    parser.add_argument(
        '-d',
        '--dest',
        help='destination root (without classname) directory '
             'where images will be downloaded',
        default=DEST
    )
    parser.add_argument(
        '-t',
        '--timeout',
        type=int,
        help='Timeout in seconds for requests before to abandon download',
        default=TIMEOUT
    )
    parser.add_argument(
        '-n',
        '--num-worker',
        type=int,
        help='Number of worker for parallel '
             'download, use number of cpus by default',
        default=CPUs
    )
    parser.add_argument(
        '-c',
        '--csv',
        type=str,
        help='CSV file where to keep downloaded file information',
        default=DATAFILE
    )

    args = parser.parse_args()

    nids = args.nid
    classname = args.name
    NUM_WORKERS = args.num_worker
    TIMEOUT = args.timeout
    DEST = args.dest
    DATAFILE = args.csv

    if args.nid is None:
        # get words
        nids = []
        words = requests.get('http://image-net.org/archive/words.txt')
        print('You didn\'t provide ID, choose in the list')
        for line in words.iter_lines():
            nid, terms = line.decode().split('\t')
            for n in classname.split(','):
                if n in terms:
                    print(
                        nid,
                        terms,
                        "See results at: %s" % SEE_URL.format(id=nid)
                    )
        sys.exit(0)

    init_queue(NUM_WORKERS)

    threads = []
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=task_download)
        t.start()
        threads.append(t)

    lines_count = 1
    results = {}
    for nid in nids.split(','):
        nid = nid.strip()
        res = get_list(nid)
        # list is not very well formatted, we need
        # to iterate to count, and not find "\n" or whatever
        # the line delimiter
        for _ in res.iter_lines():
            lines_count += 1

        results[nid] = res

    lastidx = 0
    for nid, res in results.items():
        for u in res.iter_lines():
            u = u.decode().split(' ')
            if len(u) == 2:
                imname, u = list(u)
            else:
                continue
            q.put((imname, u, classname, lines_count, lastidx, nid))
            lastidx += 1

    q.join()

    for i in range(NUM_WORKERS):
        q.put((None, None, None, None, None, None))

    for t in threads:
        t.join()
