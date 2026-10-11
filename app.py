import streamlit as st
import random

st.set_page_config(page_title="Song Survivor Gu", page_icon="🎵")

# Initialize session state variables
if 'phase' not in st.session_state:
    st.session_state.phase = 'input'
    st.session_state.songs = []
    st.session_state.current_queue = []
    st.session_state.next_queue = []
    st.session_state.round = 1
    st.session_state.target_count = 1

def start_tournament(song_list, target_count):
    songs = [s.strip() for s in song_list.split('\n') if s.strip()]
    if len(songs) < 2:
        st.warning("Please enter at least 2 songs into the pot!")
        return
    
    if target_count >= len(songs):
        st.warning(f"Target count must be less than the total number of songs ({len(songs)}).")
        return

    random.shuffle(songs)
    st.session_state.songs = songs
    st.session_state.target_count = target_count
    st.session_state.current_queue = create_pairs(songs)
    st.session_state.next_queue = []
    st.session_state.phase = 'battle'
    st.session_state.round = 1

def create_pairs(songs):
    pairs = []
    for i in range(0, len(songs), 2):
        if i + 1 < len(songs):
            pairs.append((songs[i], songs[i+1]))
        else:
            pairs.append((songs[i], None))  # Odd one out gets a free pass
    return pairs

def handle_vote(choice, pair):
    # Route survivors
    if choice == 'A':
        st.session_state.next_queue.append(pair[0])
    elif choice == 'B':
        st.session_state.next_queue.append(pair[1])
    elif choice == 'Both':
        st.session_state.next_queue.append(pair[0])
        st.session_state.next_queue.append(pair[1])
    
    # Remove the battled pair
    st.session_state.current_queue.pop(0)
    
    # Check if the current round is complete
    if len(st.session_state.current_queue) == 0:
        survivors = st.session_state.next_queue
        
        # STOP CONDITIONS:
        # 1. Target reached: Pool shrank to or below target count
        # 2. Stalemate: User chose "Both" for every single match this round (prevent infinite loop)
        if len(survivors) <= st.session_state.target_count or len(survivors) == len(st.session_state.songs):
            st.session_state.phase = 'results'
            st.session_state.songs = survivors
        else:
            # Advance to the next round
            st.session_state.songs = survivors
            random.shuffle(survivors)
            st.session_state.current_queue = create_pairs(survivors)
            st.session_state.next_queue = []
            st.session_state.round += 1

# --- UI LAYOUT ---
st.title("🎵 Song Gu Tournament")
st.markdown("Narrow your songs down to your top survivors.")

if st.session_state.
