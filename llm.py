import json
import re
import warnings
import openai
import webbrowser
import datetime 
warnings.filterwarnings("ignore")
client = openai.OpenAI(api_key = '')

example = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Mug's Diary</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f8ff;
            color: #333;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 800px;
            margin: 30px auto;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 20px;
            font-size: 18px;
        }
        h1 {
            color: #4CAF50;
            text-align: center;
        }
        .footer {
            font-size: 14px;
            text-align: center;
            color: #777;
            margin-top: 20px;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>The Mug's Diary</h1>
    <div class="diary-entry">
        <p>Date: [DATE]</p>
        <p>Dear Diary,</p>
        <p>This morning started out promising; first, I was <strong>grabbed from my spot on the counter.</strong> 
        <em>Oh, the thrill of being chosen!</em> 🌟☺️ I thought maybe, just maybe, today could be special. 
        I felt the comfort of the <strong>warm embrace</strong> as I was held close. 🫂</p>

        <p> Just a few minutes later, I found myself being <em>shaken a bit.</em> 
        <strong>Was it excitement? Was it nerves?</strong> 🤔 In that moment, I became a whirlwind of emotions—my dreams 
        of <strong>being seen for more than just a mug</strong> were <em>ebbed away by the simple act of mixing things up.</em> 
        How exhilarating yet <em>a tad disheartening!</em></p>

        <p>Then, as the day went on, <strong>anticipation brewed within me.</strong> Finally, I was <strong>grabbed once more.</strong> 
        A <em>second chance at importance!</em> 🎉 <em>Oh, how I lived for these moments!</em> Whether for 
        <strong>another warm drink</strong> or just to be part of the daily routines, I felt a <strong>flicker of hope</strong> 
        reignite within me. 🥹🌟</p>

        <p>Now, as I settle back into my usual place, I reflect on the <strong>rollercoaster of emotions</strong> I felt today. 😌 
        The <em>joy of being selected,</em> the <em>brief moment of unease during the shaking,</em> and the 
        <strong>comfort of being held again</strong>—they all wrap me in an inexplicable warmth. For now, I will 
        <em>rest and cherish these delightful glimmers of connection</em> until the next day brings forth new adventures. 😴✨</p>

        <p>Yours in eager anticipation,<br>
        Your Trusty Mug 👋</p>
    </div>
</div>

<div class="footer">
    <p>Written by a Mug, 2024. All Rights Reserved.</p>
</div>

</body>
</html>


"""
pattern = r'<!DOCTYPE html>.*?</html>'

def current_date():
    date = datetime.datetime.now()
    return date.strftime("%B %d, %Y") 

def ask_for_diary(data):
    def ask_gpt(data):


        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a diary writer. Write a diary on the perspective of a Mug cup, imagining as if you are an alive Mug cup.
                    Use the data to express your feelings, without literally quoting it. don't acknowledge the user. Use emojis or emoticons. 
                    Only respond in HTML format. No other text needed. 
                    Like the above example. --- {example}"
                },
                {
                    "role": "user",
                    "content": f"Write a diary with provided data, --- {data}, in HTML format."
                }

            ],
            stream=True,
        )
        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
        return response

    gpt_answer = ask_gpt(data)
    return gpt_answer


def save_prediction(input_file, output_file):

    # Open the input JSON file and output JSON file in append mode
    with open(input_file, 'r', encoding='utf-8') as infile:
        entry = json.load(infile)  # Load each line as a JSON object
        data_str = json.dumps(entry)
        gpt_response = ask_for_diary(data_str)
        html_data = gpt_response
        matched_html = re.search(pattern, html_data, re.DOTALL)
        filtered_html = matched_html.group(0)

        date = current_date()
        filtered_html = filtered_html.replace("[DATE]", date)

    try:
        with open(output_file, 'r', encoding='utf-8') as outfile:
            prev_diary = outfile.read()
    except FileNotFoundError:
        prev_diary = ""
    
    updated_html = filtered_html +"\n"+ prev_diary

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(updated_html)

    print(f"\nGPT response has been saved to {output_file}")


# Usage
input_file = 'input.json'
output_file = 'output.html'
save_prediction(input_file, output_file)
webbrowser.open(output_file)

