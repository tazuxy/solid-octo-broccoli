#!/usr/bin/env bash
# Usage: bash research/fetch_data.sh <WORK_DIR>   (direct HTTPS download from the public Drive folders; ~2-5 min)
# fetch histdata zips from public Drive folders (resumable)
set -u
W=${1:?work dir}; REPO=$(cd "$(dirname "$0")/.." && pwd); mkdir -p $W/test; cp $REPO/research/data_folders.txt $W/folders.txt
cd $W
LIST=$W/filelist.tsv
if [ ! -s $LIST ]; then
  : > $LIST
  while read SYM FID; do
    curl -sS -L "https://drive.google.com/embeddedfolderview?id=$FID" -o $W/test/$SYM.html
    python3 -I - "$SYM" "$W/test/$SYM.html" >> $LIST <<'P'
import re,sys
sym,f=sys.argv[1],sys.argv[2]; h=open(f).read()
for m in re.finditer(r'id="entry-([A-Za-z0-9_-]+)".*?flip-entry-title">(DAT_ASCII_[A-Z]+_M1_(\d{4})\.zip)<',h):
    fid,name,y=m.group(1),m.group(2),int(m.group(3))
    if 2005<=y<=2024:
        idx=sym in ('SPXUSD','GRXEUR','UKXGBP','JPXJPY','AUXAUD')
        d='data_idx' if idx else ('data' if y>=2012 else 'data_early')
        if idx and y<2010: continue
        print(sym,y,fid,d,name,sep='\t')
P
  done < $W/folders.txt
fi
dl(){ sym=$1; y=$2; fid=$3; d=$4; name=$5
  mkdir -p $W/$d; out=$W/$d/$name
  if [ -s $out ] && unzip -tq $out >/dev/null 2>&1; then echo "SKIP $name"; return; fi
  for i in 1 2 3 4; do
    r=$(curl -sS -L -D $W/test/$name.hdr -o $out.part -w "%{http_code} %{size_download}" "https://drive.usercontent.google.com/download?id=$fid&export=download&confirm=t")
    cl=$(grep -i '^content-length' $W/test/$name.hdr | tail -1 | tr -dc 0-9)
    sz=$(stat -c %s $out.part 2>/dev/null || echo 0)
    if [[ $r == 200* ]] && [ "$cl" = "$sz" ] && unzip -tq $out.part >/dev/null 2>&1; then mv $out.part $out; echo -e "OK\t$name\t$sz"; return; fi
    sleep $((2**i))
  done
  echo "FAIL $name $r"
}
export -f dl; export W
tr '\t' ' ' < $LIST | xargs -P 6 -L 1 bash -c 'dl "$@"' _
