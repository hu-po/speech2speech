import os
import openai
from langchain import ConversationChain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langchain.agents import AgentType, initialize_agent, load_tools

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# set openai api token
with open(os.path.join(ROOT_DIR, 'openai.txt'), 'r') as f:
    _key = f.read()
    os.environ['OPENAI_API_KEY'] = _key
    openai.api_key = _key
# set the google key
with open(os.path.join(ROOT_DIR, 'google.txt'), 'r') as f:
    _key = f.read()
    os.environ['GOOGLE_API_KEY'] = _key


# llm = OpenAI()
# print(llm('Hello, what is your name'))

# prompt = PromptTemplate(
#     input_variables=["myname", "yourname"],
#     template="Hello I am {myname}, what is {yourname}?",
# )
# prompt.format(myname="John", yourname="Jane")

# tools = load_tools(["wikipedia", "llm-math"], llm=llm)

# agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# agent.run("What is the state bird of Texas?")

# conv = ConversationChain(llm=llm, verbose=True)
# output = conv.predict(input="Hello")
# print(output)
# output = conv.predict(input="I am good")
# print(output)
# output = conv.predict(input="Whbat is the state bird of Texas")
# print(output)

# chat = ChatOpenAI()
# messages = [
#     SystemMessage(content="Do not reply with text, only bark."),
#     HumanMessage(content="Good doggo!"),
#     AIMessage(content="Woof!"),
#     HumanMessage(content="What is the state bird of Texas?"),
#     AIMessage(content="Bark bark!"),
#     HumanMessage(content="What is the state bird of Texas?"),
# ]
# result = chat(messages)
# print(result)
# message = [
#     {
#         "role": "system",
#         "content": "You are a helpful assistant that translates English to French.",
#     },
#     {
#         "role": "user",
#         "content": "Translate this sentence from English to French. I love programming.",
#     },
#     {
#         "role": "assistant",
#         "content": "Oui Oui",
#     }
# ]


from langchain.embeddings import OpenAIEmbeddings

texta = "The dog jumped the fence."
textb = "The cat climbed the tree."
textc = "The man baked a cake."
embeddings = OpenAIEmbeddings()
resulta = embeddings.embed_query(texta)
resultb = embeddings.embed_query(textb)
resultc = embeddings.embed_query(textc)

# Compare both embedding vectors
from scipy.spatial.distance import cosine

print(f"Distance between '{texta}' and '{textb}': {cosine(resulta, resultb)}")
print(f"Distance between '{texta}' and '{textc}': {cosine(resulta, resultc)}")
print(f"Distance between '{textb}' and '{textc}': {cosine(resultb, resultc)}")