

import streamlit as st
import time
import requests
import os
from urllib.parse import urlparse, parse_qs
import json
import numpy as np
import soundfile as sf
#!pip install note_seq
import note_seq
import note_seq
import librosa






# Function to generate music from text
def generate_music_from_text(text_description, genre):
    url = f"{BASE_URL}/generate-music"
    instruments = []
    all_midis = []

    pop = ("piano", "guitar", "synthesizer", "drums", "vocals")
    jazz = ("saxophone", "trumpet", "trombone", "piano", "guitar")
    hip_hop = ("drum machine", "keyboard", "sampler", "bass", "guitar")
    gospel = ("Hammond organ", "tambourines", "drums", "bass guitar", "keyboard")
    
    
    if genre == "pop":
        instruments = pop
    elif genre == "jazz":
        instruments = jazz
    elif genre == "hip-hop":
        instruments = hip_hop
    elif genre == "gospel":
        instruments = gospel
    else:
        print("Sorry, selected genre not configured yet!!")
      

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    for item in instruments:
        data = {
            'prompt': item,
            'text': text_description,
            'genre': genre
        }

        response = session.request("POST",url, headers=headers, json=data, verify=False).text

        #Using json formatting to extract the html link from the response of the request
        data = json.loads(response)
        file_url = data[0]['file_url']
        
        all_midis.append(file_url)
        
    #print(response.text)
    return all_midis



def download_wav_files(links):
    wav_files = []
    for index, link in enumerate(links):
        try:
            response = requests.get(link)
            response.raise_for_status()  # Check if the request was successful

            parsed_url = urlparse(link)
            file_name = os.path.basename(parsed_url.path)
            file_extension = os.path.splitext(file_name)[1]
            
            if not file_extension:
                file_extension = '.wav'
                
            filename = f'wave_{index}{file_extension}'

            with open(filename, 'wb') as wav_file:
                wav_file.write(response.content)
            wav_files.append(filename)
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {link}: {e}")
    return wav_files


def blend_wav_files(wav_paths, output_path):
    valid_wavs = []
    
    for path in wav_paths:
        try:
            # Try loading the WAV file to ensure it is valid
            wav, sr = librosa.load(path, sr=None)
            valid_wavs.append((wav, sr))
        except Exception as e:
            print(f"Failed to load {path}: {e}")
    
    if not valid_wavs:
        print("No valid WAV files to blend.")
        return
    
    # Find the minimum length to avoid issues with different lengths
    min_length = min([len(wav[0]) for wav in valid_wavs])
    
    # Truncate all wav files to the same length
    wavs = [wav[0][:min_length] for wav in valid_wavs]
    
    # Stack and average the wav files to blend them
    blended_wav = np.mean(wavs, axis=0)

    # Delete the content of the output file if it exists
    if os.path.exists(output_path):
        print(f"Output file {output_path} already exists and will be replaced.")
        os.remove(output_path)
        
    else:
        print(f"Output file {output_path} does not exist. Creating it now.")
    
    # Save the blended wav file
    sf.write(output_path, blended_wav, valid_wavs[0][1])
    print(f"Blended WAV file saved as {output_path}")



if __name__ == "__main__":


    html_temp = """
    <div style="background-color:tomato;padding:10px">
    <h2 style="color:white;text-align:center;">Musical Bits Generator App</h2>
    </div>
    """
    st.markdown(html_temp,unsafe_allow_html=True)

    API_KEY = "clzg6zq880004jy0cykcuqehm"
    BASE_URL = 'https://api.musicfy.lol/v1'

    session = requests.Session()
    session.verify = False
    
    text_description = st.text_input("Describe the type of beat you want to create: ").lower()
    genre = st.selectbox("Select a genre: ", ['jazz', 'gospel', 'pop', 'hip-hop'])
    
    # Output file name
    output_file = 'final_beat.wav'



    if st.button("Generate beat"):
        inputs = {
            'text_description': text_description,
            'genre': genre
        }

        try:
            with st.spinner('Cooking your beat😁'):
                result = generate_music_from_text(text_description, genre)
                print("Music generated successfully!")

                downloaded_files = download_wav_files(result)
                print(f"Downloaded files: {downloaded_files}")

                final_output = blend_wav_files(downloaded_files, output_file)
    
            st.success("Congratulations!! :)")   


            st.audio("final_beat.wav", format="audio/wav", start_time=0, sample_rate=None, end_time=None, loop=False, autoplay=False)
        except ValueError as e:
            st.error(f'Predictiion error: {e}')
        

    if st.button("About"):
        st.text("""
Building an Ai model that generates musical beats for users who may have a song but 
do not have the capacity to generate their own musical beats.
""")
