#! /bin/env python3
import glob
import random
import os
import math
import shutil

DEST = '.'


def splitdir(dirname, classname, frac=.2, dest='.'):

    train_dir = os.path.join(dest, 'train', classname)
    valid_dir = os.path.join(dest, 'valid', classname)

    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(valid_dir, exist_ok=True)

    files = glob.glob('%s/*' % dirname)
    N = len(files)*frac
    N = math.ceil(N)

    valid = random.sample(files, k=N)

    for i in valid:
        del(files[files.index(i)])

    for v in valid:
        ffrom = v
        fto = os.path.join(valid_dir, os.path.basename(v))
        print('[Validation] Copying', ffrom, fto)
        shutil.copyfile(ffrom, fto)

    for v in files:
        ffrom = v
        fto = os.path.join(train_dir, os.path.basename(v))
        print('[Train] Copying', ffrom, fto)
        shutil.copyfile(ffrom, fto)

    print('Validation images:', len(valid))
    print('Train images:', len(files))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'src',
        help='Directory from where to get images'
    )
    parser.add_argument(
        '-d',
        '--dest',
        help='destination root (without train or valid names) directory '
             'where images will be copied. '
             "eg. "
             '"--dest data" will create a "data" directory '
             'and the script will create "data/train/<class>" '
             'and "data/valid/<class>"',
        default='.'
    )
    parser.add_argument(
        '-c', '--classname',
        help='Real classname, if empty, takes the basename of SRC',
        default=None
    )
    parser.add_argument(
        '-f', '--frac',
        type=float,
        default=.2,
        help='Fraction for validation'
    )

    args = parser.parse_args()
    frac = args.frac
    ffrom = args.src
    classname = args.classname
    DEST = args.dest

    if classname in (None, ''):
        classname = os.path.basename(ffrom)

    splitdir(ffrom, classname, frac, DEST)
