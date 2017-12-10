# Cross sums

Project can solve cross sums puzzle (also known as "Kakuro").

### How to use it?

```
py cross_sums [-h] [-f FILE] [-l n]

Cross sums (also known as "Kakuro") puzzle solver.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  file with cross sums puzzle
  -l n, --limit n       limit of possible solutions (integer or asterisk)

```

Solve puzzle written in file.

```
py cross_sums -f "file.txt"
```

Solve puzzle from STDIN.

```
py cross_sums < "file.txt"
```

Get first 5 solutions.

```
py cross_sums -l 5 -f "file.txt"
```

Get all solutions.

```
py cross_sums -l * -f "file.txt"
```

### Example of input

Let's select for example this puzzle.

![Example](https://upload.wikimedia.org/wikipedia/commons/c/c8/Kakuro_black_box.svg)

In the described language it can be written as:

```
:   23: 30:   :     :     27: 12: 16:
:16 _   _     :     17:24 _   _   _
:17 _   _     15:29 _     _   _   _
:35 _   _     _     _     _   12: :
:   :7  _     _     7:8   _   _   7:
:   11: 10:16 _     _     _   _   _
:21 _   _     _     _     :5  _   _
:6  _   _     _     :     :3  _   _
```

***Note that multiple spaces inserted only with an aesthetic purpose to make input seem less complicated. There is absolutely no difference between one and multiple spaces!***

### Output

Output will be dispatched in the same style.