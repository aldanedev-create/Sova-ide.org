# Classes

Constructor shorthand creates fields automatically:

```sova
class Player(name, health) {
    function takeDamage(amount) {
        self.health -= amount
    }
}

let hero = Player("Aldane", 100)
```

An explicit `init` method is also supported. Instantiate classes without `new`. Single inheritance searches the derived class first, so defining the same method overrides the base implementation.

```sova
class Admin extends User {
    function canDelete() {
        return true
    }
}
```

Multiple inheritance, access modifiers, operator overloading, manual destructors, and C++ pointer semantics are outside 0.1v.
