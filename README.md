# audiosplitter

A simple audio splitter cli for audio files, specifically designed for usage with so-vits-svc to split audio files into 10 seconds or less. This is to prevent VRAM out of memory issues.

For this to work, **you MUST have the audio files in .wav format**

## How to use it

```
usage: audiosplitter.py [-h] --mode {audioseg,audiosplitter} [--input_file INPUT_FILE] [--output_dir OUTPUT_DIR] [--input_directory INPUT_DIRECTORY]

Audio Processing Script

options:
  -h, --help            show this help message and exit
  --mode {audioseg,audiosplitter}
  --input_file INPUT_FILE
  --output_dir OUTPUT_DIR
  --input_directory INPUT_DIRECTORY
```

Clone the repo with:

```
git clone https://github.com/derektata/audiosplitter.git
```

Once you have done that, navigate into the folder and install requirements.  I recommend you use a venv if you're familiar with them to prevent any package issues later on:
```
cd audiosplitter
pip install -r requirements.txt
```

Segment an audio file:
```bash
python audiosplitter.py --mode audioseg --input_file /path/to/audio.wav --output_dir /path/to/output/
```

Split all '.wav' files in a directory:
```bash
python audiosplitter.py --mode audiosplitter --input_directory /path/to/directory/
```