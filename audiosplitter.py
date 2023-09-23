import os
import json
import argparse
import numpy as np
from tqdm import tqdm
from pathlib import Path
from scipy.io import wavfile
from datetime import datetime, timedelta


def get_time(video_seconds: float) -> str:
    """Convert seconds to a time string format."""
    if video_seconds < 0:
        return "00"
    sec = timedelta(seconds=video_seconds)
    d = datetime(1, 1, 1) + sec
    return f"{d.hour:02d}:{d.minute:02d}:{d.second:02d}.001"


def get_total_time(video_seconds: float) -> str:
    """Get the total time as a string from seconds."""
    sec = timedelta(seconds=video_seconds)
    d = datetime(1, 1, 1) + sec
    return f"{d.hour}:{d.minute}:{d.second}"


def windows(signal: np.array, window_size: int, step_size: int):
    """Generate windows of audio samples."""
    for i_start in range(0, len(signal), step_size):
        i_end = i_start + window_size
        if i_end >= len(signal):
            break
        yield signal[i_start:i_end]


def energy(samples: np.array) -> float:
    """Calculate the energy of a sample window."""
    return np.sum(np.power(samples, 2.0)) / float(len(samples))


def rising_edges(binary_signal: np.array):
    """Generate rising edges in a binary signal."""
    previous_value = 0
    for index, x in enumerate(binary_signal):
        if x and not previous_value:
            yield index
        previous_value = x


def run_audioseg(input_file: Path, output_dir: Path) -> None:
    """
    Last Acceptable Values

    min_silence_length = 0.3
    silence_threshold = 1e-3
    step_duration = 0.03/10

    """
    if not input_file:
        raise ValueError("No file selected.")

    min_silence_length = 0.6
    silence_threshold = 1e-4
    step_duration = 0.03 / 10

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    input_filename = input_file
    window_duration = min_silence_length
    if step_duration is None:
        step_duration = window_duration / 10.0
    else:
        step_duration = step_duration

    output_filename_prefix = os.path.splitext(os.path.basename(input_filename))[0]
    dry_run = False

    print(
        "Splitting {} where energy is below {}% for longer than {}s.".format(
            input_filename, silence_threshold * 100.0, window_duration
        )
    )

    # Read and split the file

    sample_rate, samples = input_data = wavfile.read(filename=input_filename, mmap=True)

    max_amplitude = np.iinfo(samples.dtype).max
    print(max_amplitude)

    max_energy = energy([max_amplitude])
    print(max_energy)

    window_size = int(window_duration * sample_rate)
    step_size = int(step_duration * sample_rate)

    signal_windows = windows(
        signal=samples, window_size=window_size, step_size=step_size
    )

    window_energy = (
        energy(w) / max_energy
        for w in tqdm(signal_windows, total=int(len(samples) / float(step_size)))
    )

    window_silence = (e > silence_threshold for e in window_energy)

    cut_times = (r * step_duration for r in rising_edges(window_silence))

    # This is the step that takes long, since we force the generators to run.
    print("Finding silences...")
    cut_samples = [int(t * sample_rate) for t in cut_times]
    cut_samples.append(-1)

    cut_ranges = [
        (i, cut_samples[i], cut_samples[i + 1]) for i in range(len(cut_samples) - 1)
    ]

    video_sub = {
        str(i): [
            str(get_time(((cut_samples[i]) / sample_rate))),
            str(get_time(((cut_samples[i + 1]) / sample_rate))),
        ]
        for i in range(len(cut_samples) - 1)
    }

    for i, start, stop in tqdm(cut_ranges):
        output_file_path = "{}_{:03d}.wav".format(
            os.path.join(output_dir, output_filename_prefix), i
        )
        if not dry_run:
            print("Writing file {}".format(output_file_path))
            wavfile.write(
                filename=output_file_path, rate=sample_rate, data=samples[start:stop]
            )
        else:
            print("Not writing file {}".format(output_file_path))

    with open(output_dir / f"{output_filename_prefix}.json", "w") as output:
        json.dump(video_sub, output)


def run_audiosplitter(input_directory: Path):
    """Run the audio splitting logic."""
    if not input_directory.exists():
        print("No such directory.")
        return

    for audio_file in input_directory.glob("*.wav"):
        split_audio_file(audio_file)


def split_audio_file(file_path: Path, segment_duration: int = 10) -> None:
    """Split an audio file into segments of a given duration.

    Parameters:
        file_path: Path to the audio file to split.
        segment_duration: Duration of each segment in seconds.
    """
    # Load the audio file
    sample_rate, audio_data = wavfile.read(str(file_path))

    # Calculate the number of segments
    num_segments = len(audio_data) // (sample_rate * segment_duration)
    remainder = len(audio_data) % (sample_rate * segment_duration)
    if remainder > 0:
        num_segments += 1

    # Create the output directory for segments
    output_dir = file_path.parent
    base_filename = file_path.stem

    # Split the audio file into segments
    for i in range(num_segments):
        start = i * sample_rate * segment_duration
        end = min((i + 1) * sample_rate * segment_duration, len(audio_data))
        segment = audio_data[start:end]

        # Create the output file name
        segment_filename = f"{base_filename}_{i + 1}.wav"
        segment_path = output_dir / segment_filename

        # Save the segment as a new WAV file
        wavfile.write(str(segment_path), sample_rate, segment)

        print(f"Segment {i + 1}/{num_segments} saved: {segment_filename}")

    file_path.unlink()


def main():
    parser = argparse.ArgumentParser(description="Audio Processing Script")
    parser.add_argument("--mode", choices=["audioseg", "audiosplitter"], required=True)
    parser.add_argument("--input_file", type=Path, help="Audio file to split.")
    parser.add_argument("--output_dir", type=Path, help="Output directory.")
    parser.add_argument("--input_directory", type=Path, help="Input directory.")

    args = parser.parse_args()

    match args.mode:
        case "audioseg":
            if not args.input_file or not args.output_dir:
                print(
                    "Both --input_file and --output_dir must be specified for audioseg."
                )
            else:
                run_audioseg(args.input_file, args.output_dir)
        case "audiosplitter":
            if not args.input_directory:
                print("--input_directory must be specified for audiosplitter.")
            else:
                run_audiosplitter(args.input_directory)


if __name__ == "__main__":
    main()
