## Trainer

**Input**: Points that have been classified (by hand as yellow, blue, red, purple or ground).

**Output**: A classifier model that can be used to sort a given pixel into one of the categories. 

## Picker 

**Interface**: Gives user 5 screenshots equally space from the video. For each screenshot, asks the user to click 10 points for each colour.

**Output**: A .csv file of the data points in HSV.

## Verification

**Interface**: Runs a video and masks the tape lines.