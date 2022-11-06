# ScratchJr Python Wrapper

The ScratchJr Python Wrapper is a wrapper for the underlying JSON structure of a ScratchJr project. It was mostly made to be used as a tool for its creator; however, it definitely has the ability to be used to procedurally create ScratchJr projects with many different purposes. 

## Classes

The classes are split up into the few levels of heirarchy that ScratchJr has.

### Project
The project class is an incredibly simple class that holds pages.
### Page
The page class is an incredibly simple class that has a name and holds sprites.
### Sprite
The sprite is a more complex class with a name, position, size, texture, and a variable number of other customizable options. It also can contain ScriptElement lists.
### ScriptElement
The ScriptElement class holds all of the information about a single scripting block in ScratchJr. When put in lists, they can be fed to a sprite.

## Compilers

There is currently a compiler for "Extended Infinite Abacus" code (patent pending), which allows for Turing-Complete programming in ScratchJr. The language is an extension of the [Infinite Abacus](https://www.cambridge.org/core/journals/canadian-mathematical-bulletin/article/how-to-program-an-infinite-abacus/A6EB7DD8D57056044CCB128923764BEB) programming language. It includes resetting cells, incrementing by more than one, printing arbitrary strings, inline jumps, and asynchronous input. These features were all added as they are very simple and add no complexity to the compiled ScratchJr project. EIA can be easily compiled to IA, although this is unneccesary for the project.