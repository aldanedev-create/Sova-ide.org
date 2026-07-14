# Collections

Lists are mutable, tuples are fixed, and objects map string keys to values. Indexes start at zero and negative indexes count from the end.

```sova
let values = [10, 20, 30, 40]
print(values[0])
print(values[-1])
print(values[1..3])

let [first, _, third] = values
let { name: localName, age } = profile
```

List operations include `add`, `append`, `insert`, `remove`, `pop`, `clear`, `contains`, `length`, `isEmpty`, `first`, `last`, `sort`, `reverse`, `map`, `filter`, `reduce`, `find`, `any`, `all`, `unique`, and `join`.

Objects expose `keys`, `values`, `entries`, `contains`, `get`, `set`, `remove`, `merge`, `length`, and `isEmpty`. Strings expose `length`, `upper`, `lower`, `trim`, `split`, `replace`, `contains`, `startsWith`, `endsWith`, and `slice`.
