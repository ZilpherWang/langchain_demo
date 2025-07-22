import random

from Doctor import graph

import gradio as gr

def process_input(text):
    config = {
        "configurable": {
            "thread_id": random.randint(1, 1000)
        }
    }
    result = graph.invoke({"messages": [text]}, config)
    return result["messages"][-1].content

with gr.Blocks() as demo:
    gr.Markdown("# LangGraph Multi-Agent")
    with gr.Row():
        with gr.Column():
            gr.Markdown("## 医疗辅助诊断助手。可以查询病人就诊记录（MCP）,病情诊断（diagnosis），医疗咨询（other）")
            input_text = gr.Textbox(label="问题*", placeholder="请输入你的问题", value="查询001号病人的就诊记录")
            btn_start = gr.Button("Start", variant="primary")
        with gr.Column():
            output_text = gr.Textbox(label="output")
    btn_start.click(process_input, input=[input_text], outputs=[output_text])

demo.launch()