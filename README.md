# audiosplitter
A simple audio splitter for audio files, specifically designed for usage with so-vits-svc to split audio files into 10 seconds or less. This is to prevent VRAM out of memory issues.

For this to work, **you MUST have the audio files in .wav format**

## How to use it
When you run the exe or script, a file explorer window will pop up.  In this window, you want to select the audio files folder where your files are located.  It will then run through all of them, split them, and then output them in that same folder with incremental suffixes on them based on how long the audio file was.

**NOTE: IT WILL DELETE YOUR ORIGNAL AUDIO FILES SO MAKE SURE YOU HAVE COPIES OF THEM**

#### EXE
There is an exe version of it in the releases area, just go to the following link and download the exe file: https://github.com/JarodMica/audiosplitter/releases

If you're using the exe, your anti-virus may block it due to being an unknown exe file, you just have to allow it or use the python script version of it.

#### Python
Clone the repo with:

```git clone https://github.com/JarodMica/audiosplitter.git```

Once you have done that, navigate into the folder and install requirements.  I recommend you use a venv if you're familiar with them to prevent any package issues later on:
```
cd audiosplitter
pip install -r requirements.txt
```

Now that you have all the requirements, you should be able to just run the script either by using an IDE or by CMD with the following command (as long as you're in the audiosplitter folder path):
```python audiosplitter.py```
