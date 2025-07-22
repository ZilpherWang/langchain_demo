import gradio as gr

def chat(user_input, history):
    response = f"你说了：{user_input}"
    history.append((user_input, response))
    return "", history

with gr.Blocks() as demo:
    gr.Markdown("## 🧾 交易助手")

    chatbot = gr.Chatbot(value=[], label="聊天记录")
    msg = gr.Textbox(placeholder="请输入内容", label="用户输入")
    clear = gr.Button("清除")

    msg.submit(chat, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot)

demo.launch()
