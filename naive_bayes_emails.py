import pandas as pd

# Step 1: Classify emails into normal and spam categories
def classify_emails(file_path):
    normal_emails, spam_emails = [], []
    is_spam = False

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip().lower()

            if not line:
                continue
            if "normal e-mails" in line:
                continue
            if "spam e-mails" in line:
                is_spam = True
                continue

            if is_spam:
                spam_emails.append(line)
            else:
                normal_emails.append(line)

    return normal_emails, spam_emails


# Step 2: Extract unique target words from the emails
def extract_targets(emails):
    targets = []
    for email in emails:
        for word in email.split():
            if word not in targets:
                targets.append(word)
    return targets


# Step 3: Find occurrences of each word in normal and spam emails
def count_targets_in_emails(df, emails, column_name):
    for email in emails:
        for word in email.split():
            if word in df['Word'].values:
                df.loc[df['Word'] == word, column_name] += 1


# Step 4: Calculate word probabilities for normal and spam emails
def calculate_probabilities(df):
    total_words_normal = df['Normal_Count'].sum()
    total_words_spam = df['Spam_Count'].sum()

    df['Normal_Probability'] = df['Normal_Count'] / total_words_normal
    df['Spam_Probability'] = df['Spam_Count'] / total_words_spam


# Step 5: Apply Laplace Smoothing to prevent zero probabilities
def apply_laplace_smoothing(df):
    df['Normal_Count'] += 1
    df['Spam_Count'] += 1
    calculate_probabilities(df)


# Step 6: Classify an email as spam or normal based on probabilities
def classify_email(user_email, df, initial_guess_normal, initial_guess_spam):
    normal_prob = initial_guess_normal
    spam_prob = initial_guess_spam

    # Loop through each word in the user email
    for word in user_email.split():
        if word in df['Word'].values:
            # Get word probabilities for both normal and spam emails
            normal_word_prob = df.loc[df['Word'] == word, 'Normal_Probability'].values[0]
            spam_word_prob = df.loc[df['Word'] == word, 'Spam_Probability'].values[0]

            # Apply smoothing if any probability is zero
            if normal_word_prob == 0 or spam_word_prob == 0:
                apply_laplace_smoothing(df)
                normal_word_prob = df.loc[df['Word'] == word, 'Normal_Probability'].values[0]
                spam_word_prob = df.loc[df['Word'] == word, 'Spam_Probability'].values[0]

            # Multiply the probabilities for classification
            normal_prob *= normal_word_prob
            spam_prob *= spam_word_prob

    # Return the classification result based on the probabilities
    return "The email is normal." if normal_prob > spam_prob else "The email is spam."


# Step 7: Classify emails from the text file
normal_emails, spam_emails = classify_emails('Emails.txt')

print("\nNormal Emails:")  
print(", ".join(normal_emails))

print("\nSpam Emails:") 
print(", ".join(spam_emails))

# Step 8: Count emails and display counts
quantity_normals_emails = len(normal_emails)
quantity_spam_emails = len(spam_emails)

print(f"\nTotal Normal Emails: {quantity_normals_emails}") 
print(f"Total Spam Emails: {quantity_spam_emails}")

# Step 9: Extract target words from both normal and spam emails
targets = extract_targets(normal_emails + spam_emails)

print("\nTarget Words:") 
print(", ".join(targets))

# Step 10: Create a DataFrame for word counts and probabilities
df = pd.DataFrame(targets, columns=['Word'])
df['Normal_Count'] = 0
df['Spam_Count'] = 0

# Step 11: Count the occurrences of each target word in normal and spam emails
count_targets_in_emails(df, normal_emails, 'Normal_Count')
count_targets_in_emails(df, spam_emails, 'Spam_Count')

# Step 12: Log the total word counts for normal and spam emails
total_words_normal = df['Normal_Count'].sum()
total_words_spam = df['Spam_Count'].sum()

print(f"\nTotal Words in Normal Emails: {total_words_normal}")
print(f"Total Words in Spam Emails: {total_words_spam}") 

# Step 13: Calculate the probabilities of each word
calculate_probabilities(df)

# Displaying the DataFrame with counts and probabilities
print("\nDataFrame with Word Counts and Probabilities:")  # Prints the DataFrame showing counts and probabilities
print(df)

# Step 14: Calculate the initial guess for normal and spam emails
initial_guess_normal = quantity_normals_emails / (quantity_normals_emails + quantity_spam_emails)
initial_guess_spam = quantity_spam_emails / (quantity_spam_emails + quantity_normals_emails)

# Step 15: Classify a user input email
user_email = input("\nEnter the email to analyze: ").lower()
result = classify_email(user_email, df, initial_guess_normal, initial_guess_spam)
print("\n" + result)