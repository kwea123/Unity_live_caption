from argparse import ArgumentParser
from google.cloud import speech
from google.cloud.speech import enums, types
import pyaudio
from six.moves import queue
import sys
import os
import socket
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/kwea123/Downloads/MyProject-e85ed8c91456.json'

# Audio recording parameters
RATE = 44100
CHUNK = int(RATE / 1000)  # 100ms

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

def listen_print_loop(responses, print_locally=True, sock=None):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if sock is not None:
            sock.send(bytes(transcript, "utf-8"))
        
        if print_locally: # print the result on the console.
            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()
                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)
                num_chars_printed = 0


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true", 
                        help="show speech recognition result on the console",
                        default=False)
    parser.add_argument("--connect", action="store_true", 
                        help="connect to unity",
                        default=False)
    parser.add_argument("--lang_code", type=str, 
                        help="the language code of your language",
                        default="zh-tw")
    args = parser.parse_args()

    if args.connect:
        address = ('127.0.0.1', 5067)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
    else:
        sock = None

    client = speech.SpeechClient()
    config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                                     sample_rate_hertz=RATE,
                                     language_code=args.language_code)
    streaming_config = types.StreamingRecognitionConfig(config=config, interim_results=True)

    print("%s recognition started!"%language_code)
    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)
            try:    
                responses = client.streaming_recognize(streaming_config, requests)
                listen_print_loop(responses, print_locally=args.debug, sock=sock)
            except KeyboardInterrupt:
                break
            except: # ignore "400 Exceeded maximum allowed stream duration of 305 seconds."
                continue

    if sock is not None:
        sock.close()