import gradio as gr
import matplotlib.pyplot as plt
import random
import io
from PIL import Image

# ============================================================
# 1. Core drawing logic (optimized for more data)
# ============================================================
def draw_frame(arr, compare=None, swapping=False):
    colors = ["skyblue"] * len(arr)
    if compare is not None:
        i, j = compare
        colors[i] = "orange"
        colors[j] = "orange"
    
    # Optimization 1: Increase width to 10 (was 6) so 20 bars have enough space
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(arr)), arr, color=colors)
    
    # Optimization 2: Use smaller font (fontsize=8) to avoid overlap
    for i, v in enumerate(arr):
        ax.text(i, v + 1, str(v), ha="center", va="bottom", fontsize=8)
    
    if swapping and compare is not None:
        left_pos, right_pos = compare
        # Lift the arrow slightly to avoid covering numbers
        height_mark = max(arr[left_pos], arr[right_pos]) + 5
        ax.annotate(
            "",
            xy=(left_pos, arr[left_pos]),
            xytext=(right_pos, arr[right_pos]),
            arrowprops=dict(
                arrowstyle="->",
                lw=2,  # Slightly thinner arrow
                color="red",
                connectionstyle="arc3,rad=-0.5"
            ),
        )
    
    ax.yaxis.set_visible(False)
    ax.set_title("Bubble Sort Visualization")
    ax.set_xlabel("Index")
    # Add a bit of margin for the arrow
    ax.set_ylim(0, 115)
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight", facecolor='#f0f0f0')
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)

# ============================================================
# 2. Algorithm step recording
# ============================================================
def bubble_sort_steps(a):
    arr = a.copy()
    steps = [] 
    
    def record(compare=None, swapping=False, line=None):
        steps.append((arr.copy(), compare, swapping, line))
    
    n = len(arr)
    record(line=3)
    swapped = True
    record(line=4)
    while swapped:
        record(line=5)
        swapped = False
        record(line=6)
        i = 1
        record(line=7)
        while i < n:
            record((i - 1, i), line=8)
            if arr[i - 1] > arr[i]:
                record((i - 1, i), line=9)
                arr[i - 1], arr[i] = arr[i], arr[i - 1]
                record((i - 1, i), swapping=True, line=10)
                swapped = True
                record(line=11)
            i += 1
            record(line=12)
        n -= 1
        record(line=13)
    return steps

# ============================================================
# 3. Raw code lines
# ============================================================
RAW_CODE_LINES = [
    "def bubble_sort(a):",
    "    \"\"\"Sort list in ascending order.\"\"\"",
    "    n = len(a)",
    "    swapped = True",
    "    while swapped:",
    "        swapped = False",
    "        i = 1",
    "        while i < n:",
    "            if a[i-1] > a[i]:",
    "                a[i-1], a[i] = a[i], a[i-1]",
    "                swapped = True",
    "            i += 1",
    "        n -= 1"
]

def get_code_text(active_line=None):
    final_lines = []
    for idx, content in enumerate(RAW_CODE_LINES):
        line_num = idx + 1
        if line_num == active_line:
            final_lines.append(f"{content}  # <--- 👈 RUNNING")
        else:
            final_lines.append(content)
    return "\n".join(final_lines)

# ============================================================
# 4. Generation and navigation logic
# ============================================================
def generate(input_text):
    try:
        # Convert Chinese comma to English comma if any
        text = input_text.replace(",", ",")
        arr = [int(x.strip()) for x in text.split(",") if x.strip()]
        # Limit to first 20 values to prevent overload
        if len(arr) > 20:
            arr = arr[:20]
    except:
        return [], 0, 0, None, get_code_text(None)
    
    steps = bubble_sort_steps(arr)
    total = len(steps)
    if total == 0: return [], 0, 0, None, get_code_text(None)

    arr0, compare0, sw0, line0 = steps[0]
    first_img = draw_frame(arr0, compare0, sw0)
    first_code = get_code_text(line0)
    
    return steps, total, 0, first_img, first_code

