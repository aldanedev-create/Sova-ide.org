# Functions

```sova
function greet(name = "Guest") {
    print("Hello {name}")
}

function add(x: Int, y: Int) -> Int {
    return x + y
}

function sum(...numbers) {
    return numbers.reduce((total, number) => total + number, 0)
}
```

Arguments may be positional or named. Functions are first-class values and capture lexical environments. Arrow functions are concise expression closures:

```sova
let adults = users.filter(user => user.age >= 18)
```

Anonymous block functions support stateful closures. Recursive calls are bounded by the active execution policy's call-depth limit.
