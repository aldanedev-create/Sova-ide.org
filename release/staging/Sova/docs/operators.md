# Operators

Precedence from highest to lowest:

1. calls, properties, safe properties, indexing, slicing
2. exponentiation `**`
3. unary `-`, `+`, `!`, `not`
4. `*`, `/`, `%`
5. `+`, `-`
6. ranges `..`
7. `<`, `<=`, `>`, `>=`, `in`
8. `==`, `!=`, `is`
9. `and`, `&&`
10. `or`, `||`
11. null coalescing `??`
12. conditional `value if condition else fallback`
13. assignment `=`, `+=`, `-=`, `*=`, `/=`

Exponentiation is right-associative. Member access and calls bind before arithmetic. Division and modulo by zero produce `ValueError` diagnostics.
