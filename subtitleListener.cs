using UnityEngine;
using UnityEngine.UI;
using System.Threading;
using System.Net.Sockets;
using System.Net;
using System;
using System.Text;
using System.Collections;

public class subtitleListener : MonoBehaviour
{
    private Text subtitle;

    // Thread
    Thread receiveThread;
    TcpClient client;
    TcpListener listener;
    int port = 5067;
    string receivedText = "", prevText = "";
    int sameCount = 0;

    // Start is called before the first frame update
    void Start()
    {
        subtitle = GetComponent<Text>();

        InitTCP();
    }

    // Update is called once per frame
    void Update()
    {
        if (prevText.Equals(receivedText))
        {
            sameCount++;
            if (sameCount == 60) // if no speech for two seconds, erase the subtitle.
            {
                receivedText = "";
            }
        } else
        {
            sameCount = 0;
        }
        subtitle.text = receivedText;
        prevText = receivedText;
    }

    private void InitTCP()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    private void ReceiveData()
    {
        try
        {
            listener = new TcpListener(IPAddress.Parse("127.0.0.1"), port);
            listener.Start();
            Byte[] bytes = new Byte[1024];
            while (true)
            {
                using (client = listener.AcceptTcpClient())
                {
                    using (NetworkStream stream = client.GetStream())
                    {
                        int length;
                        while ((length = stream.Read(bytes, 0, bytes.Length)) != 0)
                        {
                            var incommingData = new byte[length];
                            Array.Copy(bytes, 0, incommingData, 0, length);
                            receivedText = Encoding.UTF8.GetString(incommingData);
                            if (receivedText.Length > 32) // if the text is longer than 32 words,
                                                          // cut the subtitle and print in new
                                                          // line.
                            {
                                int startIndex = 32 * (receivedText.Length / 32);
                                receivedText = receivedText.Substring(startIndex);
                            }
                        }
                    }
                }
            }
        }
        catch (Exception e)
        {
            print(e.ToString());
        }
    }

    void OnApplicationQuit()
    {
        try
        {
            receiveThread.Abort();
            client.Close();
            listener.Stop();
        }
        catch (Exception e)
        {
            Debug.Log(e.Message);
        }

    }
}
