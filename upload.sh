cd src
for file in *.*py
do
    echo "Uploading $file"
    mpremote connect id:0001 fs cp $file :$file
done
