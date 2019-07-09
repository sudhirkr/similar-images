# similar-images
Find similar images based on various hashing mechanism

Command line to run the script
#python find_similar_images.py [ahash|phash|dhash|...] [directory]

#python find_similar_images.py avhash <dir>
   - If directory is not provided then it works on all the images in current directory
   - After finding similar images, it stores results in ./result directory. Structure of result directory will be..
  
$ ls result

dup1   dup11  dup13  dup15  dup17  dup19  dup20  dup22  dup24  dup26  dup4  dup6  dup8

dup10  dup12  dup14  dup16  dup18  dup2   dup21  dup23  dup25  dup3   dup5  dup7  dup9

Each dup (duplicate) directory has similar images.
