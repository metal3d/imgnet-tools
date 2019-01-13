#! /bin/env python3
import requests
import os
import hashlib
import imghdr
import io
import queue
import threading
import multiprocessing

CPUs = multiprocessing.cpu_count()

LIST_URL = 'http://image-net.org/api/text/imagenet.synset.geturls?wnid={imid}'

# not wanted images, mainly for flickr bad file, hugedomain logos...
BADIMG = [
    '880a7a58e05d3e83797f27573bb6d35c',  # flickr
    '596246739a83bb45e30e13437e0810d9',  # warning sign
    '969e595182a947c7fdaaef4a34401760',  # forbiden sign
    'af5db09e39ca35d8930b4e59962e09e5',  # hugedomain logo
]
TIMEOUT = 5
DEST = './'

q = queue.Queue(CPUs)


def get_list(imid):
    imlist = requests.get(LIST_URL.format(imid=imid))
    return imlist


def dl_image(imurl, classname='unknown', dest='./'):
    imname = os.path.basename(imurl)
    imname = imname.decode()

    os.makedirs(os.path.join(dest, classname), exist_ok=True)

    fileto = os.path.join(dest, classname, imname)

    print('Check image name', imname)

    if os.path.exists(fileto):
        print('File %s already downloaded, skippiing' % fileto)
        return

    try:
        im = requests.get(imurl, timeout=TIMEOUT)
        if im.status_code != 200:
            print('Status code is not OK for %s, %d' % (imurl, im.status_code))
            return
    except Exception as e:
        print('Error, connot download', imurl, e)
        return

    # is it a read image ?
    b = io.BytesIO()
    b.write(im.content)
    b.seek(0)
    if imghdr.what(b) is None:
        print("%s seems to not be a valid image file, skipping" % imname)
        return

    # checking md5 of known bad files
    hhs = hashlib.md5(im.content).hexdigest()
    for md in BADIMG:
        if md == hhs:
            print('image %s seems to be a "bad file"' % fileto)
            return

    # md5 is ok, downloaded file is not empty, we can save it
    with open(fileto, 'wb') as f:
        f.write(im.content)
        print("%s file saved" % imname)


def task_download():
    while True:
        item, classname = q.get()
        if item is None:
            break
        dl_image(item, classname, DEST)
        q.task_done()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'nid',
        help='Id of the imagenet group to download')
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
        default='.'
    )
    parser.add_argument(
        '-t',
        '--timeout',
        type=int,
        help='Timeout in seconds for requests before to abandon download',
        default=5
    )
    parser.add_argument(
        '-n',
        '--num-worker',
        type=int,
        help='Number of worker for parallel '
             'download, use number of cpus by default',
        default=CPUs
    )

    args = parser.parse_args()

    nid = args.nid
    classname = args.name
    NUM_WORKERS = args.num_worker
    TIMEOUT = args.timeout
    DEST = args.dest

    threads = []
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=task_download)
        t.start()
        threads.append(t)

    for u in get_list(nid).iter_lines():
        q.put((u, classname))

    q.join()

    for i in range(NUM_WORKERS):
        q.put((None, None))

    for t in threads:
        t.join()
