
import random
import re
import logging
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('markov_chain')

class MarkovChainGenerator:
    """A class to generate text using Markov chains."""
    
    def __init__(self, order=2):
        """Initialize the Markov Chain generator.
        
        Args:
            order (int): The number of words to consider for state (default: 2)
        """
        self.order = order
        self.markov_chain = {}
        logger.info(f"Initialized MarkovChainGenerator with order {order}")
        
    def clean_text(self, text):
        """Clean and normalize text.
        
        Args:
            text (str): Input text to clean
            
        Returns:
            str: Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters except punctuation needed for sentence structure
        text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)
        return text.strip()
        
    def build_chain(self, text):
        """Build a Markov chain from the input text.
        
        Args:
            text (str): Text to build the chain from
            
        Returns:
            dict: The built Markov chain
        """
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        
        if len(words) <= self.order:
            logger.warning("Text too short to build chain with current order")
            return {}
        
        logger.info(f"Building Markov chain from {len(words)} words")
        
        for i in range(len(words) - self.order):
            key = tuple(words[i:i+self.order])  # Create key (tuple of words)
            next_word = words[i + self.order]  # Get next word
            
            if key not in self.markov_chain:
                self.markov_chain[key] = []
            self.markov_chain[key].append(next_word)
            
        logger.info(f"Built chain with {len(self.markov_chain)} states")
        return self.markov_chain
    
    def build_from_file(self, filepath):
        """Build a Markov chain from a text file.
        
        Args:
            filepath (str): Path to the text file
            
        Returns:
            dict: The built Markov chain
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
            logger.info(f"Successfully loaded text from {filepath}")
            return self.build_chain(text)
        except Exception as e:
            logger.error(f"Error loading file {filepath}: {str(e)}")
            return {}
    
    def generate_text(self, length=50, start_words=None):
        """Generate text using the built Markov chain.
        
        Args:
            length (int): Length of text to generate in words
            start_words (list): Optional list of starting words
            
        Returns:
            str: Generated text
        """
        if not self.markov_chain:
            logger.error("Cannot generate text: Markov chain is empty")
            return "Error: Markov chain not built yet."
            
        # Choose starting point
        if start_words and len(start_words) >= self.order:
            # Use provided starting words if they exist in the chain
            key = tuple(start_words[-self.order:])
            if key not in self.markov_chain:
                logger.warning(f"Starting words {start_words} not found in chain, using random start")
                key = random.choice(list(self.markov_chain.keys()))
            generated_words = list(start_words)
        else:
            # Use random starting point
            key = random.choice(list(self.markov_chain.keys()))
            generated_words = list(key)
            
        logger.info(f"Generating text with length {length}, starting with {key}")
        
        for _ in range(length - len(generated_words)):
            if key in self.markov_chain and self.markov_chain[key]:
                next_word = random.choice(self.markov_chain[key])
                generated_words.append(next_word)
                # Update key with the new sequence of words
                key = tuple(generated_words[-self.order:])
            else:
                logger.info("Reached end state with no transitions")
                break
                
        return " ".join(generated_words)

def main():
    """Main function to run the Markov Chain generator from command line."""
    parser = argparse.ArgumentParser(description='Generate text using a Markov Chain')
    parser.add_argument('--file', type=str, help='Input text file')
    parser.add_argument('--text', type=str, help='Input text directly')
    parser.add_argument('--order', type=int, default=2, help='Markov chain order (default: 2)')
    parser.add_argument('--length', type=int, default=50, help='Length of generated text (default: 50)')
    parser.add_argument('--start', type=str, help='Starting words (comma separated)')
    
    args = parser.parse_args()
    
    generator = MarkovChainGenerator(order=args.order)
    
    # Build chain from file or text
    if args.file:
        generator.build_from_file(args.file)
    elif args.text:
        generator.build_chain(args.text)
    else:
        # Use sample text if no input provided
        sample_text = """This is a simple example of a Markov Chain text generator. 
        Markov chains are used to model sequences of words based on probabilities.
        The order of a Markov chain determines how many previous words are considered.
        Higher order chains produce more coherent text but require more data."""
        generator.build_chain(sample_text)
    
    # Parse starting words if provided
    start_words = None
    if args.start:
        start_words = args.start.split(',')
    
    # Generate and print text
    generated_text = generator.generate_text(length=args.length, start_words=start_words)
    print("🔹 Generated Text:\n", generated_text)

if __name__ == "__main__":
    main()
