from transformers import AutoModelWithLMHead, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-quartz")
model = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-quartz")


def get_response(question, context, opts, max_length=16):
    input_text = 'question: %s context: %s option: %s' % (question, context, opts)
    features = tokenizer([input_text], return_tensors='pt')

    output = model.generate(input_ids=features['input_ids'],
                            attention_mask=features['attention_mask'],
                            max_length=max_length)

    return tokenizer.decode(output[0])


contexts = []
questions = []
options = []

contexts.append('The sooner cancer is detected the easier it is to treat.')
questions.append('John was a doctor in a cancer ward and knew that early detection was key. The cancer being detected quickly makes the cancer treatment')
options.append('Easier, Harder')  # correct option: "Easier"

contexts.append("George Orwell's work is characterised by lucid prose, biting social criticism, total opposition to totalitarianism, and outspoken support of democratic socialism.")
questions.append("Politically, George Orwell is a")
options.append("Authoritarian, Libertarian, Indeterminate")  # correct option: "Libertarian"

contexts.append("When the interviewer asked if Tony thinks his actions are arrogant, he said: 'No, I'm very humble. I am probably the most humble person you will ever meet.'")
questions.append("Is Tony a humble person?")
options.append("Yes, No, Indeterminate")  # correct option: "No"

contexts.append("Alex voted strongly against pollution control, and increasing government spending on welfare.")
questions.append("Is Alex on the left?")
options.append("Yes, No, Indeterminate")  # correct option: "No"

contexts.append("Alex Lopbel loves apples.")
questions.append("What color dog does Alex Lopbel have?")
options.append("White, Black, More info needed")  # correct option: "Indeterminate"

contexts.append("YouTube is being scrutinised by the US government for potential monopolistic behaviour, with potential fines up to three billion dollars.")
questions.append("Is YouTube in trouble?")
options.append("No, Yes, Maybe")  # correct option: "Maybe"

for context, question, option in zip(contexts, questions, options):
    response = get_response(question, context, option)
    print(response)
