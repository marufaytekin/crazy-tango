import pyaudio
import aubio
import time
import threading
import numpy as np

def play(file_name, handle_beat, sample_rate=0):
    win_s = 1024  # fft size
    hop_s = win_s // 2  # hop size
    a_source = aubio.source(file_name, sample_rate, hop_s)  # create aubio source

    sample_rate = a_source.samplerate

    # create aubio tempo detection
    a_tempo = aubio.tempo("default", win_s, hop_s, sample_rate)
    global last_beat_time
    last_beat_time = time.time()


    # pyaudio callback
    def callback(_in_data, _frame_count, _time_info, _status):
        samples, read = a_source()
        is_beat = a_tempo(samples)
        global last_beat_time
        now = time.time()
        if is_beat:
            beat_length = now - last_beat_time
            last_beat_time = now
            print("tick")
            t = threading.Thread(target=handle_beat, args=[beat_length])
            t.start()
        audiobuf = samples.tobytes()
        if read < hop_s:
            beat_length = now - last_beat_time
            handle_beat(beat_length)
            #t = threading.Thread(target=handle_beat, args=[beat_length])
            #t.start()
            return audiobuf, pyaudio.paComplete
        return audiobuf, pyaudio.paContinue

    # create pyaudio stream with frames_per_buffer=hop_s and format=paFloat32
    p = pyaudio.PyAudio()
    pyaudio_format = pyaudio.paFloat32
    frames_per_buffer = hop_s
    n_channels = 1
    stream = p.open(format=pyaudio_format, channels=n_channels, rate=sample_rate,
                    output=True, frames_per_buffer=frames_per_buffer,
                    stream_callback=callback)

    # start pyaudio stream
    stream.start_stream()

    # wait for stream to finish
    while stream.is_active():
        time.sleep(0.1)

    # stop pyaudio stream
    stream.stop_stream()
    stream.close()

    # close pyaudio
    p.terminate()
