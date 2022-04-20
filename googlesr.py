from argparse import ArgumentParser
from google.cloud import speech, translate
from pyaudio import PyAudio, paInt16, paContinue
from six.moves.queue import Queue, Empty
from sys import stdout
import socket

from os import environ
environ['GOOGLE_APPLICATION_CREDENTIALS'] = \
    'C:/Users/kwea1/Downloads/youtubeapi-329002-9f71c84a7e37.json'

# Audio recording parameters
RATE = 44100
CHUNK = RATE//1000  # 100ms

class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=paInt16,
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
        return None, paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None: return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None: return
                    data.append(chunk)
                except Empty: break

            yield b''.join(data)

def listen_print_loop(sp_responses,
                      tr_client,
                      tgt_lang_code,
                      print_locally=True,
                      sock=None):
    num_chars_printed = 0
    for sp_response in sp_responses:
        if not sp_response.results: continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = sp_response.results[0]
        if not result.alternatives: continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript
        if tr_client is not None: # translate the text
            tr_response = tr_client.translate_text(
                contents=[transcript],
                target_language_code=tgt_lang_code,
                parent="projects/youtubeapi-329002")
            transcript = tr_response.translations[0].translated_text

        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if sock is not None:
            sock.send(bytes(transcript, "utf-8"))
        
        if print_locally: # print the result on the console.
            if not result.is_final:
                stdout.write(transcript + overwrite_chars + '\r')
                stdout.flush()
                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)
                num_chars_printed = 0


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--debug", default=False, action="store_true", 
                        help="show speech recognition result on the console")
    parser.add_argument("--connect", default=False, action="store_true", 
                        help="connect to unity")
    parser.add_argument("--src_lang_code", type=str, default="zh-tw",
                        help="the language code of the speech language")
    parser.add_argument("--tgt_lang_code", type=str, default="en",
                        help="""the language code of the language you want to translate to.
                        Set to empty string to disable translation.""")
    args = parser.parse_args()

    if args.connect:
        address = ('127.0.0.1', 5067)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
    else:
        sock = None

    sp_client = speech.SpeechClient()
    config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code=args.src_lang_code)
    streaming_config = \
        speech.StreamingRecognitionConfig(config=config, interim_results=True)

    if args.tgt_lang_code != "":
        tr_client = translate.TranslationServiceClient()
    else:
        tr_client = None

    print(f"{args.src_lang_code} recognition, {args.tgt_lang_code} translation started!")
    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (speech.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)
            try:
                sp_responses = sp_client.streaming_recognize(streaming_config, requests)
                listen_print_loop(sp_responses, tr_client, args.tgt_lang_code,
                                  print_locally=args.debug, sock=sock)
            except KeyboardInterrupt:
                break
            except: # ignore "400 Exceeded maximum allowed stream duration of 305 seconds."
                continue

    if sock is not None:
        sock.close()