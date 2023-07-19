import ssl
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import os

# Set the SSL certificate file path
ssl._create_default_https_context = ssl._create_unverified_context

# Set the NLTK data directory within the 'env' folder
nltk.data.path.append(os.path.join(os.getcwd(), 'nltk_data'))

nltk.download('wordnet')

# Continue with the rest of your code

# NORMALISATION
text1 = "Lurk lurks lurking lurkings lurked"

# Make words lowercase
text1_lower = text1.lower()

text1 = text1_lower.split(' ')

print("Normalised words:", text1)

# STEMMING
porter = PorterStemmer()
stemmed_words = [porter.stem(word) for word in text1]

lemmatizer = WordNetLemmatizer()
lemmatized_words = [lemmatizer.lemmatize(word) for word in text1]

print("Stemmed words:", stemmed_words)
print("Lemmatized words:", lemmatized_words)
