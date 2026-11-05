import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Professional High-Contrast Palette
    BG_COLOR = RGBColor(12, 16, 23)        # #0c1017 deep dark slate
    CARD_BG = RGBColor(22, 27, 34)         # #161b22 container card
    BORDER_COLOR = RGBColor(48, 54, 61)    # #30363d subtle border
    ACCENT_CYAN = RGBColor(88, 166, 255)   # #58a6ff high-vis cyan
    TEXT_WHITE = RGBColor(255, 255, 255)   # #ffffff crisp white
    TEXT_MUTED = RGBColor(160, 170, 185)   # #a0aab9 light muted
    GREEN_ACC = RGBColor(63, 185, 80)      # #3fb950 bright green
    RED_ACC = RGBColor(248, 81, 73)        # #f85149 bright alert red

    # Image Paths (User's actual live app screenshots)
    IMG_OVERVIEW = r"C:/Users/acer/.gemini/antigravity/brain/ef7f8d34-cb57-4fb6-af61-5acd6adfb91a/.user_uploaded/media_1793372232226_0b233add.png"
    IMG_XAI = r"C:/Users/acer/.gemini/antigravity/brain/ef7f8d34-cb57-4fb6-af61-5acd6adfb91a/.user_uploaded/media_1793370505332_8ebbd9a3.png"
    IMG_EVAL = r"C:/Users/acer/.gemini/antigravity/brain/ef7f8d34-cb57-4fb6-af61-5acd6adfb91a/.user_uploaded/media_1793372322569_32eeb867.png"

    def apply_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.color.rgb = BG_COLOR
        return bg

    def add_header(slide, title_text, category="DEEP LEARNING (DS306)  |  FINAL PROJECT"):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.7), Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        
        p0 = tf.paragraphs[0]
        p0.text = category.upper()
        p0.font.size = Pt(13)
        p0.font.bold = True
        p0.font.color.rgb = ACCENT_CYAN
        
        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(28)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_WHITE
        p1.space_before = Pt(3)

    # ==================== SLIDE 1: COVER PAGE ====================
    s1 = prs.slides.add_slide(blank_layout)
    apply_bg(s1)

    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(0.8), Inches(11.5), Inches(5.9))
    card1.fill.solid()
    card1.fill.fore_color.rgb = CARD_BG
    card1.line.color.rgb = ACCENT_CYAN
    card1.line.width = Pt(2.0)

    tb1 = s1.shapes.add_textbox(Inches(1.4), Inches(1.1), Inches(10.5), Inches(5.3))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "DEEP LEARNING  •  COURSE CODE: DS306"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(10)

    p = tf1.add_paragraph()
    p.text = "ThreatLens AI"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    p = tf1.add_paragraph()
    p.text = "Explainable Network Intrusion Detection using Deep Neural Networks"
    p.font.size = Pt(22)
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(28)

    p = tf1.add_paragraph()
    p.text = "Course Instructor:"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = TEXT_MUTED

    p = tf1.add_paragraph()
    p.text = "Dr. Kongara Srinivasa Rao"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(22)

    p = tf1.add_paragraph()
    p.text = "Project Submitted By:"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = TEXT_MUTED

    p = tf1.add_paragraph()
    p.text = "•  T Yokshith   (23STUCHH010958)\n•  Nitin Sain    (23STUCHH010968)"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    # ==================== SLIDE 2: PROBLEM STATEMENT ====================
    s2 = prs.slides.add_slide(blank_layout)
    apply_bg(s2)
    add_header(s2, "Problem Statement: Why Deep Learning in Cybersecurity?")

    cards_data = [
        ("1. Traditional Firewalls Fail on Zero-Day Threats",
         "Legacy Intrusion Detection Systems (Snort, static firewalls) rely entirely on known signatures. They are powerless against polymorphic attacks, new DoS variants, and evasive probes.",
         RED_ACC),
        ("2. The 'Black-Box' Problem in AI Models",
         "Standard machine learning classifiers alert analysts that an attack occurred, but cannot explain WHY. Without feature attribution, SOC analysts face severe alert fatigue and false positives.",
         ACCENT_CYAN),
        ("3. High-Velocity Network Flow Demands",
         "Enterprise networks process tens of thousands of packets per second. Detection systems must classify flows in sub-milliseconds without introducing latency into the network infrastructure.",
         GREEN_ACC)
    ]

    for i, (head, desc, color) in enumerate(cards_data):
        top_y = 1.6 + i * 1.8
        c = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(11.7), Inches(1.55))
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_BG
        c.line.color.rgb = BORDER_COLOR
        c.line.width = Pt(1.5)

        t = s2.shapes.add_textbox(Inches(1.1), Inches(top_y + 0.15), Inches(11.1), Inches(1.25))
        tf = t.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = head
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(6)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(16)
        p.font.color.rgb = TEXT_WHITE

    # ==================== SLIDE 3: DEEP LEARNING TECHNOLOGIES ====================
    s3 = prs.slides.add_slide(blank_layout)
    apply_bg(s3)
    add_header(s3, "Deep Learning Technologies & Frameworks")

    tech_data = [
        ("PyTorch 2.11 Framework", "High-performance deep learning library supporting dynamic tensor computation, GPU/CPU execution, and custom autograd engines."),
        ("Multi-Layer Perceptron (MLP)", "Fully connected feed-forward architecture capable of learning complex non-linear decision boundaries between benign and attack vectors."),
        ("Batch Normalization (BatchNorm1d)", "Applied after each dense layer to eliminate internal covariate shift, stabilize training dynamics, and accelerate convergence."),
        ("Dropout Regularization (p = 0.2)", "Randomly zeroes 20% of neuron outputs during training to prevent co-adaptation and eliminate overfitting on specific dataset artifacts."),
        ("BCEWithLogitsLoss (pos_weight = 3.0)", "Combines Sigmoid + Binary Cross-Entropy with positive-class reweighting to penalize missed cyber attacks 3x heavier than false alarms."),
        ("Adam Optimizer + LR Scheduler", "Adaptive moment estimation with ReduceLROnPlateau to dynamically reduce learning rates when validation loss reaches a plateau.")
    ]

    for i, (title, desc) in enumerate(tech_data):
        col = i % 2
        row = i // 2
        left_x = 0.8 + col * 5.95
        top_y = 1.6 + row * 1.8

        c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_x), Inches(top_y), Inches(5.75), Inches(1.6))
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_BG
        c.line.color.rgb = BORDER_COLOR
        c.line.width = Pt(1.2)

        t = s3.shapes.add_textbox(Inches(left_x + 0.2), Inches(top_y + 0.15), Inches(5.35), Inches(1.3))
        tf = t.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN
        p.space_after = Pt(4)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(14)
        p.font.color.rgb = TEXT_WHITE

    # ==================== SLIDE 4: MODEL ARCHITECTURE ====================
    s4 = prs.slides.add_slide(blank_layout)
    apply_bg(s4)
    add_header(s4, "Deep Learning Model Architecture: ThreatLensMLP")

    # Left card: Pipeline details
    c_arch1 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(6.0), Inches(5.3))
    c_arch1.fill.solid()
    c_arch1.fill.fore_color.rgb = CARD_BG
    c_arch1.line.color.rgb = BORDER_COLOR
    c_arch1.line.width = Pt(1.5)

    t_a1 = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.6), Inches(4.9))
    tf_a1 = t_a1.text_frame
    tf_a1.word_wrap = True

    p = tf_a1.paragraphs[0]
    p.text = "Neural Layer Specification"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(14)

    arch_layers = [
        "1. Input Dimension: 59 Tabular Features",
        "2. Hidden Layer 1: Linear(59 → 64)",
        "    • BatchNorm1d(64) + ReLU() + Dropout(0.2)",
        "3. Hidden Layer 2: Linear(64 → 32)",
        "    • BatchNorm1d(32) + ReLU() + Dropout(0.2)",
        "4. Output Layer: Linear(32 → 1)  (Raw Logit)",
        "5. Output Activation: Sigmoid(Logit) ∈ [0.0, 1.0]",
        "    • Threshold = 0.50  (≥ 0.50 Flagged as Attack)"
    ]
    for line in arch_layers:
        p = tf_a1.add_paragraph()
        p.text = line
        p.font.size = Pt(15 if not line.startswith("    ") else 14)
        p.font.bold = not line.startswith("    ")
        p.font.color.rgb = TEXT_MUTED if line.startswith("    ") else TEXT_WHITE
        p.space_after = Pt(4)

    # Right card: Architectural Advantages
    c_arch2 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(1.6), Inches(5.4), Inches(5.3))
    c_arch2.fill.solid()
    c_arch2.fill.fore_color.rgb = CARD_BG
    c_arch2.line.color.rgb = BORDER_COLOR
    c_arch2.line.width = Pt(1.5)

    t_a2 = s4.shapes.add_textbox(Inches(7.3), Inches(1.8), Inches(5.0), Inches(4.9))
    tf_a2 = t_a2.text_frame
    tf_a2.word_wrap = True

    p = tf_a2.paragraphs[0]
    p.text = "Key Design Strengths"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACC
    p.space_after = Pt(14)

    advs = [
        ("Compact & Fast:", "Only 6,017 parameters — avoids bloat while providing rich non-linear representation capacity."),
        ("Sub-Millisecond Inference:", "Average single-flow classification time is just 0.51 ms on a standard CPU."),
        ("No Data Leakage:", "StandardScaler parameters are saved from training set only; test flows never leak statistical bounds."),
        ("Direct XAI Saliency:", "Clean feed-forward geometry allows direct first-layer weight sensitivity analysis without autograd lag.")
    ]
    for h, b in advs:
        p = tf_a2.add_paragraph()
        p.text = f"✔ {h} {b}"
        p.font.size = Pt(15)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(12)

    # ==================== SLIDE 5: HOW THE MODEL WORKS ====================
    s5 = prs.slides.add_slide(blank_layout)
    apply_bg(s5)
    add_header(s5, "How ThreatLens AI Works: End-to-End Pipeline")

    pipe_steps = [
        ("Step 1: Raw Traffic Capture", "Ingests network connection records (CIC-IDS2017 format with 78 physical network features including Flow Duration, Packet Rates, Flag counts)."),
        ("Step 2: Cleaning & Preprocessing", "Strips whitespace, cleans Infinite/NaN values, drops zero-variance columns (78 → 59 features), and applies pre-saved training StandardScaler."),
        ("Step 3: PyTorch Deep Inference", "Normalized vector passes through ThreatLensMLP layers with ReLU non-linearities and BatchNorm to compute final scalar logit."),
        ("Step 4: Anomaly Scoring & Risk Triage", "Sigmoid activation maps logit to Anomaly Probability [0, 1]. Categorized into 4 risk tiers: BENIGN, ELEVATED, SUSPICIOUS, or CRITICAL alert."),
        ("Step 5: Explainable AI Attribution", "First-layer weight magnitude analysis highlights the top 3 physical features that pushed the flow toward an anomaly alert.")
    ]

    for i, (stitle, sdesc) in enumerate(pipe_steps):
        top_y = 1.6 + i * 1.08
        c = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(11.7), Inches(0.98))
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_BG
        c.line.color.rgb = BORDER_COLOR

        t = s5.shapes.add_textbox(Inches(1.0), Inches(top_y + 0.1), Inches(11.3), Inches(0.8))
        tf = t.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = f"{stitle}:  "
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN

        run = p.add_run()
        run.text = sdesc
        run.font.size = Pt(14)
        run.font.bold = False
        run.font.color.rgb = TEXT_WHITE

    # ==================== SLIDE 6: EXPLAINABLE AI WITH REAL PHOTO ====================
    s6 = prs.slides.add_slide(blank_layout)
    apply_bg(s6)
    add_header(s6, "Explainable AI (XAI): White-Box Threat Attribution")

    # Left text card
    c_xai = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    c_xai.fill.solid()
    c_xai.fill.fore_color.rgb = CARD_BG
    c_xai.line.color.rgb = BORDER_COLOR
    c_xai.line.width = Pt(1.5)

    t_x = s6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf_x = t_x.text_frame
    tf_x.word_wrap = True

    p = tf_x.paragraphs[0]
    p.text = "Mathematical Attribution Engine"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(12)

    xai_bullets = [
        "• Purpose: Turns 'black-box' deep learning into actionable SOC intelligence.",
        "• Formulation: Saliency_j = Mean(|W1[:, j]|) × |x_j|",
        "   - W1: First Linear layer weights (sensitivity).",
        "   - x_j: Normalized input feature value.",
        "• Live Case (Shown on Right):",
        "   - Connection: Port 53 (DNS) | Score: 0.985 (CRITICAL)",
        "   - Top Drivers: Flow IAT Min (+3.64σ), Min Packet Length",
        "   - Diagnostic: Identifies rapid automated probe packets deviating from regular human DNS lookups."
    ]
    for b in xai_bullets:
        p = tf_x.add_paragraph()
        p.text = b
        p.font.size = Pt(14 if b.startswith("   ") else 15)
        p.font.bold = not b.startswith("   ")
        p.font.color.rgb = TEXT_MUTED if b.startswith("   ") else TEXT_WHITE
        p.space_after = Pt(4)

    # Right side: Embed user's actual screenshot
    if os.path.exists(IMG_XAI):
        s6.shapes.add_picture(IMG_XAI, Inches(6.6), Inches(1.6), width=Inches(5.9), height=Inches(5.3))

    # ==================== SLIDE 7: EMPIRICAL RESULTS WITH REAL PHOTO ====================
    s7 = prs.slides.add_slide(blank_layout)
    apply_bg(s7)
    add_header(s7, "Empirical Results: Performance & Evaluation")

    # Left side: Metrics Table Card
    c_res = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    c_res.fill.solid()
    c_res.fill.fore_color.rgb = CARD_BG
    c_res.line.color.rgb = BORDER_COLOR
    c_res.line.width = Pt(1.5)

    t_r = s7.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf_r = t_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Test Split Benchmark Results"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACC
    p.space_after = Pt(10)

    res_lines = [
        "• Held-Out Test Set: 900 flows (strictly isolated)",
        "• Accuracy: 100.00 %",
        "• Precision: 100.00 %",
        "• Recall (Sensitivity): 100.00 %",
        "• F1-Score: 1.0000",
        "• ROC-AUC: 1.0000 (Area Under Curve)",
        "• Single Latency: 0.51 ms per connection",
        "• Confusion Matrix Breakdown:",
        "   - True Benign: 675 flows | True Attack: 225 flows",
        "   - False Positives: 0     | False Negatives: 0"
    ]
    for line in res_lines:
        p = tf_r.add_paragraph()
        p.text = line
        p.font.size = Pt(14 if line.startswith("   ") else 15)
        p.font.bold = not line.startswith("   ")
        p.font.color.rgb = GREEN_ACC if "100.00" in line or "1.0000" in line else (TEXT_MUTED if line.startswith("   ") else TEXT_WHITE)
        p.space_after = Pt(4)

    # Right side: Embed user's actual confusion matrix & ROC curve photo
    if os.path.exists(IMG_EVAL):
        s7.shapes.add_picture(IMG_EVAL, Inches(6.6), Inches(1.6), width=Inches(5.9), height=Inches(5.3))

    # ==================== SLIDE 8: INTERACTIVE SOC DASHBOARD WITH PHOTO ====================
    s8 = prs.slides.add_slide(blank_layout)
    apply_bg(s8)
    add_header(s8, "Interactive Security Operations Center (SOC) Dashboard")

    # Left card: Features
    c_soc = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    c_soc.fill.solid()
    c_soc.fill.fore_color.rgb = CARD_BG
    c_soc.line.color.rgb = BORDER_COLOR
    c_soc.line.width = Pt(1.5)

    t_sc = s8.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf_sc = t_sc.text_frame
    tf_sc.word_wrap = True

    p = tf_sc.paragraphs[0]
    p.text = "SOC Interface Capabilities"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(12)

    soc_points = [
        ("Live Overview Telemetry:", "Real-time donut class distribution (75% Benign, 25% Attack), threat breakdown (DoS Hulk, PortScan, FTP-Patator), and instant alert feed."),
        ("Production File Ingestion:", "Supports direct CSV uploads of large real-world captures (tested on 225,745 flows) with dynamic batch sampling."),
        ("Analyst Threshold Control:", "Interactive risk sensitivity slider allows SOC operators to filter background noise and isolate critical threats."),
        ("Single-Click Export:", "Export fully classified flows with risk tags and top feature attributions to CSV for incident response logs.")
    ]
    for h, b in soc_points:
        p = tf_sc.add_paragraph()
        p.text = f"✔ {h} {b}"
        p.font.size = Pt(14)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

    # Right side: Embed user's actual dashboard overview screenshot
    if os.path.exists(IMG_OVERVIEW):
        s8.shapes.add_picture(IMG_OVERVIEW, Inches(6.6), Inches(1.6), width=Inches(5.9), height=Inches(5.3))

    # ==================== SLIDE 9: CONCLUSION & THANK YOU ====================
    s9 = prs.slides.add_slide(blank_layout)
    apply_bg(s9)

    card_c = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(0.9), Inches(10.9), Inches(5.7))
    card_c.fill.solid()
    card_c.fill.fore_color.rgb = CARD_BG
    card_c.line.color.rgb = ACCENT_CYAN
    card_c.line.width = Pt(2.0)

    tb_c = s9.shapes.add_textbox(Inches(1.6), Inches(1.2), Inches(10.1), Inches(5.1))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p = tf_c.paragraphs[0]
    p.text = "CONCLUSION & PROJECT SUMMARY"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(8)

    p = tf_c.add_paragraph()
    p.text = "ThreatLens AI — Final Project Delivery"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(14)

    conc_bullets = [
        "✔ Successfully built an end-to-end Deep Learning Intrusion Detection System using PyTorch.",
        "✔ Integrated Explainable AI (XAI) feature attribution, removing black-box opacity in security operations.",
        "✔ Enforced strict zero-data-leakage preprocessing, achieving 100% precision & recall on held-out tests.",
        "✔ Deployed a live 3-page interactive SOC dashboard capable of analyzing 225k+ real network flows."
    ]
    for b in conc_bullets:
        p = tf_c.add_paragraph()
        p.text = b
        p.font.size = Pt(16)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    p = tf_c.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "\nThank You, Dr. Kongara Srinivasa Rao!"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = GREEN_ACC

    p = tf_c.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.text = "Questions & Answers (Viva Defense)\nPresented by: T Yokshith (23STUCHH010958) & Nitin Sain (23STUCHH010968)"
    p.font.size = Pt(16)
    p.font.color.rgb = TEXT_MUTED

    output_path = os.path.abspath("ThreatLens_AI_Final_Presentation.pptx")
    prs.save(output_path)
    print(f"9-slide presentation successfully generated at: {output_path}")
    try:
        prs.save(os.path.abspath("ThreatLens_AI_Presentation.pptx"))
    except Exception:
        pass

if __name__ == "__main__":
    build_presentation()
