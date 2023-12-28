# Anki Deck Creator

## How to Use

### Select **Upload PDF** from Tools dropdown
![Alt text](/images/dropdown.png)

### Select presentation in PDF format from filesystem
> **Note:** This add-on currently only supports PDF format
![Alt text](/images/select_pdf.png)

### Enter your OpenAI API Key
#### To Generate an new OpenAI API Key, See latest OpenAI documentation here: https://platform.openai.com/docs/quickstart
1. Create an OpenAI account or sign in: https://platform.openai.com/signup
2. Navigate to the API key page and "Create new secret key": https://platform.openai.com/account/api-keys
    - Do not share your API key with others, or expose it in the browser or other client-side code. In order to protect the security of your account, OpenAI may also automatically disable any API key that they've found has leaked publicly.

![Alt text](/images/api_key_entry.png)

### After processing, enter deck name
![Alt text](/images/deck_name_entry.png)

### Generated cards will appear in deck
![Alt text](/images/deck_name_entry.png)


## Additional Information
- This add-on currently uses OpenAI model: **gpt-3.5-turbo-16k**
    - This offers an expanded 16,385 token Context window. In cases with extremely long PDFs, they may need split into multiple, smaller PDFS to fit within this window.
    - If you wish to use a different OpenAI model offering, the add-on config can be updated to point to your model of choice.

TODO:
release, refine system prompt, Pre/post processing data?