# Unity_live_caption
利用 Google Speech-to-Text API 和 Unity 來做實時直播上字幕！ 可以跟你的虛擬腳色很好的搭配使用！

**重要訊息 : 這個API是要收費的！ 收費規則在[這裡](https://cloud.google.com/speech-to-text/pricing).**

這是我 [youtube直播](https://www.youtube.com/watch?v=AZsUm_cuj9U) 演示的結果。

## 前置作業

你要先有google帳號。

根據[官網](https://cloud.google.com/speech-to-text/)的指示，在主控台啟用`Speech-to-Text` API，並且下載API金鑰(會是一個`.json`檔)。

中文的話我只介紹圖形介面(GUI)怎麼使用，如果想從命令行執行的話，請參照英文的[README](README.md)。

## Usage

1.  Test if speech recognition works in python:
    1. Change [here](https://github.com/kwea123/Unity_live_caption/blob/master/googlesr.py#L9) to where your `key.json` is located.
    2. Run `python googlesr.py --debug --lang_code={YOUR LANGUAGE CODE}`. For the language codes, check [here](https://cloud.google.com/speech-to-text/docs/languages). You should see the recognition output on the console.

2.  Output the recognition result to unity:
    1.  Create a Text component via `GameObject->UI->Text`.
    2.  Attach `subtitleListener.cs` to it.
    3.  Run the unity program **FIRST**, either in editor or executable, then run `python googlesr.py --lang_code={YOUR LANGUAGE CODE} --connect`. You should see the recognition output now in unity. You can stop and restart the recognition anytime by pressing `Ctrl` and `c` in the python console without affecting the unity program at all.
    
3.  **Remember to stop the python program when you finish the work, otherwise it is going to keep charging you! I disclaim any reponsibility of the induced charges by using my program.**
    
## Customization

1.  You can change the connection port by changing the port number (default 5067) [here](https://github.com/kwea123/Unity_live_caption/blob/master/googlesr.py#L127) and [here](https://github.com/kwea123/Unity_live_caption/blob/master/subtitleListener.cs#L18)

2.  You can change how the text is printed on unity [here](https://github.com/kwea123/Unity_live_caption/blob/master/subtitleListener.cs#L73-L79) and [here](https://github.com/kwea123/Unity_live_caption/blob/master/subtitleListener.cs#L36-L39). The default is configured to print at most 32 characters in Chinese, so you might need to change if you're not using Chinese.

## GUI usage

1.  Download `googlesr_gui_english.zip` from [here](https://github.com/kwea123/Unity_live_caption/releases/tag/v1.0).

2.  Open `googlesr_gui_english.exe` and you will see

![alt](images/1.png)

3.  Select your language, set the API key to where you downloaded `key.json` and select whether to connect to unity and/or print to console.

4.  Press Start to start. It takes some time to warm-up. When it's ready, you will see the following and you can start to talk. You can adjust the size of this window.

![alt](images/2.png)

5.  Press `Ctrl` and `c` to stop the program when you finish.

6.  **Remember to stop the program when you finish the work, otherwise it is going to keep charging you! I disclaim any reponsibility of the induced charges by using my program.**

## Other issues
Please ask in [issue](https://github.com/kwea123/Unity_live_caption/issues)

