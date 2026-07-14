# Performance Roadmap

Sova 0.1v is a tree-walking interpreter. It is not C++-speed and makes no native-performance claim.

## Stage 1 - Current

Lex, parse, analyze, and walk the AST. Count operations, calls, output, collections, and elapsed runtime.

## Stage 2 - Bytecode

Compile the stable AST to a documented Sova bytecode format.

## Stage 3 - Virtual Machine

Implement a stack VM with explicit frames, local slots, module caches, and portable bytecode files.

## Stage 4 - Optimization

Add constant folding, dead-code elimination, peephole optimization, local-slot allocation, and inline property caches only after behavior is covered by compatibility tests.

## Stage 5 - Optional Native Targets

Evaluate LLVM IR, C, and WebAssembly as optional ahead-of-time targets. Native compilation is not part of 0.1v.
