echo $1 | perl -pe 's/.*\///g'
./apriori -m2 -n3 -s-30 <(cat $1 | perl -pe 's/ 0 *$//g' | tail -n +2) 2> >(grep writing | perl -pe 's/^.*?\[(.*?)\].*$/$1/g')
