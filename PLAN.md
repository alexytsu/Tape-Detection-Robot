# Software Modules we need to Write

## Trainer

**Input**: Points that have been classified (by hand as yellow, blue, red, purple or ground).

**Output**: A classifier model that can be used to sort a given pixel into one of the categories.

## Planner

**Interface**: Gives user 5 screenshots equally space from the video. For each screenshot, asks the user to click 10 points for each colour.

**Output**: A .csv file of the data points in HSV.

## Tester

**Interface**: Runs a video and masks the tape lines.

## Masker

**Input**: A training model, and the live image
**Output**: The location of the tapes and the obstacles.

## Navigator

**Input**: The location of the tape boundaries in the image
**Output**: A direction to steer