# Import the necessary packages
import graphics as g

# Create a new window
win = g.GraphWin("Test Scores", 400, 400)

# Define the list of test scores
test_scores = [85, 95, 70, 75, 100]

# Create a rectangle for each test score
for i, score in enumerate(test_scores):
    # Create a new rectangle
    rect = g.Rectangle(g.Point(0, i * 50), g.Point(score, (i + 1) * 50))
    rect.draw(win)

    # Add the score to the end of the rectangle
    text = g.Text(g.Point(score, (i + 0.5) * 50), str(score))
    text.draw(win)

# Wait for the user to close the window
win.getMouse()
win.close()
