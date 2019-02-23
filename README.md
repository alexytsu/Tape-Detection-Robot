# Line Detection

A python module written for DRC2019 competition. Uses opencv to plot a path between a blue line on the left and a yellow line on the right. 

## Setting up a development environment

- Ensure you are using `python3`
- Create a virtualenvironment to store the dependencies `virtualenv venv`
- Activate the virtual environment `source venv/bin/activate` on Linux or `.\venv\Scripts\activate` on Windows
- Now install the dependencies (opencv)
- `pip install python-opencv`
- To test, you should be able to open a python3 shell and import cv2

### Getting the footage

- Footage should not be committed to version control
- By default it is place in the _footage/_ directory
- To be able to run `python stream.py` you will need to place a file in _footage/_
- Then you will need to configure the script accordingly by changing the filename it script expects
	- This is configured near the top of the **stream.py** file as the global variable **VIDEO_FILE**
