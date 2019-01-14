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
DATAFILE = './data.csv'


q = queue.Queue(CPUs)
locker = threading.Lock()


def get_list(imid):
    imlist = requests.get(LIST_URL.format(imid=imid))
    return imlist


def logthat(content, total=-1, index=-1):
    if total is not None and index is not None:
        print('%d/%d %s' % (index+1, total, content))
    else:
        print('%s' % content)


def save_data(url, md5, classname):
    locker.acquire()
    try:
        with open(DATAFILE, 'a+') as f:
            f.write('%s,%s,%s\n' % (url.decode(), md5, classname))
    except Exception as e:
        print(e)
    finally:
        locker.release()


def is_in_db(url):
    locker.acquire()
    try:
        with open(DATAFILE, 'r') as f:
            lines = f.readlines()
    except Exception:
        return False
    finally:
        locker.release()

    for l in lines:
        elements = l.split(',')
        if elements[0] == url.decode():
            return True
    return False


def dl_image(imurl, classname='unknown', dest='./', total=None, index=None):
    imname = os.path.basename(imurl)
    imname = imname.decode()

    # prepare the desitnation directory
    os.makedirs(os.path.join(dest, classname), exist_ok=True)

    # deactivate, use md5
    # if os.path.exists(fileto):
    #    print('File %s already downloaded, skippiing' % fileto)
    #    return

    # check if image is in csv database
    if is_in_db(imurl):
        logthat('Image already downloaded, skipping', total, index)
        return

    # download image, and check status_code
    try:
        im = requests.get(imurl, timeout=TIMEOUT)
        if im.status_code != 200:
            logthat(
                'Status code is not OK for %s, %d' % (imurl, im.status_code),
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

    # checking md5 of known bad files
    hhs = hashlib.md5(im.content).hexdigest()
    fileto = os.path.join(dest, classname, hhs + '.' + ext)
    if hhs in BADIMG:
        logthat('image %s seems to be a "bad file"' % fileto, total, index)
        return

    # md5 is ok, downloaded file is not empty, we can save it
    with open(fileto, 'wb') as f:
        f.write(im.content)
        logthat("%s file saved" % imname, total, index)
        save_data(imurl, hhs, classname)


def task_download():
    while True:
        item, classname, total, index = q.get()
        if item is None:
            break
        dl_image(item, classname, DEST, total, index)
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

    nid = args.nid
    classname = args.name
    NUM_WORKERS = args.num_worker
    TIMEOUT = args.timeout
    DEST = args.dest
    DATAFILE = args.csv

    threads = []
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=task_download)
        t.start()
        threads.append(t)

    res = get_list(nid)
    # list is not very well formatted, we need
    # to iterate to count, and not find "\n" or whatever
    # the line delimiter
    for idx, _ in enumerate(res.iter_lines()):
        lines_count = idx

    # it starts from 0, so add one
    lines_count += 1

    for idx, u in enumerate(res.iter_lines()):
        q.put((u, classname, lines_count, idx))

    q.join()

    for i in range(NUM_WORKERS):
        q.put((None, None, None, None))

    for t in threads:
        t.join()
