import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Don't draw headers/footers on cover page
        if self._pageNumber > 1:
            # Header
            self.drawString(54, letter[1] - 36, "ThreatLens AI — Code Walkthrough & Technical Guide | DS306")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
            
            # Footer
            self.line(54, 46, letter[0] - 54, 46)
            self.drawString(54, 32, "Submitted by: T Yokshith & Nitin Sain  |  Instructor: Dr. Kongara Srinivasa Rao")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(letter[0] - 54, 32, page_text)
            
        self.restoreState()

def generate_code_explanation_pdf(filename="ThreatLens_AI_Code_Walkthrough.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1A365D")      # Deep Navy
    SECONDARY = colors.HexColor("#2B6CB0")    # Classic Blue
    ACCENT = colors.HexColor("#2C5282")       # Slate Blue
    DARK_TEXT = colors.HexColor("#2D3748")    # Charcoal body
    CODE_BG = colors.HexColor("#F7FAFC")      # Off-white code bg
    CODE_BORDER = colors.HexColor("#CBD5E0")  # Light gray border
    BORDER_LIGHT = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        alignment=0,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=17,
        textColor=SECONDARY,
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=DARK_TEXT
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_TEXT,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_TEXT,
        leftIndent=15,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1A202C")
    )

    viva_q = ParagraphStyle(
        'VivaQ',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13.5,
        textColor=PRIMARY,
        spaceBefore=4,
        spaceAfter=2
    )

    viva_a = ParagraphStyle(
        'VivaA',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_TEXT,
        leftIndent=10,
        spaceAfter=6
    )

    story = []

    # ==================== COVER / HEADER BANNER ====================
    story.append(Paragraph("ThreatLens AI — Code Walkthrough", title_style))
    story.append(Paragraph("Technical Code Architecture & Line-by-Line Viva Defense Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceBefore=0, spaceAfter=12))

    meta_table_data = [
        [
            Paragraph("<b>Subject:</b> Deep Learning (DS306)", meta_style),
            Paragraph("<b>Course Instructor:</b> Dr. Kongara Srinivasa Rao", meta_style)
        ],
        [
            Paragraph("<b>Submitted By:</b> T Yokshith (23STUCHH010958)", meta_style),
            Paragraph("<b>Submitted By:</b> Nitin Sain (23STUCHH010968)", meta_style)
        ],
        [
            Paragraph("<b>Project Root:</b> <code>D:\\yokshi dl\\</code>", meta_style),
            Paragraph("<b>Framework:</b> PyTorch 2.11 + Streamlit 1.66", meta_style)
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[240, 264])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # ==================== EXECUTIVE PROJECT ARCHITECTURE ====================
    story.append(Paragraph("1. Project Architecture & File Directory", h1_style))
    story.append(Paragraph(
        "ThreatLens AI is an end-to-end Explainable Deep Learning Intrusion Detection System (IDS). "
        "It replaces black-box classifiers with a transparent Multi-Layer Perceptron (MLP) featuring "
        "first-layer weight-magnitude saliency for root-cause diagnosis. Below is the structural hierarchy of the codebase:",
        body_style
    ))

    dir_code = (
        "D:\\yokshi dl\\\n"
        "├── src/\n"
        "│   ├── model.py               # ThreatLensMLP PyTorch architecture & XAI explain_flow()\n"
        "│   ├── train_model.py         # BCEWithLogitsLoss, Adam, ReduceLROnPlateau training loop\n"
        "│   ├── data_preprocessing.py  # Zero-leakage StandardScaler, NaN cleaning, 70/15/15 split\n"
        "│   ├── predict.py             # Inference pipeline & batch classification engine\n"
        "│   └── evaluate.py            # Confusion matrix, ROC-AUC, PR-AUC & latency metrics\n"
        "├── pages/\n"
        "│   ├── 1_Overview.py          # SOC telemetry, donut class distribution, alerts feed\n"
        "│   ├── 2_Traffic_Analysis.py  # Real-time CSV ingestion, threshold slider, XAI gauge\n"
        "│   └── 3_Model_Evaluation.py  # Model vs baseline comparison & academic Viva Q&A\n"
        "├── app.py                     # Main Streamlit hub entrypoint\n"
        "└── models/                    # Serialized PyTorch weights (.pt) & preprocessing (.pkl)"
    )
    t_dir = Table([[Paragraph(dir_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style)]], colWidths=[504])
    t_dir.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CODE_BG),
        ('BOX', (0,0), (-1,-1), 1, CODE_BORDER),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_dir)
    story.append(Spacer(1, 14))

    # ==================== FILE 1: src/model.py ====================
    story.append(Paragraph("2. Core Deep Learning Model — <code>src/model.py</code>", h1_style))
    story.append(Paragraph(
        "This file defines the <b>ThreatLensMLP</b> neural network class and the <b>explain_flow()</b> "
        "feature attribution engine. It is the most critical file for your Deep Learning evaluation.",
        body_style
    ))

    story.append(Paragraph("A. ThreatLensMLP Architecture Breakdown", h2_style))
    story.append(Paragraph(
        "The model is a deep feed-forward Multi-Layer Perceptron implemented via <code>torch.nn.Sequential</code>:",
        body_style
    ))

    arch_code = (
        "class ThreatLensMLP(nn.Module):\n"
        "    def __init__(self, input_dim: int, hidden_dim1: int = 64, hidden_dim2: int = 32, dropout_rate: float = 0.2):\n"
        "        super(ThreatLensMLP, self).__init__()\n"
        "        self.network = nn.Sequential(\n"
        "            # Layer 1: 59 inputs -> 64 hidden units\n"
        "            nn.Linear(input_dim, hidden_dim1),\n"
        "            nn.BatchNorm1d(hidden_dim1),\n"
        "            nn.ReLU(),\n"
        "            nn.Dropout(dropout_rate),\n"
        "            \n"
        "            # Layer 2: 64 -> 32 hidden units\n"
        "            nn.Linear(hidden_dim1, hidden_dim2),\n"
        "            nn.BatchNorm1d(hidden_dim2),\n"
        "            nn.ReLU(),\n"
        "            nn.Dropout(dropout_rate),\n"
        "            \n"
        "            # Layer 3: 32 -> 1 output logit (unbounded scalar)\n"
        "            nn.Linear(hidden_dim2, 1)\n"
        "        )\n"
        "\n"
        "    def forward(self, x: torch.Tensor) -> torch.Tensor:\n"
        "        return self.network(x)\n"
        "        \n"
        "    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:\n"
        "        self.eval()\n"
        "        with torch.no_grad():\n"
        "            return torch.sigmoid(self.forward(x))"
    )
    t_arch = Table([[Paragraph(arch_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style)]], colWidths=[504])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CODE_BG),
        ('BOX', (0,0), (-1,-1), 1, CODE_BORDER),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Key Architectural Concepts to Explain to Dr. Kongara:</b>", body_style))
    story.append(Paragraph("• <b>Input Dimension (59 Features):</b> Derived after removing zero-variance and redundant identifier columns from 78 raw CIC-IDS2017 features.", bullet_style))
    story.append(Paragraph("• <b>BatchNorm1d:</b> Normalizes batch activations to mean=0, var=1. This accelerates convergence and prevents internal covariate shift.", bullet_style))
    story.append(Paragraph("• <b>Dropout (p=0.2):</b> Zeroes out 20% of neuron outputs randomly during training to prevent co-adaptation and overfitting.", bullet_style))
    story.append(Paragraph("• <b>Raw Logits vs Sigmoid:</b> The output layer returns raw unnormalized logits so we can use numerically stable <code>BCEWithLogitsLoss</code> during training, while applying <code>torch.sigmoid</code> only at test time.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("B. Explainable AI Engine — <code>explain_flow()</code>", h2_style))
    story.append(Paragraph(
        "Instead of opaque predictions, ThreatLens computes <b>first-layer weight-magnitude saliency</b>. "
        "It measures how much each feature is amplified by the first dense layer multiplied by the actual standardized input deviation:",
        body_style
    ))

    xai_code = (
        "def explain_flow(self, x_single: torch.Tensor, feature_names: List[str], top_k: int = 5):\n"
        "    self.eval()\n"
        "    with torch.no_grad():\n"
        "        x_val = x_single.squeeze(0) if x_single.ndim > 1 else x_single\n"
        "        W1 = self.network[0].weight             # First Linear layer [64, 59]\n"
        "        mean_abs_weight = W1.abs().mean(dim=0)  # Sensitivity per input feature\n"
        "        saliency = (mean_abs_weight * x_val.abs()).cpu().numpy()\n"
        "\n"
        "    top_indices = np.argsort(saliency)[::-1][:top_k]\n"
        "    return [{'feature': feature_names[i], 'attribution_score': float(saliency[i])} for i in top_indices]"
    )
    t_xai = Table([[Paragraph(xai_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style)]], colWidths=[504])
    t_xai.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CODE_BG),
        ('BOX', (0,0), (-1,-1), 1, CODE_BORDER),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_xai)
    story.append(Spacer(1, 8))

    # ==================== FILE 2: src/train_model.py ====================
    story.append(Paragraph("3. Training Pipeline & Loss Function — <code>src/train_model.py</code>", h1_style))
    story.append(Paragraph(
        "This script orchestrates the model optimization, handling class imbalance, dynamic learning rates, "
        "and early stopping. It also trains a baseline Logistic Regression model for academic comparison.",
        body_style
    ))

    train_code = (
        "# 1. Class Imbalance Reweighting\n"
        "pos_weight = torch.tensor([3.0]).to(device)  # Penalizes missed intrusions 3x heavier\n"
        "criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)\n"
        "\n"
        "# 2. Optimizer & Dynamic Scheduler\n"
        "optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)\n"
        "scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)\n"
        "\n"
        "# 3. Epoch Loop with Early Stopping\n"
        "for epoch in range(1, epochs + 1):\n"
        "    model.train()\n"
        "    optimizer.zero_grad()\n"
        "    logits = model(x_train_batch).squeeze(-1)\n"
        "    loss = criterion(logits, y_train_batch)\n"
        "    loss.backward()\n"
        "    optimizer.step()\n"
        "    \n"
        "    # Validation & Early Stopping Check\n"
        "    scheduler.step(val_loss)\n"
        "    if val_f1 > best_val_f1:\n"
        "        torch.save(model.state_dict(), 'models/mlp_model.pt')"
    )
    t_tr = Table([[Paragraph(train_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style)]], colWidths=[504])
    t_tr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CODE_BG),
        ('BOX', (0,0), (-1,-1), 1, CODE_BORDER),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_tr)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Key Training Concepts to Defend:</b>", body_style))
    story.append(Paragraph("• <b>pos_weight=3.0:</b> In cybersecurity, a False Negative (undetected malware) is far more dangerous than a False Positive. The 3.0 weight forces the loss function to prioritize catching intrusions.", bullet_style))
    story.append(Paragraph("• <b>ReduceLROnPlateau:</b> When validation loss plateaus for 3 epochs, the learning rate drops by 50% (factor=0.5), allowing fine-grained convergence into local minima.", bullet_style))
    story.append(Paragraph("• <b>Baseline Comparison:</b> We train a `LogisticRegression(class_weight='balanced')` on the exact same splits to prove the non-linear MLP's superiority.", bullet_style))

    # ==================== FILE 3: src/data_preprocessing.py ====================
    story.append(Paragraph("4. Preprocessing & Leakage Prevention — <code>src/data_preprocessing.py</code>", h1_style))
    story.append(Paragraph(
        "Rigorous data hygiene is required for academic integrity. This module cleans real-world network captures "
        "and isolates train/val/test splits before computing normalization parameters.",
        body_style
    ))

    pre_code = (
        "def preprocess_cicids_pipeline(df_raw, test_size=0.15, val_size=0.15, random_state=42):\n"
        "    # Step 1: Clean column names (strip leading/trailing whitespace)\n"
        "    df = clean_column_names(df_raw)\n"
        "    \n"
        "    # Step 2: Handle infinities and NaNs (replace with 0 or column max)\n"
        "    df = clean_features(df)\n"
        "    \n"
        "    # Step 3: Stratified Split BEFORE scaling (Prevents Data Leakage!)\n"
        "    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, stratify=y)\n"
        "    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, stratify=y_temp)\n"
        "    \n"
        "    # Step 4: Fit StandardScaler ONLY on X_train\n"
        "    scaler = StandardScaler()\n"
        "    X_train_scaled = scaler.fit_transform(X_train)\n"
        "    X_val_scaled = scaler.transform(X_val)      # Transform only\n"
        "    X_test_scaled = scaler.transform(X_test)    # Transform only\n"
        "    \n"
        "    # Save scaler and feature names to models/preprocessing.pkl"
    )
    t_pre = Table([[Paragraph(pre_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style)]], colWidths=[504])
    t_pre.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CODE_BG),
        ('BOX', (0,0), (-1,-1), 1, CODE_BORDER),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_pre)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Zero Data Leakage Rule:</b>", body_style))
    story.append(Paragraph(
        "If a model fits <code>StandardScaler</code> on the entire dataset before splitting, the mean and variance "
        "of the test data leak into training. In ThreatLens AI, <code>scaler.fit()</code> is strictly restricted to "
        "<code>X_train</code>, guaranteeing completely blind, honest test split evaluation.",
        body_style
    ))

    # ==================== FILE 4: src/predict.py & evaluate.py ====================
    story.append(Paragraph("5. Inference & Evaluation — <code>src/predict.py</code> & <code>src/evaluate.py</code>", h1_style))
    story.append(Paragraph(
        "<code>ThreatLensPredictor</code> provides an enterprise-ready inference class. "
        "It categorizes incoming flows into four operational risk levels based on model confidence:",
        body_style
    ))

    risk_table_data = [
        [Paragraph("<b>Risk Level</b>", meta_style), Paragraph("<b>Anomaly Probability</b>", meta_style), Paragraph("<b>SOC Action</b>", meta_style)],
        [Paragraph("<font color='#2ea043'><b>BENIGN</b></font>", meta_style), Paragraph("0.00 to 0.35", meta_style), Paragraph("Normal authorized traffic. No action required.", meta_style)],
        [Paragraph("<font color='#3182ce'><b>ELEVATED</b></font>", meta_style), Paragraph("0.35 to 0.50", meta_style), Paragraph("Mild anomaly (traffic spikes / unusual port). Logged.", meta_style)],
        [Paragraph("<font color='#dd6b20'><b>SUSPICIOUS</b></font>", meta_style), Paragraph("0.50 to 0.70", meta_style), Paragraph("Flagged attack candidate. Queue for analyst review.", meta_style)],
        [Paragraph("<font color='#e53e3e'><b>CRITICAL</b></font>", meta_style), Paragraph("0.70 to 1.00", meta_style), Paragraph("High-confidence intrusion. Instant firewall block alert.", meta_style)]
    ]
    t_risk = Table(risk_table_data, colWidths=[90, 130, 284])
    t_risk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2D3748")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_risk)
    story.append(Spacer(1, 10))

    # ==================== VIVA DEFENSE CHEAT SHEET ====================
    story.append(Paragraph("6. Academic Viva Defense Cheat Sheet (Questions for Sir)", h1_style))
    story.append(Paragraph(
        "Dr. Kongara Srinivasa Rao is likely to ask technical questions about why specific architectural "
        "and mathematical choices were made. Use these prepared answers:",
        body_style
    ))

    viva_qa = [
        ("Q1: Why did you use Multi-Layer Perceptron (MLP) instead of CNN or LSTM?",
         "A: Network flow data from CIC-IDS2017 is aggregated tabular data (features like Flow Duration, Total Packets, IAT), not raw byte sequences or images. MLPs with non-linear activations excel at tabular feature correlations and achieve sub-millisecond (0.51 ms) execution, making them ideal for high-speed network gateways."),
        
        ("Q2: Why use BCEWithLogitsLoss instead of BCELoss + Sigmoid in the forward pass?",
         "A: Combining the Sigmoid activation and Binary Cross Entropy into a single layer (BCEWithLogitsLoss) takes advantage of the log-sum-exp trick. This prevents severe numerical instability, floating-point overflow, and exploding/vanishing gradients during backpropagation."),
        
        ("Q3: How does your Explainable AI (XAI) work mathematically?",
         "A: We compute first-layer weight-magnitude saliency: Saliency_j = Mean(|W1[:, j]|) * |x_j|. It multiplies the neural network's structural sensitivity to feature j (the weights connecting feature j to layer 1) by the standardized deviation of the input. This highlights features that pushed the score highest without needing slow autograd backward passes in production."),
        
        ("Q4: How did you ensure your model does not overfit?",
         "A: We used three distinct regularization techniques: (1) Dropout layers (p=0.2) after every hidden activation, (2) BatchNorm1d to regularize activations across batches, and (3) Weight decay (L2 regularization = 1e-4) in the Adam optimizer."),

        ("Q5: What happened when the Anomaly Score Threshold slider was changed in the app?",
         "A: The threshold slider acts as an operational noise filter. At 0.00, analysts see all traffic. At 0.25, the dashboard filters out the 809 normal benign flows (score 0.00), isolating only suspicious flows and critical alarms for triage.")
    ]

    for q, a in viva_qa:
        story.append(Paragraph(q, viva_q))
        story.append(Paragraph(a, viva_a))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Code walkthrough PDF generated successfully at: {os.path.abspath(filename)}")

if __name__ == "__main__":
    generate_code_explanation_pdf()
