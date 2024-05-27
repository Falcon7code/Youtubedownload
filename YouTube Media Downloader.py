import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import http.client
import threading
import json
import ssl
from pytube import YouTube

def fetch_video_details():
    video_id = video_id_entry.get().strip()
    if not video_id:
        messagebox.showerror("Error", "Please enter a video ID")
        return

    # Check if video_id looks like a URL
    if "youtube.com" in video_id or "youtu.be" in video_id:
        messagebox.showerror("Error", "Please enter only the video ID, not the full URL")
        return

    progress_label.config(text="Fetching video details...")
    progress_bar.start()

    def api_call():
        # Create an SSL context to ignore certificate verification
        context = ssl._create_unverified_context()
        conn = http.client.HTTPSConnection("youtube-media-downloader.p.rapidapi.com", context=context)

        headers = {
            'x-rapidapi-key': "eabb72b3d0mshdecf177b50e29dcp1990f2jsn813d42ee3318",
            'x-rapidapi-host': "youtube-media-downloader.p.rapidapi.com"
        }

        try:
            conn.request("GET", f"/v2/video/details?videoId={video_id}", headers=headers)
            res = conn.getresponse()
            data = res.read()
            if res.status != 200:
                error_message = f"HTTP error occurred: {res.status} - {res.reason}\n{data.decode('utf-8')}"
                display_error(error_message)
                return

            video_details = json.loads(data.decode("utf-8"))
            display_video_details(video_details)
            download_button.config(state=tk.NORMAL)
        except Exception as err:
            error_message = f"An error occurred: {err}"
            display_error(error_message)
        finally:
            conn.close()
            progress_bar.stop()
            progress_label.config(text="")

    threading.Thread(target=api_call).start()

def display_video_details(details):
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, json.dumps(details, indent=4))

def display_error(message):
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, message)

def download_video():
    video_id = video_id_entry.get().strip()
    if not video_id:
        messagebox.showerror("Error", "Please enter a video ID")
        return
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if not file_path:
        return

    progress_label.config(text="Downloading video...")
    progress_bar.start()

    def download():
        try:
            yt = YouTube(url)
            stream = yt.streams.get_highest_resolution()
            stream.download(output_path=file_path)
            messagebox.showinfo("Success", "Video downloaded successfully!")
        except Exception as err:
            error_message = f"An error occurred: {err}"
            display_error(error_message)
        finally:
            progress_bar.stop()
            progress_label.config(text="")

    threading.Thread(target=download).start()

# Setting up the GUI
root = tk.Tk()
root.title("YouTube Video Details Fetcher - Pokédex Style")
root.geometry("800x600")
root.configure(bg="#f0f0f0")

# Title Label
title_label = tk.Label(root, text="YouTube Video Details Fetcher", font=("Helvetica", 16, "bold"), bg="#ff0000", fg="#ffffff", borderwidth=2, relief="solid")
title_label.pack(pady=10)

# Frame for Entry and Button
frame = tk.Frame(root, bg="#ffcb05", borderwidth=2, relief="solid")
frame.pack(pady=20)

video_id_label = tk.Label(frame, text="Enter YouTube Video ID:", font=("Helvetica", 12, "bold"), bg="#ffcb05", fg="#000000")
video_id_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

video_id_entry = tk.Entry(frame, width=40, font=("Helvetica", 12))
video_id_entry.grid(row=0, column=1, padx=5, pady=5)

fetch_button = tk.Button(frame, text="Fetch Video Details", font=("Helvetica", 12, "bold"), bg="#3b4cca", fg="#ffffff", command=fetch_video_details)
fetch_button.grid(row=0, column=2, padx=5, pady=5)

download_button = tk.Button(root, text="Download Video", font=("Helvetica", 12, "bold"), bg="#4caf50", fg="#ffffff", state=tk.DISABLED, command=download_video)
download_button.pack(pady=10)

# Progress Indicator
progress_label = tk.Label(root, text="", font=("Helvetica", 10, "italic"), bg="#f0f0f0")
progress_label.pack(pady=5)

progress_bar = ttk.Progressbar(root, mode="indeterminate")
progress_bar.pack(pady=5, fill="x", padx=20)

# Result Display
result_label = tk.Label(root, text="Video Details:", font=("Helvetica", 12, "bold"), bg="#ffcb05", fg="#000000", borderwidth=2, relief="solid")
result_label.pack(pady=10)

result_text = tk.Text(root, height=20, width=70, font=("Helvetica", 12), wrap="word", borderwidth=2, relief="solid", bg="#ffffff", fg="#000000")
result_text.pack(pady=10)

root.mainloop()
