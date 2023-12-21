cd src
for file in *.*py
do
    echo "Uploading $file"
    mpremote connect id:001 fs cp $file :$file
done
