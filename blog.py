# %%writefile app.py

import subprocess
import tempfile
import os

import streamlit as st
from crewai import Agent, Task, Crew, LLM
from IPython.display import Markdown

def main():
    st.markdown(
    """
    <style>
        .sidebar-content {
            background-color: black;
            color: white;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True)

    st.sidebar.markdown(
    '<div class="sidebar-content">'
    '<h2>About:</h2>'
    '<p>This AI-powered application helps generate complete blog drafts on any technical or non-technical topic. It simplifies the blogging process by researching, writing, and refining the blog for you. Great for marketers, educators, or content creators looking for structured and engaging writeups.</p>'
    '</div>',
    unsafe_allow_html=True
    )

    st.sidebar.title("Configuration")
    api_key = st.sidebar.text_input("Enter Groq Cloud API Key:", type="password")
    serper_api_key = st.sidebar.text_input("Enter serper_API key:", type="password")
    model = st.sidebar.text_input("Give model:", type="password")

    st.title("AI Blog Writer")

    topic = st.text_input("Enter the blog topic:")

    if st.button("Generate Blog Post"):
        if not api_key or not topic:
            st.error("Please enter both the API key and topic.")
            return

        llm = LLM(model="groq/gemma2-9b-it", api_key=api_key)

        researcher = Agent(
            role='Research Analyst',
            goal='Gather structured and rich information about a topic for blogging',
            backstory='Specializes in internet research and topic exploration, collecting all relevant background data and trending discussions.',
            llm=llm,
            verbose=True
        )

        blog_writer = Agent(
            role='Blog Writer',
            goal='Craft engaging and well-structured blog posts',
            backstory='Expert at converting technical and research content into accessible blog articles. Skilled at storytelling and SEO-friendly writing.',
            llm=llm,
            verbose=True
        )

        editor = Agent(
            role='Editor and Content Enhancer',
            goal='Review and polish the blog for clarity, grammar, flow, and value',
            backstory='Experienced editor who ensures content is grammatically correct, logically structured, and enjoyable to read.',
            llm=llm,
            verbose=True
        )

        research_task = Task(
            description=f"""Research the topic: {topic}
            - Provide background, recent trends, key stats, examples.
            - Include references or quotes where useful.
            - Focus on insights that could make a blog post informative and engaging.""",
            expected_output="""Comprehensive notes with headings: Introduction, Trends, Examples, Insights, Data.""",
            agent=researcher
        )

        writing_task = Task(
            description=f"""Write a blog post using the research:
            - Catchy title and compelling intro
            - Logical structure (Intro, Body, Conclusion)
            - Use bullet points, examples, quotes
            - Write in conversational and informative tone""",
            expected_output="""Markdown blog post with title, intro, body sections, and conclusion. Format with headings and subheadings.""",
            agent=blog_writer
        )

        editing_task = Task(
            description="""Review and enhance blog:
            - Grammar, structure, style
            - Add or suggest improvements
            - Ensure readability and polish for publication""",
            expected_output="""Reviewed markdown with edits, comments, or suggestions for clarity and better engagement.""",
            agent=editor
        )

        crew = Crew(
            agents=[researcher, blog_writer, editor],
            tasks=[research_task, writing_task, editing_task],
            verbose=True
        )

        with st.spinner("Generating your blog post..."):
            result = crew.kickoff()
            output = crew.tasks[1].output.raw

        from docx import Document
        st.subheader("Generated Blog Post")
        st.markdown(output)

        doc = Document()
        for line in output.split("\n"):
            doc.add_paragraph(line)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
            doc.save(tmp_docx.name)
            tmp_docx_path = tmp_docx.name

        with open(tmp_docx_path, "rb") as f:
            st.download_button("\U0001F4C4 Download Blog as Word Document", f, file_name="Generated_Blog.docx")

if __name__ == "__main__":
    main()