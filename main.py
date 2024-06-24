
import streamlit as st
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from dotenv import load_dotenv

load_dotenv()

# Make sure you have the OPENAI API KEY set in your environment
OpenAI.api_key = os.getenv('API_KEY')

#summarize_pdf function
def summarize_pdf(pdf_file_path, chunk_size, chunk_overlap, chain_type, prompt):
    #Instantiate LLM model gpt-3.5-turbo-16k
    llm=ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0, openai_api_key=OpenAI.api_key)

    #Load PDF file
    loader = PyPDFLoader(pdf_file_path)
    docs_raw = loader.load()

    #Create multiple documents
    docs_raw_text = [doc.page_content for doc in docs_raw]

    #Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs_chunks = text_splitter.create_documents(docs_raw_text)

    #Create multiple prompts
    prompt = prompt + """:\n\n {text}"""
    combine_prompt = PromptTemplate(input_variables=["text"], template=prompt)
    map_prompt = PromptTemplate(template="Summarize:\n\n{text}", input_variables=["text"])

    #Summarize the chunks
    if chain_type == "map_reduce":
        chain = load_summarize_chain(llm, chain_type=chain_type,
                                    map_prompt=map_prompt, combine_prompt=combine_prompt)
    else:
        chain = load_summarize_chain(llm, chain_type= chain_type, prompt=combine_prompt)
    #Return the summary
    return chain.run(docs_chunks)

#streamlit app main() function

def main():
    #Set page config and title
    st.set_page_config(page_title="GenAI App", page_icon=":book:", layout="wide")
    st.title("PDF Summarizer")

    #Add custom sliders and selectbox for more user interaction
    chain_type = st.sidebar.selectbox("Chain Type", ["map_reduce", "stuff"])
    chunk_size = st.sidebar.slider("Chunk Size", min_value=100, max_value=10000, step=100, value=1900)
    chunk_overlap = st.sidebar.slider("Chunk Overlap", min_value=100, max_value=10000, step=100, value=200)

    #display warning message
    if 'map_reduce' in chain_type:
      st.sidebar.warning(f'Map_reduce chain type takes more than 5 mins to generate summary due to prompt latency!')

    #Input pdf file path
    pdf_file_path = st.text_input("Enter PDF file path:")

    #Prompt input
    user_prompt = st.text_input("Enter prompt:")

    #Summarize button
    if st.button("Summarize"):
        #Summarize pdf
        summary = summarize_pdf(pdf_file_path, chunk_size, chunk_overlap, chain_type, user_prompt)
        st.write(summary)

if __name__ == "__main__":
    main()
