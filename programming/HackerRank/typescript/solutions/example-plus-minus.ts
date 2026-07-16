// HackerRank: Plus Minus (warmup) — https://www.hackerrank.com/challenges/plus-minus
// Run: npm run solve solutions/example-plus-minus.ts

function plusMinus(arr: number[]): void {
  const n = arr.length;
  const pos = arr.filter((x) => x > 0).length;
  const neg = arr.filter((x) => x < 0).length;
  console.log((pos / n).toFixed(6));
  console.log((neg / n).toFixed(6));
  console.log(((n - pos - neg) / n).toFixed(6));
}

plusMinus([-4, 3, -9, 0, 4, 1]);
