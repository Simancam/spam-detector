from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# Step 1 - Read the Emails.txt file
with open('Emails.txt', 'r') as file:
    lines = file.readlines()

normal_emails = []
spam_emails = []
is_spam = False
quantity_normals_emails = 0
quantity_spam_emails = 0

targets = []
for line in lines:
    line = line.strip()
    if line == "":
        continue
    if "Normal e-mails" in line:
        continue  # Skip the "Normal e-mails" line
    if "Spam e-mails" in line:
        is_spam = True
        continue  # Skip the "Spam e-mails" line
    if is_spam:
        spam_emails.append(line.lower())
    else:
        normal_emails.append(line.lower())

# Get the counts of emails
quantity_normals_emails = len(normal_emails)
quantity_spam_emails = len(spam_emails)

# Get unique target words
targets = []

def fill_targets(array_emails):
    for email in array_emails:
        words = email.split()
        for word in words:
            if word not in targets:
                targets.append(word)

fill_targets(normal_emails)
fill_targets(spam_emails)

# Get the count of target words in each type of email
df = pd.DataFrame(targets, columns=['Word'])
df['Normal_Count'] = 0
df['Spam_Count'] = 0

# Function to count words in a list of emails
def count_targets_in_emails(emails, column_name):
    for email in emails:
        for word in email.split():
            if word in df['Word'].values:
                df.loc[df['Word'] == word, column_name] += 1

count_targets_in_emails(normal_emails, 'Normal_Count')
count_targets_in_emails(spam_emails, 'Spam_Count')

# Calculate the initial guess for each type of email
initial_guess_normal = (quantity_normals_emails / (quantity_normals_emails + quantity_spam_emails))
initial_guess_spam = (quantity_spam_emails / (quantity_spam_emails + quantity_normals_emails))

# Calculate probabilities
def calculate_probabilities():
    total_words_normal = sum(df['Normal_Count'])
    total_words_spam = sum(df['Spam_Count'])
    df['Normal_Probability'] = df['Normal_Count'] / total_words_normal
    df['Spam_Probability'] = df['Spam_Count'] / total_words_spam

calculate_probabilities()

# Apply Laplace Smoothing if there are zero probabilities
def apply_laplace_smoothing():
    df['Normal_Count'] += 1
    df['Spam_Count'] += 1
    calculate_probabilities()

# Function to classify the entered email
def classify_email(user_email):
    normal_prob = initial_guess_normal
    spam_prob = initial_guess_spam
    words = user_email.split()

    for word in words:
        if word in df['Word'].values:
            normal_word_prob = df.loc[df['Word'] == word, 'Normal_Probability'].values[0]
            spam_word_prob = df.loc[df['Word'] == word, 'Spam_Probability'].values[0]

            # If any probability is 0, apply Laplace Smoothing and recalculate
            if normal_word_prob == 0 or spam_word_prob == 0:
                apply_laplace_smoothing()
                normal_word_prob = df.loc[df['Word'] == word, 'Normal_Probability'].values[0]
                spam_word_prob = df.loc[df['Word'] == word, 'Spam_Probability'].values[0]

            normal_prob *= normal_word_prob
            spam_prob *= spam_word_prob

    return "spam" if spam_prob > normal_prob else "normal"

# Route to serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle email classification
@app.route('/classify', methods=['POST'])
def classify():
    email_text = request.json['email']
    classification = classify_email(email_text.lower())
    return jsonify({"classification": classification})

if __name__ == '__main__':
    app.run(debug=True)