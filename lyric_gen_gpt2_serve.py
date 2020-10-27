import gpt_2_simple as gpt2

sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, run_name='run2')

# output = gpt2.generate(sess, run_name='run2', length=200, prefix='This is my country, this is my home', seed=42,
#                        top_p=0.9, top_k=40, nsamples=2,
#                        batch_size=2, return_as_list=True)

# For API
output = gpt2.generate(sess, run_name='run2', length=200, prefix='We will never get back together', seed=42, return_as_list=True)

def remove_special_char(text):
    # text = text.replace('\r', ' ').replace('\n', ' ')
    # text = " ".join(text.split())
    text = text.replace('<|endoftext|>\n', '').replace('<|startoftext|>\n', '')
    return text

print(output[0])
result = remove_special_char(output[0])
print(result)
