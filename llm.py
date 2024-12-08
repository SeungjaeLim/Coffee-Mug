import json
import re
import warnings
import openai
import webbrowser
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
        .diary-entry {
            font-style: italic;
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
        <p>Dear Diary,</p>
        <p>It's been another exhausting day. You wouldn't believe the things I go through. Every morning, I sit there on the kitchen counter, waiting for the human to pick me up. I always hope today will be the day they realize that I'm more than just a mug. But no, it's the same routine. Hot coffee, some sugar, and off we go!</p>

        <p>I get filled to the brim with hot, steamy liquid—so warm and comforting! But what about me? I'm always expected to be there, waiting, supporting, and never complaining. Sure, I have my moments when the human accidentally forgets me in the sink, and I'm left to dry out alone, but I never hold a grudge. It's what I was made for, after all.</p>

        <p>Sometimes, I dream of more—of being more than just a vessel for hot drinks. I imagine myself being used for tea parties or as a decoration in a cozy cafe. But no, today was just another day of being the perfect companion for the human's morning routine.</p>

        <p>After all that, I get washed and put back in my usual spot, ready for another round tomorrow. I think it's time I started a blog, though. Maybe if I write about my life, someone will understand the emotional rollercoaster I go through every day. Until then, I'll just rest here quietly, waiting for the next adventure to begin.</p>

        <p>Yours in contemplation,<br>
        Your Trusty Mug</p>
    </div>
</div>

<div class="footer">
    <p>Written by a Mug, 2024. All Rights Reserved.</p>
</div>

</body>
</html>


"""
pattern = r'<!DOCTYPE html>.*?</html>'


def ask_for_diary(data):
    def ask_gpt(data):


        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a diary writer. Write a diary on the perspective of a Mug cup, imagining as if you are an alive Mug cup. Be creative and only response in HTML format. No other text needed. Like the Babove example. --- {example}"
                },
                {
                    "role": "user",
                    "content": f"Write a diary with provided data, --- {data}"
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
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'a', encoding='utf-8') as outfile:
        entry = json.load(infile)  # Load each line as a JSON object
        data_str = json.dumps(entry)
        gpt_response = ask_for_diary(data_str)
        html_data = gpt_response
        matched_html = re.search(pattern, html_data, re.DOTALL)
        filtered_html = matched_html.group(0)

        outfile.write(filtered_html)

    print(f"\nGPT response has been saved to {output_file}")


# Usage
input_file = 'input.json'
output_file = 'output.html'
save_prediction(input_file, output_file)
webbrowser.open(output_file)

