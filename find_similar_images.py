#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
from PIL import Image
import six
import sys
import shutil
import imagehash
import json
import errno
from pprint import pprint

dst = "./result/"
THRESHOLD = 93

def avhash(im):
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    im = im.resize((8, 8), Image.ANTIALIAS).convert('L')
    avg = reduce(lambda x, y: x + y, im.getdata()) / 64.
    return reduce(lambda x, (y, z): x | (z << y),
                  enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())),
                  0)

"""
Hamming distance between two hashes
"""    
def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h

"""
Similarity %
"""    
def similarity_img(hash, images):
    max_sim = 0
    besthash = None    
    for key, img_list in six.iteritems(images):
        dist = hamming(hash, key)
        similarity = ((64 - dist) * 100 / 64)
        #print ("similarity", similarity, hash)
        if similarity >= THRESHOLD:
            if similarity > max_sim:
                max_sim = similarity
                besthash = key

    return (besthash, max_sim)

# copy images to result folder
def result_to_folder(images):
    try:
        os.makedirs(dst)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print ("Result directory already exits. It will be removed and created again")
            shutil.rmtree(dst)
            os.makedirs(dst)


    index = 1
    for key, img_list in six.iteritems(images):
        if len(img_list) > 1:
            dup = "dup" + str(index)
            dup_path = os.path.join(dst, dup)
            print (dup_path)
            os.makedirs(dup_path)
            index = index + 1
            for imgpath in img_list:
                print ("copying %s to %s" %(imgpath, dup_path))
                shutil.copy2(imgpath, dup_path)

def find_similar_images(userpath, hashfunc = imagehash.average_hash):
    import os
    print (userpath)
    def is_image(filename):
        f = filename.lower()
        return f.endswith(".png") or f.endswith(".jpg") or \
            f.endswith(".jpeg") or f.endswith(".bmp") or f.endswith(".gif")
    
    image_filenames = [os.path.join(userpath, path) for path in os.listdir(userpath) if is_image(path)]

    images = {}
    dup = {}
    for img in sorted(image_filenames):
        hash = hashfunc(Image.open(img))

        besthash, max_sim = similarity_img(hash, images)
        print (max_sim, besthash, img)
        if besthash is None:
            images[hash] = images.get(hash, []) + [img]
        else:
            images[besthash] = images.get(besthash, []) + [img]

    # copy cluster to result folder 
    result_to_folder(images) 
    #print (images)
    print ("--------------")

def load_json():
    images = {}
    json_data = json.load(open('hash.json'))
    for json_elem in json_data:
        #print (json_elem['avHash'])
        #print (json_elem['image'])
        hash = json_elem['avHash']
        img = json_elem['image']

        besthash, max_sim = similarity_img(hash, images)
        if besthash is None:
            images[hash] = images.get(hash, []) + [img]
        else:
            images[besthash] = images.get(besthash, []) + [img]

    # copy result to folder        
    #print (images)
    print(len(images.keys()))
    result_to_folder(images) 
    print ("--------------")

def load_lists():
    images = {}
    lines = []
    import ast
    
    try:
        with open('hash2.json') as hashf:
            for line in hashf:
                line = line.strip()
                hlist = ast.literal_eval(line)

                # hash and image name
                img = hlist[0]
                hash = hlist[1]

                besthash, max_sim = similarity_img(hash, images)
                if besthash is None:
                    images[hash] = images.get(hash, []) + [img]
                else:
                    images[besthash] = images.get(besthash, []) + [img]
    except Exception as e:
        print ("\nhash file should be named as hash2.json and it should be in same directory")
        exit()

    #print (images)
    # copy result to folder        
    #print(len(images.keys()))
    #result_to_folder(images) 
    #print ("--------------")

def usage():
    print("python find_similar_images.py [ahash|phash|dhash|...] [directory]")
    exit()

if __name__ == '__main__':
    import sys, os
    #load_lists()
    #Identifies similar images in the directory.

    """
    Method: 
    ahash:      Average hash
    phash:      Perceptual hash
    dhash:      Difference hash
    whash-haar: Haar wavelet hash
    whash-db4:  Daubechies wavelet hash

    (C) Johannes Buchner, 2013-2017
    """
    hashmethod = sys.argv[1] if len(sys.argv) > 1 else usage()
    if hashmethod == 'ahash':
        hashfunc = imagehash.average_hash
    elif hashmethod == 'avhash':
        hashfunc = avhash
    elif hashmethod == 'phash':
        hashfunc = imagehash.phash
    elif hashmethod == 'dhash':
        hashfunc = imagehash.dhash
    elif hashmethod == 'whash-haar':
        hashfunc = imagehash.whash
    elif hashmethod == 'whash-db4':
        hashfunc = lambda img: imagehash.whash(img, mode='db4')
    else:
        usage()
    userpath = sys.argv[2] if len(sys.argv) > 2 else "."
    find_similar_images(userpath=userpath, hashfunc=hashfunc)