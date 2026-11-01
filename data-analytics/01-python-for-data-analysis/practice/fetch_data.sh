#!/usr/bin/env bash
# Download the data for the notebooks from wesm/pydata-book (2nd edition, MIT).
#   mckinney/examples/  mckinney/datasets/   (used by mckinney/chNN.ipynb, ~240 MB)
#   data/*.csv                               (used by 5_Plotting … 7_Time_Series)
# Nothing here is committed: see .gitignore in this folder. Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")"

repo=https://github.com/wesm/pydata-book.git
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

echo "Cloning pydata-book (sparse: examples/ and datasets/)…"
git clone --quiet --depth 1 --branch 2nd-edition --filter=blob:none --sparse "$repo" "$tmp/pydata-book"
git -C "$tmp/pydata-book" sparse-checkout set examples datasets

rm -rf mckinney/examples mckinney/datasets
cp -R "$tmp/pydata-book/examples" "$tmp/pydata-book/datasets" mckinney/

mkdir -p data
for f in macrodata.csv spx.csv stock_px_2.csv tips.csv; do
  cp "mckinney/examples/$f" data/
done

echo "Done: mckinney/examples, mckinney/datasets and data/{macrodata,spx,stock_px_2,tips}.csv"
echo "Start Jupyter from this folder, or from mckinney/ for the chNN notebooks."
