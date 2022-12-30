\*\*Main programming task:

- Create a moving catcher/hoop, such that when throwing a ball, the hoop moves to catch the ball
- Programming Subtasks:

  1. Map 2-D points of the center of the ball from a fixed camera to 3-D points / Triangulate the position of the ball to a 3-D coordinate system
     - Input: webcam frames of the ball
     - Output: A list of points in the format: [(x1, y1, z1), (x2, y2, z2), ..., (xn, yn, zn)]
  2. Using the list of 3-D points, try to predict where the ball will hit on the wall

  - Input: A list of points from Subtask (a)
  - Output: A coordinate pair (x, y) on the wall

  1. Make the hoop move to the coordinate pair (x, y) on the wall

  - Input: A coordinate pair (x, y) on the wall
  - Output: Motor controls to move to (x, y)

- How to approach each Subtask

1. Subtask A

- Implement this paper: [https://sci-hub.se/10.1109/TPAMI.2008.247](https://sci-hub.se/10.1109/TPAMI.2008.247) (idk what any of this means)
- Triangulate the position using OpenCV

1. Subtask B

- Machine learning (needs data)
- Curve fit the points given from Subtask A and find where on that curve is the wall

1. Subtask C

- ???

\*\*
