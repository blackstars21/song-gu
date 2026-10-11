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

def start_tournament(song_list):
    songs = [s.strip() for s in song_list.split('\n') if s.strip()]
    if len(songs) < 2:
        st.warning("Please enter at least 2 songs into the pot!")
        return
    
    random.shuffle(songs)
    st.session_state.songs = songs
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
            pairs.append((songs[i], None)) # Odd one out gets a free pass
    return pairs

def handle_vote(choice, pair):
    # Route the survivors
    if choice == 'A':
        st.session_state.next_queue.append(pair[0])
    elif choice == 'B':
        st.session_state.next_queue.append(pair[1])
    elif choice == 'Both':
        st.session_state.next_queue.append(pair[0])
        st.session_state.next_queue.append(pair[1])
    
    # Remove the battled pair from the current queue
    st.session_state.current_queue.pop(0)
    
    # Check if the round is over
    if len(st.session_state.current_queue) == 0:
        next_round_songs = st.session_state.next_queue
        
        # Stop condition: 1 song left OR user chose "Both" for every pair this round
        if len(next_round_songs) <= 1 or len(next_round_songs) == len(st.session_state.songs):
            st.session_state.phase = 'results'
            st.session_state.songs = next_round_songs
        else:
            # Setup next round
            st.session_state.songs = next_round_songs
            random.shuffle(next_round_songs)
            st.session_state.current_queue = create_pairs(next_round_songs)
            st.session_state.next_queue = []
            st.session_state.round += 1

# --- UI LAYOUT ---
st.title("🎵 Song Gu Tournament")
st.markdown("Throw your songs into the pot. Only the strongest survive.")

if st.session_state.phase == 'input':
    song_input = st.text_area("Paste your songs (one per line):", value=default_songs, height=200)
    
    if st.button("Seal the Pot (Start)", use_container_width=True):
        start_tournament(song_input)
        st.rerun()

elif st.session_state.phase == 'battle':
    st.subheader(f"Round {st.session_state.round}")
    
    if len(st.session_state.current_queue) > 0:
        current_pair = st.session_state.current_queue[0]
        
        if current_pair[1] is None:
            st.info(f"**{current_pair[0]}** got lucky and advances automatically this round!")
            handle_vote('A', current_pair)
            st.button("Next Match", use_container_width=True)
        else:
            st.write("### Which one survives?")
            
            # Create three equal columns for the buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"👈 {current_pair[0]}", use_container_width=True):
                    handle_vote('A', current_pair)
                    st.rerun()
            with col2:
                if st.button("🤝 Both Survive", use_container_width=True):
                    handle_vote('Both', current_pair)
                    st.rerun()
            with col3:
                if st.button(f"{current_pair[1]} 👉", use_container_width=True):
                    handle_vote('B', current_pair)
                    st.rerun()
            
            # Progress bar for the current round
            total_matches = max(1, len(st.session_state.songs) // 2)
            matches_left = len(st.session_state.current_queue)
            st.progress((total_matches - matches_left) / total_matches)

elif st.session_state.phase == 'results':
    st.success("The dust has settled.")
    st.write("### Your Ultimate Survivors:")
    
    for i, song in enumerate(st.session_state.songs, 1):
        st.markdown(f"**{i}. {song}**")
        
    if st.button("Start a New Tournament", use_container_width=True):
        st.session_state.phase = 'input'
        st.rerun()
