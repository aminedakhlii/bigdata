tail -n +2 $1 | split -l $2 --additional-suffix=.csv - chunks/split_
for file in chunks/split_*
do
    head -n 1 $1 > tmp_file
    cat "$file" >> tmp_file
    mv -f tmp_file "$file"
done