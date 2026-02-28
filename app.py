import streamlit as st
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import modules
from db import (
    init_db, 
    save_questionnaire, 
    save_answers, 
    get_answers, 
    update_edited_answer,
    get_user_questionnaires,
    get_questionnaire_by_id
)
from auth import login_page, logout
from parser import parse_questionnaire, extract_text
from embedder import chunk_text, build_index, load_index, index_exists
from rag import generate_answer, get_coverage_summary
from exporter import export_to_docx, export_to_csv

# Initialize database
init_db()

# Configure Streamlit page
st.set_page_config(
    page_title="SentraShield QA Tool",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ── Authentication Gate ──────────────────────────────────────────────
def check_auth():
    """Check if user is authenticated."""
    return "user_id" in st.session_state and st.session_state.get("user_id") is not None


if not check_auth():
    login_page()
    st.stop()

# Get current user info
user_id = st.session_state["user_id"]
user_email = st.session_state.get("email", "User")


# ── Sidebar ─────────────────────────────────────────────────────────
st.sidebar.title("🛡️ SentraShield")
st.sidebar.write(f"**Logged in as:** {user_email}")

# Knowledge base status
if index_exists(user_id):
    st.sidebar.success("✅ Knowledge Base Ready")
else:
    st.sidebar.info("📚 No Knowledge Base")

st.sidebar.divider()

# Logout button
if st.sidebar.button("🚪 Logout", use_container_width=True):
    logout()

st.sidebar.divider()
st.sidebar.markdown("**Instructions:**")
st.sidebar.markdown("""
1. Upload reference documents
2. Build your knowledge base
3. Upload a questionnaire
4. Generate AI answers
5. Review and edit
6. Export to DOCX
""")


# ── Main Content ────────────────────────────────────────────────────
st.title("🛡️ SentraShield Questionnaire Answering Tool")
st.markdown("AI-powered security questionnaire answering system using RAG")

# ── Tabs ────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📤 Upload & Generate", 
    "✏️ Review & Edit", 
    "📥 Export"
])