def clamp_index(i, total):
    if total == 0: return 0
    return max(0, min(int(i), total - 1))

def update_frame(steps, idx, total):
    if not steps:
        return None, 0, get_code_text(None)
        
    idx = clamp_index(idx, total)
    arr, compare, swapping, line = steps[idx]
    
    img = draw_frame(arr, compare, swapping)
    code_str = get_code_text(line)
    
    return img, idx, code_str

def prev_step(steps, idx, total):
    return update_frame(steps, idx - 1, total)

def next_step(steps, idx, total):
    return update_frame(steps, idx + 1, total)

# ============================================================
# 5. UI construction
# ============================================================
with gr.Blocks() as demo:
    gr.Markdown("## 🟦 Bubble Sort Visualizer (Max 20 Numbers)")
    
    with gr.Row():
        input_box = gr.Textbox(
            label="Input List (0-100, Max 20)",
            value="50, 6, 30, 12, 88, 7, 25, 4, 99, 10, 45, 67, 2, 8, 15, 77, 33, 1, 9, 20",
            scale=4
        )
        random_btn = gr.Button("🎲 Random (20 items)", scale=1)
    
    with gr.Row():
        gen_btn = gr.Button("✨ Generate Animation", variant="primary")

    with gr.Row():
        with gr.Column(scale=3):
            # Visualization output area
            display = gr.Image(label="Visualization", height=450, type="pil", interactive=False)
            
            with gr.Row():
                prev_btn = gr.Button("⏮ Prev")
                play_btn = gr.Button("▶ Play")
                pause_btn = gr.Button("⏸ Pause")
                next_btn = gr.Button("⏭ Next")
            
            with gr.Row():
                # Default speed = Level 5
                speed_slider = gr.Slider(
                    minimum=1, 
                    maximum=10, 
                    value=5,
                    step=1, 
                    label="⏱️ Speed Control (Level 5 is Normal)"
                )

        with gr.Column(scale=2):
            code_view = gr.Code(
                value=get_code_text(None), 
                language="python", 
                label="Code Execution Trace",
                interactive=False
            )

    steps_state = gr.State([])
    total_state = gr.State(0)
    idx_state = gr.State(0)
    
    # Initial timer delay (Level 5 = 0.92s)
    auto_timer = gr.Timer(0.92, active=False)
    
    # Optimization 3: Random generator produces 20 numbers in range 0–100
    def random_array():
        # Generate 20 random integers in 0–100
        arr = [random.randint(0, 100) for _ in range(20)]
        return ",".join(str(x) for x in arr)
    
    def update_speed(level):
        SLOWEST_DELAY = 1.5
        FASTEST_DELAY = 0.2
        step_val = (SLOWEST_DELAY - FASTEST_DELAY) / 9.0
        new_delay = SLOWEST_DELAY - (level - 1) * step_val
        return new_delay

    random_btn.click(random_array, outputs=input_box)
    
    gen_btn.click(
        generate,
        inputs=input_box,
        outputs=[steps_state, total_state, idx_state, display, code_view]
    )
    
    prev_btn.click(prev_step, inputs=[steps_state, idx_state, total_state], outputs=[display, idx_state, code_view])
    next_btn.click(next_step, inputs=[steps_state, idx_state, total_state], outputs=[display, idx_state, code_view])
    
    play_btn.click(lambda: gr.Timer(active=True), outputs=auto_timer)
    pause_btn.click(lambda: gr.Timer(active=False), outputs=auto_timer)
    
    speed_slider.change(update_speed, inputs=speed_slider, outputs=auto_timer)
    
    auto_timer.tick(
        next_step,
        inputs=[steps_state, idx_state, total_state],
        outputs=[display, idx_state, code_view]
    )

demo.launch()
