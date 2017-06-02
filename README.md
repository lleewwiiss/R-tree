# R-tree - Python
Based loosely off:
    Enhanced nearest neighbour search on the R-tree (Cheung, Fu 1998)
    &
    R-Trees: A Dynamic Index Structure for Spatial Searching (Antonn Guttmann, 1984)

## Input Examples:

### Data set:
n
id 1 x 1 y 1
id 2 x 2 y 2
...
id n x n y n

### Range Query set:
x 1 x’ 1 y 1 y’ 1
x 2 x’ 2 y 2 y’ 2
...
x n x’ n y n y’ n


### Nearest Neigbour set:

x 1 y 1
x 2 y 2
...
x n y n