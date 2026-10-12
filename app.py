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

if st.session_state.phase == 'input':
    default_songs = "Live My Life - aespa\nWedding Dress - TAEYANG\nDash - NMIXX\nUntouchable - ITZY\nEyes, Nose, Lips - TAEYANG\nSupernova - aespa"
    song_input = st.text_area("Paste your songs (one per line):", value=default_songs, height=180)
    
    # Dynamic target count selector
    target = st.number_input(
        "Stop when the pot narrows down to (Target Top N):",
        min_value=1,
        max_value=100,
        value=3,
        step=1
    )
    
    if st.button("Seal the Pot (Start)", use_container_width=True):
        start_tournament(song_input, target)
        st.rerun()

elif st.session_state.phase == 'battle':
    # Live tracker header
    songs_remaining = len(st.session_state.current_queue) * 2 + len(st.session_state.next_queue)
    st.subheader(f"Round {st.session_state.round}")
    st.caption(f"🎯 Target pool: **≤ {st.session_state.target_count} songs**")
    
    if len(st.session_state.current_queue) > 0:
        current_pair = st.session_state.current_queue[0]
        
        if current_pair[1] is None:
            st.info(f"**{current_pair[0]}** got a bye and advances automatically!")
            handle_vote('A', current_pair)
            st.button("Next Match", use_container_width=True)
        else:
            st.write("### Which one survives?")
            
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
            
            st.divider()
            
            # --- EARLY STOP BUTTON ---
            if st.button("🛑 Stop Tournament Early & Show Remaining Songs", use_container_width=True):
                # Gather songs that already survived this round
                remaining_songs = list(st.session_state.next_queue)
                
                # Gather songs that are still waiting to battle in the current round
                for pair in st.session_state.current_queue:
                    remaining_songs.append(pair[0])
                    if pair[1] is not None:
                        remaining_songs.append(pair[1])
                
                # Update state to skip straight to results
                st.session_state.songs = remaining_songs
                st.session_state.phase = 'results'
                st.rerun()

elif st.session_state.phase == 'results':
    st.success("The tournament has ended. The pot has settled.")
    st.write(f"### Final Survivors ({len(st.session_state.songs)} total):")
    
    for i, song in enumerate(st.session_state.songs, 1):
        st.markdown(f"**{i}. {song}**")
        
    if st.button("Start a New Tournament", use_container_width=True):
        st.session_state.phase = 'input'
        st.rerun()
