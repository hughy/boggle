# Boggle
[Boggle](https://en.wikipedia.org/wiki/Boggle) is a popular word game originally produced by Parker Brothers.
## Rules
Although later versions include larger grids the original version of the Boggle game uses a 4x4 grid of letters cubes. Each cube has one letter, except for `Qu`, which includes `U` because `U` follows `Q` in almost all English words in which `Q` appears.

Players search for words in the letter grid by constructing words from adjacent letter cubes. Adjacency in Boggle includes horizontal, vertical, and diagonal neighbors of each cube. A valid word in Boggle can only use a given letter cube one time.

## How to play
I've used `pipenv` to manage dependencies and virtual environments in this project. If you have `pipenv` installed you can simply run

    pipenv run python -m boggle

to play a game with a randomly generated letter grid. If you don't have `pipenv` installed you can run the commands below to set up a virtual environmentA, install dependencies, and run the `boggle` program:

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python -m boggle

## Implementation
### Depth-first search
The grid layout of the letter cubes and the rules of Boggle suggest a graph structure: each letter is a node in the graph with edges to its adjacent letters. After mentally modeling the letter grid as a graph, graph search algorithms like depth-first and breadth-first search can easily find all valid words in the grid. In this project I've implemented the depth-first search solution.

### Trie
A key part of the depth-first search implementation is terminating search paths when they will not produce any additional words. I use a [trie](https://en.wikipedia.org/wiki/Trie) data structure to represent the dictionary of valid words and terminate searches when the current search path does not exist as a prefix in the trie.

## Further work
For this implementation I've leveraged the [pygtrie](https://github.com/google/pygtrie) library for its trie data structure. This implementation works well, but implementing the trie myself would remove a dependency.

I may revisit this project later on to add more features to the command-line game: custom grid input, multi-player, Boggle scoring, etc.
