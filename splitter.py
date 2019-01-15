#! /bin/env python3
""" Helper script to split images in train/valid directories
with a given fraction (default to .2 => 20%)

Author: Patrice FERLET <metal3d@gmail.com>
Licence: MIT
"""
import glob
import random
import os
import math
import shutil

DEST = '.'
CSV_ONLY = False


def write_base(files, classname: str, usage: str):
    """ Write CSV file for train or valid"""

    csvfile = os.path.join(DEST, '%s.csv' % usage)

    if type(files) is not list:
        files = [files]

    try:
        if not os.path.exists(csvfile):
            with open(csvfile, 'w') as f:
                f.write('Filename,Classname\n')

        content = open(csvfile).read()

        with open(csvfile, 'a+') as csv:
            for f in files:
                line = '%s,%s' % (f, classname)
                # do not rewrite already found files/classname
                if line not in content:
                    csv.write(line + '\n')

    except Exception as e:
        print(e)

    print(csvfile, "written")


def splitdir(dirname, classname, frac=.2, dest='.'):
    """ Randomly split files fraction from dirname
        and copy them to destination. Also, call
        the write_base function to write corresponding
        CSV files.
    """

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

    if not CSV_ONLY:
        for v in valid:
            ffrom = v
            fto = os.path.join(valid_dir, os.path.basename(v))
            print('[Validation] Copying', ffrom, fto)
            shutil.copyfile(ffrom, fto)
            write_base(fto, classname, 'valid')

        for v in files:
            ffrom = v
            fto = os.path.join(train_dir, os.path.basename(v))
            print('[Train] Copying', ffrom, fto)
            shutil.copyfile(ffrom, fto)
            write_base(fto, classname, 'train')

    else:
        # write real path in CSV
        write_base(valid, classname, 'valid')
        write_base(files, classname, 'train')

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
        '-a',
        '--all',
        help='Get all images from SRC and splits the whole classes found. '
             'This option deactivates the -c/--classname option.',
        action='store_true'
    )
    parser.add_argument(
        '-C',
        '--csv-only',
        help='Only create the CSV files, do not copy images '
             'in destination directory.',
        action='store_true'
    )
    parser.add_argument(
        '-d',
        '--dest',
        help='Destination where to copy files, and where '
             'CSV files are written. Do not set classname in '
             'this option value ! eg. "-d data" will create '
             '"data/<classnames>" and "data/{valid,train}.csv"',
        default=DEST
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
    CSV_ONLY = args.csv_only

    if classname in (None, ''):
        classname = os.path.basename(ffrom)

    if args.all:
        try:
            os.unlink(os.path.join(DEST, 'valid.csv'))
        except Exception:
            pass

        try:
            os.unlink(os.path.join(DEST, 'train.csv'))
        except Exception:
            pass

        dirs = glob.glob(os.path.join(ffrom, '*'))
        for d in dirs:
            classname = d.split(os.path.sep)[-1]
            print('Split %s class' % classname)
            splitdir(d, classname, frac, DEST)
    else:
        splitdir(ffrom, classname, frac, DEST)
