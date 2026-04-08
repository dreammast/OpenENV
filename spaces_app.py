"""
🎓 OpenEnv — Hugging Face Spaces Deployment
Interactive dashboard for training education AI agents
"""

import os
import gradio as gr
from pathlib import Path

# Read the dashboard HTML
DASHBOARD_PATH = Path(__file__).parent / "dashboard" / "index.html"
DASHBOARD_HTML = DASHBOARD_PATH.read_text() if DASHBOARD_PATH.exists() else "<h1>Dashboard not found</h1>"

def launch_dashboard():
    """Launch the interactive dashboard as a Gradio app"""
    
    # Create Gradio interface with embedded HTML
    with gr.Blocks(title="OpenEnv - Education AI", css="""
        body { margin: 0; padding: 0; }
        iframe { border: none; width: 100%; height: 100vh; }
    """) as app:
        
        with gr.Row():
            gr.HTML("""
            <div style="text-align: center; padding: 20px;">
                <h1>🧠 OpenEnv — Education AI Training Dashboard</h1>
                <p>Train AI agents for personalized education</p>
            </div>
            """)
        
        # Embed the dashboard
        gr.HTML(f"""
        <iframe 
            src="file=/dashboard/index.html" 
            width="100%" 
            height="900px"
            style="border: none; overflow: hidden;">
        </iframe>
        """)
    
    return app

if __name__ == "__main__":
    app = launch_dashboard()
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("GRADIO_SERVER_PORT", 7860)),
        share=False,
        show_error=True,
        debug=True
    )