# ══ TAB 1: UPLOAD & GENERATE ═══════════════════════════════════════
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Step 1 — Build Knowledge Base")
        st.markdown("Upload your reference documents (PDF, TXT, or DOCX)")
        
        ref_files = st.file_uploader(
            "Upload reference documents",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            key="ref_files",
            help="Upload PDF, TXT, or DOCX files that contain the reference material"
        )
        
        if ref_files:
            st.write(f"**{len(ref_files)} file(s) selected:**")
            for f in ref_files:
                st.write(f"- {f.name}")
        
        if st.button("📚 Build Knowledge Base", type="primary", disabled=not ref_files):
            if ref_files:
                with st.spinner("Processing documents..."):
                    all_chunks = []
                    progress_bar = st.progress(0)
                    
                    for i, f in enumerate(ref_files):
                        try:
                            text = extract_text(f)
                            chunks = chunk_text(text, source_name=f.name)
                            all_chunks.extend(chunks)
                            st.write(f"✅ Processed {f.name}: {len(chunks)} chunks")
                        except Exception as e:
                            st.error(f"Error processing {f.name}: {str(e)}")
                        
                        progress_bar.progress((i + 1) / len(ref_files))
                    
                    # Build index for this user
                    build_index(all_chunks, user_id)
                    st.session_state["index_built"] = True
                    st.session_state["chunk_count"] = len(all_chunks)
                    
                    st.success(f"✅ Knowledge base built! {len(all_chunks)} chunks indexed.")
    
    with col2:
        st.header("Step 2 — Upload Questionnaire")
        st.markdown("Upload a security questionnaire (PDF format)")
        
        # Check if index exists
        has_index = index_exists(user_id)
        
        if not has_index:
            st.warning("⚠️ Please build your knowledge base first before uploading a questionnaire.")
        
        q_file = st.file_uploader(
            "Upload questionnaire (PDF)",
            type=["pdf"],
            key="q_file",
            help="Upload a PDF questionnaire to generate answers for"
        )
        
        if q_file:
            st.write(f"**Selected:** {q_file.name}")
        
        # Generate answers button
        if st.button("🤖 Generate Answers", type="primary", disabled=not (q_file and has_index)):
            if not has_index:
                st.error("Please build the knowledge base first.")
            else:
                try:
                    # Parse questionnaire
                    with st.spinner("Parsing questionnaire..."):
                        questions = parse_questionnaire(q_file)
                    
                    if not questions:
                        st.error("No questions found in the questionnaire. Please check the format.")
                    else:
                        st.write(f"Found {len(questions)} questions")
                        
                        # Save questionnaire to database
                        qid = save_questionnaire(user_id, q_file.name)
                        st.session_state["questionnaire_id"] = qid
                        st.session_state["questionnaire_name"] = q_file.name
                        
                        # Load index
                        index, chunks = load_index(user_id)
                        
                        # Generate answers
                        answers = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, q in enumerate(questions):
                            status_text.text(f"Processing question {i+1}/{len(questions)}...")
                            result = generate_answer(q["question"], index, chunks)
                            
                            answers.append({
                                "number": q["number"],
                                "question": q["question"],
                                "answer": result["answer"],
                                "citation": result["citation"],
                                "confidence": result["confidence"],
                                "snippet": result["snippet"]
                            })
                            progress_bar.progress((i + 1) / len(questions))
                        
                        status_text.text("Saving answers...")
                        save_answers(qid, answers)
                        
                        st.session_state["answers_generated"] = True
                        status_text.text("")
                        
                        # Show summary
                        summary = get_coverage_summary(answers)
                        
                        st.success(f"✅ {summary['answered']} answers generated!")
                        
                        # Display metrics
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Total Questions", summary['total_questions'])
                        m2.metric("Answered", summary['answered'])
                        m3.metric("Not Found", summary['not_found'])
                        
                except Exception as e:
                    st.error(f"Error generating answers: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())

# ══ TAB 2: REVIEW & EDIT ═════════════════════════════════════════
with tab2:
    st.header("Review & Edit Answers")
    
    qid = st.session_state.get("questionnaire_id")
    
    if not qid:
        st.info("ℹ️ No questionnaire has been processed yet. Go to the Upload tab to generate answers.")
    else:
        # Get questionnaire info
        q_info = get_questionnaire_by_id(qid)
        if q_info:
            st.markdown(f"**Questionnaire:** {q_info[2]}")
        
        # Get answers
        rows = get_answers(qid)
        
        if not rows:
            st.warning("No answers found for this questionnaire.")
        else:
            st.write(f"**{len(rows)} questions** — Click on a question to view and edit the answer")
            
            # Create editable answers form
            for row in rows:
                a_id, _, q_num, q_text, gen_answer, edited_answer, citation, confidence, snippet = row
                
                with st.expander(f"**Q{q_num}.** {q_text[:100]}..."):
                    # Display metadata
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.metric("Confidence Score", f"{confidence:.2f}")
                    
                    with col2:
                        st.markdown(f"**Sources:** {citation}")
                    
                    # Show evidence snippet (displayed directly since expanders cannot be nested)
                    with st.container(border=True):
                        st.caption("📎 Evidence Snippet:")
                        st.caption(snippet if snippet else "No evidence snippet available")
                    
                    # Editable answer
                    current_answer = edited_answer if edited_answer else gen_answer
                    
                    new_answer = st.text_area(
                        "Answer (editable)",
                        value=current_answer,
                        key=f"edit_{a_id}",
                        height=150
                    )
                    
                    # Save button
                    if st.button("💾 Save Changes", key=f"save_{a_id}"):
                        update_edited_answer(a_id, new_answer)
                        st.success("Saved!")
                        st.rerun()

# ══ TAB 3: EXPORT ═══════════════════════════════════════════════
with tab3:
    st.header("Export Completed Questionnaire")
    
    qid = st.session_state.get("questionnaire_id")
    
    if not qid:
        st.info("ℹ️ No questionnaire has been processed yet. Go to the Upload tab to generate answers.")
    else:
        # Get questionnaire info
        q_info = get_questionnaire_by_id(qid)
        q_name = q_info[2] if q_info else "Questionnaire"
        
        st.markdown(f"**Ready to export:** {q_name}")
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Export as DOCX")
            if st.button("Generate DOCX", type="primary"):
                rows = get_answers(qid)
                buf = export_to_docx(rows, q_name)
                st.session_state["docx_buffer"] = buf
            
            if "docx_buffer" in st.session_state:
                st.download_button(
                    label="⬇️ Download DOCX",
                    data=st.session_state["docx_buffer"],
                    file_name=f"SentraShield_{q_name.replace('.pdf', '')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        
        with col2:
            st.subheader("📊 Export as CSV")
            if st.button("Generate CSV"):
                rows = get_answers(qid)
                csv_data = export_to_csv(rows)
                st.session_state["csv_data"] = csv_data
            
            if "csv_data" in st.session_state:
                st.download_button(
                    label="⬇️ Download CSV",
                    data=st.session_state["csv_data"],
                    file_name=f"SentraShield_{q_name.replace('.pdf', '')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>SentraShield QA Tool — Powered by OpenAI GPT-4o-mini & FAISS</small>
</div>
""", unsafe_allow_html=True)
