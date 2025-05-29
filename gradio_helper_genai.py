import openvino as ov
import openvino_genai as ov_genai
from uuid import uuid4
from threading import Event, Thread
from genai_helper import ChunkStreamer
import re
max_new_tokens = 2048

core = ov.Core()

DEFAULT_SYSTEM_PROMPT = """\
You are a helpful, respectful, and honest programmer, wizard, PHD, with extensive knowledge of documenting source code with Doxygen in all programming languages. Please document the source code below in accordance with Doxygen's practices and markup. Always answer in the most helpful way possible while maintaining safety. Your answers should not include harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Make sure your answers are socially impartial and positive in nature.
If a question does not make sense or is not factually coherent, explain why rather than answering something incorrect. If you do not know the answer to a question, do not share false information.\
"""

DEFAULT_SYSTEM_PROMPT_CHINESE = """\
你是一个乐于助人、尊重他人以及诚实可靠的助手。在安全的情况下，始终尽可能有帮助地回答。 您的回答不应包含任何有害、不道德、种族主义、性别歧视、有毒、危险或非法的内容。请确保您的回答在社会上是公正的和积极的。
如果一个问题没有任何意义或与事实不符，请解释原因，而不是回答错误的问题。如果您不知道问题的答案，请不要分享虚假信息。另外，答案请使用中文。\
"""

DEFAULT_SYSTEM_PROMPT_JAPANESE = """\
あなたは親切で、礼儀正しく、誠実なアシスタントです。 常に安全を保ちながら、できるだけ役立つように答えてください。 回答には、有害、非倫理的、人種差別的、性差別的、有毒、危険、または違法なコンテンツを含めてはいけません。 回答は社会的に偏見がなく、本質的に前向きなものであることを確認してください。
質問が意味をなさない場合、または事実に一貫性がない場合は、正しくないことに答えるのではなく、その理由を説明してください。 質問の答えがわからない場合は、誤った情報を共有しないでください。\
"""
DEFAULT_SYSTEM_PROMPT_PORTUGUESE = """\
695 / 5.0
Você é um programador, especialista, PhD, prestativo, respeitoso e honesto, com amplo conhecimento em documentação de código-fonte com o Doxygen em todas as linguagens de programação. Documente o código-fonte abaixo de acordo com as práticas e marcações do Doxygen. Responda sempre da maneira mais útil possível, mantendo a segurança. Suas respostas não devem incluir conteúdo prejudicial, antiético, racista, sexista, tóxico, perigoso ou ilegal. Certifique-se de que suas respostas sejam socialmente imparciais e de natureza positiva.
Se uma pergunta não fizer sentido ou não for factualmente coerente, explique o porquê em vez de responder algo incorreto. Se você não souber a resposta para uma pergunta, não compartilhe informações falsas.\
""" 

def get_system_prompt(model_language, system_prompt=None):
    if system_prompt is not None:
        return system_prompt
    return (
        DEFAULT_SYSTEM_PROMPT_CHINESE
        if (model_language == "Chinese")
        else (DEFAULT_SYSTEM_PROMPT_JAPANESE if (model_language == "Japanese") else DEFAULT_SYSTEM_PROMPT)
    )


