#!/bin/sh

# cleanup
rm -r code
rm code.zip
# create tmp
mkdir code
# copy dir & files
for dir in "bot" "database" "user_interaction"
do
  echo Dir $dir copy to out package
  cp -r $dir code
done
for file in "logs.py" "index.py" "requirements.txt"
do
  echo File $file copy to out package
  cp $file code
done
# make zip
zip -r "code.zip" "code"
# cleanup
rm -r code
