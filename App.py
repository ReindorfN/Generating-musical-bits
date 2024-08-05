import streamlit as st
import music_bits



if __name__ == "__main__":
    text_description = st.text_input("Describe the type of beat you want to create: ").lower()
    genre = st.text_input("Select a genre: ").lower()
    
    # Output file name
    output_file = 'final_beat.wav'
    try:
        result = music_bits.generate_music_from_text(text_description, genre)
        print("Music generated successfully!")

        #for i, items in enumerate(result):
            #print(f'item {i}, download: {items}')

        downloaded_files = music_bits.download_wav_files(result)
        print(f"Downloaded files: {downloaded_files}")

        final_output = music_bits.blend_wav_files(downloaded_files, output_file)
    except Exception as e:
        print(e)
