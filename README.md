# Line Detection

A python module written for DRC2019 competition. Uses opencv to plot a path between a blue line on the left and a yellow line on the right. 

## Setting up a development environment

- Ensure you are using `python3`
- Create a virtualenvironment to store the dependencies `virtualenv venv`
- Activate the virtual environment `source venv/bin/activate` on Linux or `.\venv\Scripts\activate` on Windows
- Install the dependencies `pip install -r requirements.txt`

### Running the colour collector

With the development environment set up and some footage in the  "footage/" folder, (this should be in the top level i.e. tape-detection/footage/testfile.mp4) run `python3 planner.py`.

Make sure you also have the folder "tape-detection/training_data" created. This is where the training data is outputted.

### Getting the footage

- Footage should not be committed to version control
- By default it is place in the _footage/_ directory
- To be able to run `python stream.py` you will need to place a file in _footage/_
- Then you will need to configure the script accordingly by changing the filename it script expects
	- This is configured near the top of the **stream.py** file as the global variable **VIDEO_FILE**