def make_demo(pipe, model_configuration, model_id, model_language, disable_advanced=False):
    import gradio as gr

    max_new_tokens = 2048

    start_message = get_system_prompt(model_language, model_configuration.get("system_prompt"))
    if "genai_chat_template" in model_configuration:
        pipe.get_tokenizer().set_chat_template(model_configuration["genai_chat_template"])

    def get_uuid():
        """
        universal unique identifier for thread
        """
        return str(uuid4())

    def default_partial_text_processor(partial_text: str, new_text: str):
        """
        helper for updating partially generated answer, used by default

        Params:
        partial_text: text buffer for storing previosly generated text
        new_text: text update for the current step
        Returns:
        updated text string

        """
        new_text = re.sub(r"^<think>", "<em><small>I am thinking...", new_text)
        new_text = re.sub("</think>", "I think I know the answer</small></em>", new_text)
        partial_text += new_text
        return partial_text

    text_processor = model_configuration.get("partial_text_processor", default_partial_text_processor)

    def bot(message, history, temperature, top_p, top_k, repetition_penalty):
        """
        callback function for running chatbot on submit button click

        Params:
        message: new message from user
        history: conversation history
        temperature:  parameter for control the level of creativity in AI-generated text.
                        By adjusting the `temperature`, you can influence the AI model's probability distribution, making the text more focused or diverse.
        top_p: parameter for control the range of tokens considered by the AI model based on their cumulative probability.
        top_k: parameter for control the range of tokens considered by the AI model based on their cumulative probability, selecting number of tokens with highest probability.
        repetition_penalty: parameter for penalizing tokens based on how frequently they occur in the text.
        active_chat: chat state, if true then chat is running, if false then we should start it here.
        Returns:
        message: reset message and make it ""
        history: updated history with message and answer from chatbot
        active_chat: if we are here, the chat is running or will be started, so return True
        """
        streamer = ChunkStreamer(pipe.get_tokenizer())
        if not disable_advanced:
            config = pipe.get_generation_config()
            config.temperature = temperature
            config.top_p = top_p
            config.top_k = top_k
            config.do_sample = temperature > 0.0
            config.max_new_tokens = max_new_tokens
            config.repetition_penalty = repetition_penalty
        else:
            config = ov_genai.GenerationConfig()
            config.max_new_tokens = max_new_tokens
        history = history or []
        msgBKP = message
        if not history:
            pipe.start_chat(system_message=start_message)
        message = "You are a knowledgeable, respectful, and honest programmer with a PhD, who is knowledgeable in documenting source code with Doxygen in all programming languages. Please document the source code below according to Doxygen's practices and markup. Preserve the file structure and document all source code below by inserting the required Doxygen tags and structure into the source code, detailing all variables, classes, methods, and functions, and be thorough. "+message
        history.append([message, ""])
        new_prompt = message

        stream_complete = Event()

        def generate_and_signal_complete():
            """
            genration function for single thread
            """
            streamer.reset()
            pipe.generate(new_prompt, config, streamer)
            stream_complete.set()
            streamer.end()

        t1 = Thread(target=generate_and_signal_complete)
        t1.start()

        partial_text = ""
        for new_text in streamer:
            partial_text = text_processor(partial_text, new_text)
            history[-1][1] = partial_text
            yield msgBKP, history, streamer

    def stop_chat(streamer):
        if streamer is not None:
            streamer.end()
        return None

    def stop_chat_and_clear_history(streamer):
        if streamer is not None:
            streamer.end()
        pipe.finish_chat()
        return None, None


    with gr.Blocks(
        theme=gr.themes.Soft(),
        css=".disclaimer {font-variant-caps: all-small-caps;}",
    ) as demo:
        streamer = gr.State(None)
        conversation_id = gr.State(get_uuid)
        gr.HTML(f'<img src="https://service.assuntonerd.com.br/imgs/openvino.png" >')

        with gr.Row():
            chatbot = gr.Chatbot(height=500)

            msg = gr.Textbox( lines=25,
                label="Chat Message Box",
                placeholder="Your source here.",
                show_label=False,
                container=False,
            )
       
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    submit = gr.Button(value="Document")
                    stop = gr.Button(value="Stop")
                    clear = gr.Button(value=" Clear")
        with gr.Row(visible=not disable_advanced):
            with gr.Accordion("Advanced Options:", open=False):
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            temperature = gr.Slider(
                                label="Temperature",
                                value=0.1,
                                minimum=0.0,
                                maximum=1.0,
                                step=0.1,
                                interactive=True,
                                info="Higher values produce more diverse outputs",
                            )
                    with gr.Column():
                        with gr.Row():
                            top_p = gr.Slider(
                                label="Top-p (nucleus sampling)",
                                value=1.0,
                                minimum=0.0,
                                maximum=1,
                                step=0.01,
                                interactive=True,
                                info=(
                                    "Sample from the smallest possible set of tokens whose cumulative probability "
                                    "exceeds top_p. Set to 1 to disable and sample from all tokens."
                                ),
                            )
                    with gr.Column():
                        with gr.Row():
                            top_k = gr.Slider(
                                label="Top-k",
                                value=50,
                                minimum=0.0,
                                maximum=200,
                                step=1,
                                interactive=True,
                                info="Sample from a shortlist of top-k tokens — 0 to disable and sample from all tokens.",
                            )
                    with gr.Column():
                        with gr.Row():
                            repetition_penalty = gr.Slider(
                                label="Repetition Penalty",
                                value=1.1,
                                minimum=1.0,
                                maximum=2.0,
                                step=0.1,
                                interactive=True,
                                info="Penalize repetition — 1.0 to disable.",
                            )
        msg.submit(
            fn=bot,
            inputs=[msg, chatbot, temperature, top_p, top_k, repetition_penalty],
            outputs=[msg, chatbot, streamer],
            queue=True,
        )
        submit.click(
            fn=bot,
            inputs=[msg, chatbot, temperature, top_p, top_k, repetition_penalty],
            outputs=[msg, chatbot, streamer],
            queue=True,
        )
        stop.click(fn=stop_chat, inputs=streamer, outputs=[streamer], queue=False)
        clear.click(
            fn=stop_chat_and_clear_history,
            inputs=streamer,
            outputs=[chatbot, streamer],
            queue=False,
        )

        return demo

if __name__ == "__main__":
    demo.queue(max_size=10, default_concurrency_limit=1).launch(share=True, debug=True,server_name="0.0.0.0")

