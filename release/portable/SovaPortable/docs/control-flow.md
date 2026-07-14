# Control Flow

```sova
if age >= 18 {
    print("Adult")
} elif age >= 13 {
    print("Teen")
} else {
    print("Child")
}

while count < 10 {
    count += 1
}

for number in 1..10 {
    if number == 5 { continue }
    if number == 9 { break }
    print(number)
}
```

Ranges are inclusive and may count upward or downward. A guard return exits only when its condition is true:

```sova
return 0 if items.isEmpty()
```
