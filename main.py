import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from chain import MarkovChainGenerator

def main():
    st.set_page_config(
        page_title="Markov Text Generator",
        page_icon="🔤",
        layout="wide"
    )
    
    st.markdown("""
   <h1 style='text-align: center;'>🔄 Markov Chain Text Generator</h1>
   """, unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; font-size: 15px;'>
    Generate realistic text using Markov Chains. Enter your own text to create
    a model that generates new content based on the patterns in your input.
    </div>
""", unsafe_allow_html=True)

    
    # Sidebar for parameters and additional sections
    st.sidebar.header("⚙️ Parameters")
    order = st.sidebar.slider("Chain Order (words to consider)", 1, 5, 2, 
                          help="Higher values create more coherent but less creative text")
    length = st.sidebar.slider("Output Length (words)", 10, 500, 100)
    
    # Sidebar "About" section
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ About This App")
    st.sidebar.markdown("""
    This app generates text based on a Markov Chain model. 
    You can upload your own text or choose from pre-defined sample texts to create 
    new text sequences. It uses a statistical method where the probability 
    of each word depends on the previous word(s).
    """)

    # Initialize the generator
    generator = MarkovChainGenerator(order=order)
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📝 Enter Text", "📊 Analysis"])
    
    with tab1:
        st.subheader("Enter Your Text")
        
        # Sample texts dropdown
        sample_option = st.selectbox(
            "Choose a sample text:",
            ["None", "Lorem Ipsum", "Adventure", "Inspirational Quote", "Technology & Innovation", "Programming Concepts"]
        )
        
        sample_texts = {
            "Lorem Ipsum": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "Adventure": "In the heart of the jungle, a brave explorer embarks on a quest to uncover the lost city of gold. With every step, danger lurks around every corner, but the allure of discovering something extraordinary keeps them moving forward. The path is treacherous, and only the most courageous will survive the wild terrain and unravel the mysteries of the ancient world.",
            "Inspirational Quote": "The future belongs to those who believe in the beauty of their dreams. Every challenge faced today is an opportunity to grow stronger, wiser, and more resilient. The road ahead may be uncertain, but with courage and determination, anything is possible. Embrace the journey, for it is through the struggle that greatness is achieved.",
            "Technology & Innovation": "In the rapidly evolving world of technology, innovations are happening at an unprecedented pace. From artificial intelligence to blockchain, new breakthroughs are shaping industries and transforming how we live, work, and interact. As we move into the future, it's essential to embrace these advancements, staying curious and adaptable to the ever-changing landscape of technology.",
            "Programming Concepts": "Python is a high-level, interpreted programming language. It is known for its readability and simplicity. Functions are first-class objects in Python, which means they can be assigned to variables, passed as arguments, and returned from other functions. Object-oriented programming is supported through classes and inheritance. Python's standard library provides many modules for common tasks."
        }
        
        if sample_option != "None":
            text_input = st.text_area("Input Text", value=sample_texts[sample_option], height=200)
        else:
            text_input = st.text_area("Input Text", height=200, 
                                   placeholder="Enter text here to build a Markov chain...")
        
        starting_words = st.text_input("Starting Words (optional, comma-separated)", 
                                    placeholder="e.g., The cat, Once upon")
        
        start_button = st.button("🚀 Generate Text", key="generate_text")
        
        if start_button and text_input:
            generator.build_chain(text_input)
            
            start_list = None
            if starting_words:
                start_list = starting_words.split(',')
                
            generated_text = generator.generate_text(length=length, start_words=start_list)
            
            st.subheader("📝 Generated Text:")
            st.markdown(f"*{generated_text}*")
            
            # Add download button for generated text
            st.download_button(
                label="Download Generated Text",
                data=generated_text,
                file_name="markov_generated_text.txt",
                mime="text/plain"
            )
    
    with tab2:
        st.subheader("Markov Chain Analysis")
        
        text_for_analysis = st.text_area(
            "Enter text for analysis:", 
            height=150,
            placeholder="Enter text to analyze its Markov chain properties...",
            key="analysis_text"
        )
        
        analyze_button = st.button("📊 Analyze Text", key="analyze")
        
        if analyze_button and text_for_analysis:
            # Build the chain and analyze
            chain = generator.build_chain(text_for_analysis)
            
            # Display stats
            st.write(f"📊 **Chain Statistics:**")
            st.write(f"- Total number of states: {len(chain)}")
            
            # Find most common transitions
            transition_counts = {}
            for key, values in chain.items():
                for word in values:
                    state_str = ' '.join(key)
                    transition = f"'{state_str}' → '{word}'"
                    if transition in transition_counts:
                        transition_counts[transition] += 1
                    else:
                        transition_counts[transition] = 1
            
            # Display top transitions
            if transition_counts:
                st.write("🔝 **Top Transitions:**")
                
                # Convert to dataframe for better display
                transitions_df = pd.DataFrame({
                    'Transition': list(transition_counts.keys()),
                    'Count': list(transition_counts.values())
                }).sort_values('Count', ascending=False).head(10)
                
                st.dataframe(transitions_df, use_container_width=True)
                
                # Find dead ends (states with no outgoing transitions)
                all_states = set()
                for key in chain.keys():
                    all_states.add(' '.join(key))
                    
                # Calculate vocabulary size
                vocabulary = set()
                for key in chain.keys():
                    for word in key:
                        vocabulary.add(word)
                for values in chain.values():
                    for word in values:
                        vocabulary.add(word)
                
                st.write(f"📚 **Vocabulary size:** {len(vocabulary)} unique words")
                st.write(f"🔄 **Average transitions per state:** {sum(len(v) for v in chain.values()) / len(chain) if chain else 0:.2f}")
                
                # Generate text sample for comparison
                st.write("💡 **Sample generation:**")
                sample = generator.generate_text(length=30)
                st.write(sample)
                
                # Visualization of word frequency
                st.write("📈 **Word Frequency Visualization:**")
                word_freq = pd.Series(list(vocabulary)).value_counts()
                fig, ax = plt.subplots()
                word_freq.head(10).plot(kind='bar', ax=ax, color='skyblue')
                ax.set_xlabel("Words")
                ax.set_ylabel("Frequency")
                ax.set_title("Top 10 Most Frequent Words in the Chain")
                st.pyplot(fig)

if __name__ == "__main__":
    main()
