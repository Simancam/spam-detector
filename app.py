from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

# Configurar Flask con carpetas correctas
app = Flask(__name__, template_folder="templates", static_folder="static")

# Leer el archivo Emails.txt si existe
emails_file = 'Emails.txt'
if os.path.exists(emails_file):
    with open(emails_file, 'r') as file:
        lines = file.readlines()
else:
    lines = []

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
        continue
    if "Spam e-mails" in line:
        is_spam = True
        continue
    if is_spam:
        spam_emails.append(line.lower())
    else:
        normal_emails.append(line.lower())

quantity_normals_emails = len(normal_emails)
quantity_spam_emails = len(spam_emails)

# Obtener palabras únicas
def fill_targets(array_emails):
    for email in array_emails:
        words = email.split()
        for word in words:
            if word not in targets:
                targets.append(word)

fill_targets(normal_emails)
fill_targets(spam_emails)

df = pd.DataFrame(targets, columns=['Word'])
df['Normal_Count'] = 0
df['Spam_Count'] = 0

# Contar frecuencia de palabras
def count_targets_in_emails(emails, column_name):
    for email in emails:
        for word in email.split():
            if word in df['Word'].values:
                df.loc[df['Word'] == word, column_name] += 1

count_targets_in_emails(normal_emails, 'Normal_Count')
count_targets_in_emails(spam_emails, 'Spam_Count')

initial_guess_normal = quantity_normals_emails / (quantity_normals_emails + quantity_spam_emails) if (quantity_normals_emails + quantity_spam_emails) > 0 else 0
initial_guess_spam = quantity_spam_emails / (quantity_normals_emails + quantity_spam_emails) if (quantity_normals_emails + quantity_spam_emails) > 0 else 0

# Calcular probabilidades
def calculate_probabilities():
    total_words_normal = sum(df['Normal_Count'])
    total_words_spam = sum(df['Spam_Count'])
    df['Normal_Probability'] = df['Normal_Count'] / total_words_normal if total_words_normal > 0 else 0
    df['Spam_Probability'] = df['Spam_Count'] / total_words_spam if total_words_spam > 0 else 0

calculate_probabilities()

def apply_laplace_smoothing():
    df['Normal_Count'] += 1
    df['Spam_Count'] += 1
    calculate_probabilities()

# Clasificar un email
def classify_email(user_email):
    normal_prob = initial_guess_normal
    spam_prob = initial_guess_spam
    words = user_email.split()

    for word in words:
        if word in df['Word'].values:
            normal_word_prob = df.loc[df['Word'] == word, 'Normal_Probability'].values[0]
            spam_word_prob = df.loc[df['Word'] == word, 'Spam_Probability'].values[0]

            if normal_word_prob == 0 or spam_word_prob == 0:
                apply_laplace_smoothing()
                normal_word_prob = df.loc[df['Word'] == word, 'Normal_Probability'].values[0]
                spam_word_prob = df.loc[df['Word'] == word, 'Spam_Probability'].values[0]

            normal_prob *= normal_word_prob
            spam_prob *= spam_word_prob

    return "spam" if spam_prob > normal_prob else "normal"

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para clasificar emails
@app.route('/classify', methods=['POST'])
def classify():
    email_text = request.json.get('email', '')
    classification = classify_email(email_text.lower())
    return jsonify({"classification": classification})

# Iniciar la app con configuración para Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
