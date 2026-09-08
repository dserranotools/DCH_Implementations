import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Modern styling parameters
plt.rcParams['font.sans-serif'] = 'Segoe UI, Arial, sans-serif'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8

output_dir = r"d:\DevelopmentLocal\Daniel\DCH\Branches\DCH440_Git.worktrees\DCH440_Forecast_Lags\Docs\Insights_Forecast_Accuracy\images"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------
# 1. ACCURACY FUNNEL (Lag Evolution by Category)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#FFFFFF')

lags = np.array([6, 5, 4, 3, 2, 1])
wape_total = np.array([32.5, 27.8, 22.4, 18.2, 14.8, 11.5])
wape_ambient = np.array([24.0, 21.2, 17.5, 14.0, 11.2, 8.5])
wape_fresh = np.array([42.0, 36.5, 29.8, 24.5, 19.8, 15.2])

ax.plot(lags, wape_fresh, marker='o', color='#EF4444', linewidth=2.5, label='Fresh & Perishables (High Volatility)')
ax.plot(lags, wape_total, marker='s', color='#2563EB', linewidth=3.5, label='Total Portfolio (Average)')
ax.plot(lags, wape_ambient, marker='^', color='#10B981', linewidth=2.5, label='Ambient / Core Ambient (Stable)')

# Annotate points for Total Portfolio
for x, y in zip(lags, wape_total):
    ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 10),
                ha='center', fontsize=9, fontweight='bold', color='#1E293B',
                bbox=dict(boxstyle="round,pad=0.2", fc="#EFF6FF", ec="#BFDBFE", lw=0.8))

ax.invert_xaxis()
ax.set_title("The Accuracy Funnel: WAPE (%) Evolution by Planning Lag", fontsize=14, fontweight='bold', pad=15, color='#0F172A')
ax.set_xlabel("Planning Horizon (Lag Periods Ahead of Target Month)", fontsize=11, fontweight='semibold', labelpad=10, color='#334155')
ax.set_ylabel("Error - WAPE (%)", fontsize=11, fontweight='semibold', labelpad=10, color='#334155')
ax.set_ylim(0, 50)
ax.grid(True, linestyle='--', alpha=0.5, color='#E2E8F0')
ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#E2E8F0', fontsize=10, loc='upper left')

# Subtle note
ax.text(0.98, 0.04, "Target: Error shrinks as Lag decreases (Convergence Zone)", 
        transform=ax.transAxes, ha='right', fontsize=9, fontstyle='italic', color='#64748B')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "01_accuracy_funnel.jpg"), format='jpg', dpi=200)
plt.close()

# -------------------------------------------------------------
# 2. FORECAST VALUE ADD (FVA) WATERFALL
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.8), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#FFFFFF')

stages = ['SO99 Baseline\n(FrcRev 0)', 'Sales / KAM\n(FrcRev 1)', 'Demand Plan\n(FrcRev 2)', 'Finance / S&OP\n(FrcRev 3)', 'Executive\nConsensus (Rev 4)']
start_val = 18.5
# Deltas: Sales (-1.8% green), DP (-2.4% green), Finance (+1.2% red - error increase / value destruction), Consensus (-0.9% green)
deltas = [0, -1.8, -2.4, +1.2, -0.9]
running = [start_val]
for d in deltas[1:]:
    running.append(running[-1] + d)

# Bar plotting
x = np.arange(len(stages))
for i in range(len(stages)):
    if i == 0:
        ax.bar(x[i], running[i], color='#3B82F6', width=0.52, edgecolor='#1D4ED8')
        ax.text(x[i], running[i] + 0.45, f"{running[i]:.1f}%", ha='center', fontweight='bold', color='#1E293B', fontsize=10.5)
    elif i == len(stages) - 1:
        ax.bar(x[i], running[i], color='#059669', width=0.52, edgecolor='#047857')
        ax.text(x[i], running[i] + 0.45, f"{running[i]:.1f}%", ha='center', fontweight='bold', color='#065F46', fontsize=10.5)
    else:
        d = deltas[i]
        prev = running[i-1]
        curr = running[i]
        # If error decreased (d < 0): GREEN (Value Added). If error increased (d > 0): RED (Noise/Error Added)
        is_fva_positive = (d < 0)
        bar_color = '#10B981' if is_fva_positive else '#EF4444'
        bottom = curr if is_fva_positive else prev
        height = abs(d)
        
        ax.bar(x[i], height, bottom=bottom, color=bar_color, width=0.52, edgecolor='#0F172A', linewidth=0.6)
        
        # Crisp badge label placed cleanly above the bar
        if is_fva_positive:
            fva_text = f"+{abs(d):.1f}% FVA"
            badge_fc = "#D1FAE5"
            badge_ec = "#10B981"
            text_color = "#065F46"
            y_pos = bottom + height + 0.4
        else:
            fva_text = f"-{abs(d):.1f}% FVA\n(+{abs(d):.1f}% Err)"
            badge_fc = "#FEE2E2"
            badge_ec = "#EF4444"
            text_color = "#991B1B"
            y_pos = bottom + height + 0.45

        ax.text(x[i], y_pos, fva_text, ha='center', va='bottom',
                fontsize=8.5, fontweight='bold', color=text_color,
                bbox=dict(boxstyle="round,pad=0.25", fc=badge_fc, ec=badge_ec, lw=0.9))
            
        # Cumulative running error value below the floating bar
        ax.text(x[i], min(prev, curr) - 0.75, f"{curr:.1f}%", ha='center', fontsize=9.5, fontweight='bold', color='#475569')

ax.set_title("Forecast Value Add (FVA) Waterfall: Error Reduction vs. Human Noise", fontsize=14, fontweight='bold', pad=18, color='#0F172A')
ax.set_ylabel("WAPE Error (%) [Lower is Better]", fontsize=11, fontweight='semibold', labelpad=10, color='#334155')
ax.set_xticks(x)
ax.set_xticklabels(stages, fontsize=10, fontweight='semibold', color='#334155')
ax.set_ylim(0, 24.5)
ax.grid(True, axis='y', linestyle='--', alpha=0.5, color='#E2E8F0')

# Highlight Cumulative FVA
total_fva = start_val - running[-1]
ax.annotate(f"Net S&OP FVA: +{total_fva:.1f}% Accuracy Gain vs. SO99", xy=(4, running[-1]), xytext=(1.8, 22.0),
            arrowprops=dict(facecolor='#059669', shrink=0.08, width=1.5, headwidth=6),
            fontsize=10, fontweight='bold', color='#065F46',
            bbox=dict(boxstyle="round,pad=0.4", fc="#D1FAE5", ec="#6EE7B7"))

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "02_fva_waterfall.jpg"), format='jpg', dpi=200)
plt.close()

# -------------------------------------------------------------
# 3. BIAS VS ACCURACY QUADRANT MATRIX
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#FFFFFF')

# Data points: (Family, Bias, WAPE, Turnover_M)
points = [
    ("Beverages & Soft Drinks", 18.5, 34.0, 4.2),
    ("Dairy & Chilled", -14.2, 28.5, 3.8),
    ("Dry Pasta & Cereal", 1.8, 12.0, 5.5),
    ("Confectionery & Snacks", 12.0, 22.0, 2.4),
    ("Personal Care & Soap", -4.5, 14.2, 3.1),
    ("Canned Vegetables", -19.0, 31.0, 1.9),
    ("Coffee & Hot Drinks", 3.2, 11.5, 6.0),
    ("Frozen Foods", 24.0, 38.0, 2.8)
]

for name, bias, wape, val in points:
    # Color based on quadrant
    if wape > 20 and bias > 5:
        c = '#EF4444' # Overforecast
    elif wape > 20 and bias < -5:
        c = '#F59E0B' # Underforecast
    else:
        c = '#10B981' # High accuracy
    size = val * 90
    ax.scatter(bias, wape, s=size, color=c, alpha=0.7, edgecolors='#1E293B', linewidth=1)
    ax.annotate(f"{name}\n(€{val:.1f}M)", (bias, wape), textcoords="offset points", xytext=(0, 10),
                ha='center', fontsize=8.5, fontweight='semibold', color='#1E293B')

# Axes and Reference Lines
ax.axvline(0, color='#64748B', linestyle='-', linewidth=1.2, alpha=0.7)
ax.axhline(20, color='#64748B', linestyle='--', linewidth=1.2, alpha=0.7)

# Quadrant Labels
ax.text(28, 43, "CHRONIC OVER-FORECASTING\n[Working Capital & Waste Risk]", 
        ha='right', va='top', fontsize=9, fontweight='bold', color='#B91C1C',
        bbox=dict(boxstyle="square,pad=0.3", fc="#FEE2E2", ec="#FCA5A5", alpha=0.8))

ax.text(-28, 43, "CHRONIC UNDER-FORECASTING\n[Stockout & Lost Sales Risk]", 
        ha='left', va='top', fontsize=9, fontweight='bold', color='#B45309',
        bbox=dict(boxstyle="square,pad=0.3", fc="#FEF3C7", ec="#FCD34D", alpha=0.8))

ax.text(0, 5, "OPTIMAL CONVERGENCE ZONE (High Accuracy & Balanced)", 
        ha='center', va='bottom', fontsize=9, fontweight='bold', color='#047857',
        bbox=dict(boxstyle="square,pad=0.3", fc="#D1FAE5", ec="#6EE7B7", alpha=0.8))

ax.set_title("Portfolio Diagnostic: Bias (%) vs. WAPE Error (%) Matrix", fontsize=14, fontweight='bold', pad=15, color='#0F172A')
ax.set_xlabel("Systematic Bias (%) [ <0: Under-forecast | >0: Over-forecast ]", fontsize=11, fontweight='semibold', labelpad=10, color='#334155')
ax.set_ylabel("WAPE Error (%) [Lower is Better]", fontsize=11, fontweight='semibold', labelpad=10, color='#334155')
ax.set_xlim(-32, 32)
ax.set_ylim(0, 46)
ax.grid(True, linestyle=':', alpha=0.6, color='#CBD5E1')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "03_bias_accuracy_matrix.jpg"), format='jpg', dpi=200)
plt.close()

# -------------------------------------------------------------
# 4. S&OP CYCLE-OVER-CYCLE STABILITY HEATMAP
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#FFFFFF')

cycles = ['Cycle Jan 26', 'Cycle Feb 26', 'Cycle Mar 26', 'Cycle Apr 26', 'Cycle May 26', 'Cycle Jun 26']
target_months = ['Feb 26', 'Mar 26', 'Apr 26', 'May 26', 'Jun 26', 'Jul 26', 'Aug 26', 'Sep 26']

# Create matrix (NaN where target month is before cycle month)
data = np.full((len(cycles), len(target_months)), np.nan)

# Fill simulated accuracy values (Accuracy = 100 - WAPE)
for c_idx in range(len(cycles)):
    for t_idx in range(len(target_months)):
        lag = (t_idx + 1) - c_idx # lag 1, 2, 3...
        if lag >= 1:
            base_acc = 92.0 - (lag - 1) * 3.5 + np.random.uniform(-1.5, 1.5)
            data[c_idx, t_idx] = max(min(base_acc, 96.0), 68.0)

cmap = plt.cm.RdYlGn
im = ax.imshow(data, cmap=cmap, vmin=65, vmax=96, aspect='auto')

# Labels and ticks
ax.set_xticks(np.arange(len(target_months)))
ax.set_yticks(np.arange(len(cycles)))
ax.set_xticklabels(target_months, fontsize=10, fontweight='semibold', color='#334155')
ax.set_yticklabels(cycles, fontsize=10, fontweight='semibold', color='#334155')

# Text annotations inside cells
for i in range(len(cycles)):
    for j in range(len(target_months)):
        val = data[i, j]
        if not np.isnan(val):
            text_color = '#FFFFFF' if val < 75 or val > 91 else '#1E293B'
            ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                    color=text_color, fontsize=9, fontweight="bold")
        else:
            ax.text(j, i, "—", ha="center", va="center", color="#94A3B8", fontsize=12)

cbar = ax.figure.colorbar(im, ax=ax, orientation='vertical', pad=0.03, fraction=0.046)
cbar.set_label('Forecast Accuracy (%)', rotation=90, labelpad=12, fontweight='semibold', color='#334155')

ax.set_title("S&OP Cycle Stability: Accuracy (%) by Planning Cycle vs. Target Month", fontsize=14, fontweight='bold', pad=15, color='#0F172A')
ax.set_xlabel("Target Forecasted Period", fontsize=11, fontweight='semibold', labelpad=10, color='#334155')
ax.set_ylabel("S&OP Execution Cycle", fontsize=11, fontweight='semibold', labelpad=10, color='#334155')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "04_cycle_heatmap.jpg"), format='jpg', dpi=200)
plt.close()

# -------------------------------------------------------------
# 5. CONSOLIDATED EXECUTIVE COCKPIT MOCKUP
# -------------------------------------------------------------
fig = plt.figure(figsize=(14, 8.5), dpi=200)
fig.patch.set_facecolor('#0F172A') # Dark Executive Cockpit Theme

# Header
plt.figtext(0.04, 0.945, "DCH Insights | Forecast Accuracy & FVA Cockpit", color='#F8FAFC', fontsize=16, fontweight='bold')
plt.figtext(0.04, 0.915, "Real-time S&OP Performance Monitoring  •  Target Horizon: Lag 1 to 6  •  Portfolio: All Markets", color='#94A3B8', fontsize=9.5)

# 4 KPI Summary Cards at top
kpis = [
    ("CONSOLIDATED WAPE", "14.2%", "Accuracy: 85.8% (+1.2% MoM)", "#38BDF8"),
    ("PORTFOLIO BIAS", "+2.1%", "Slight Over-forecast (Controlled)", "#34D399"),
    ("FORECAST VALUE ADD", "+3.4%", "Human Edits vs. Machine Baseline", "#A78BFA"),
    ("CAPITAL AT RISK", "€ 142.5K", "Based on Lag 1 Unit Deviations", "#F87171")
]

# Total horizontal width available: from 0.04 to 0.96 = 0.92
# 4 cards with 3 gaps in between
# Card width = 0.215, Gap = 0.02 -> 4 * 0.215 + 3 * 0.02 = 0.86 + 0.06 = 0.92 (zero overlap!)
card_w = 0.215
gap = 0.02
card_y = 0.74
card_h = 0.13

for idx, (label, val, sub, col) in enumerate(kpis):
    x0 = 0.04 + idx * (card_w + gap)
    # Card Background with crisp border and round corners without pad bleeding
    rect = patches.FancyBboxPatch((x0, card_y), card_w, card_h,
                                  boxstyle=patches.BoxStyle("Round", pad=0.0, rounding_size=0.015),
                                  facecolor='#1E293B', edgecolor='#334155', linewidth=1.2, transform=fig.transFigure)
    fig.patches.append(rect)
    
    # Text inside each card
    plt.figtext(x0 + 0.012, card_y + 0.095, label, color='#94A3B8', fontsize=8.5, fontweight='bold')
    plt.figtext(x0 + 0.012, card_y + 0.045, val, color=col, fontsize=19, fontweight='bold')
    plt.figtext(x0 + 0.012, card_y + 0.016, sub, color='#CBD5E1', fontsize=7.8)

# Panel 1: Funnel mini
ax1 = fig.add_axes([0.04, 0.10, 0.43, 0.56])
ax1.set_facecolor('#1E293B')
ax1.plot([6, 5, 4, 3, 2, 1], [32.5, 27.8, 22.4, 18.2, 14.8, 11.5], marker='o', color='#38BDF8', lw=2.5, label='Portfolio Avg')
ax1.plot([6, 5, 4, 3, 2, 1], [24.0, 21.2, 17.5, 14.0, 11.2, 8.5], marker='^', color='#34D399', lw=2, label='Core Fast Moving')
ax1.invert_xaxis()
ax1.set_title("The Accuracy Funnel (Error % by Lag)", color='#F8FAFC', fontsize=11, fontweight='bold', pad=10)
ax1.set_xlabel("Planning Lag (Periods Ahead)", color='#94A3B8', fontsize=9)
ax1.set_ylabel("WAPE Error (%)", color='#94A3B8', fontsize=9)
ax1.tick_params(colors='#94A3B8')
ax1.grid(True, linestyle='--', alpha=0.2, color='#64748B')
ax1.legend(facecolor='#0F172A', edgecolor='#334155', labelcolor='#F8FAFC', fontsize=8)

# Panel 2: FVA Waterfall mini
ax2 = fig.add_axes([0.53, 0.10, 0.43, 0.56])
ax2.set_facecolor('#1E293B')
w_stages = ['SO99 Base', 'Sales KAM', 'Demand Plan', 'Consensus']
w_vals = [17.8, 16.3, 14.2, 14.4]
bars = ax2.bar(w_stages, w_vals, color=['#38BDF8', '#34D399', '#34D399', '#A78BFA'], width=0.5, edgecolor='#0F172A')
for bar, val in zip(bars, w_vals):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 0.3, f"{val:.1f}%", ha='center', color='#F8FAFC', fontsize=9, fontweight='bold')
ax2.set_title("Forecast Value Add (WAPE % by Workflow Level)", color='#F8FAFC', fontsize=11, fontweight='bold', pad=10)
ax2.set_ylabel("WAPE Error (%)", color='#94A3B8', fontsize=9)
ax2.tick_params(colors='#94A3B8')
ax2.set_ylim(0, 22)
ax2.grid(True, axis='y', linestyle='--', alpha=0.2, color='#64748B')

plt.savefig(os.path.join(output_dir, "00_executive_cockpit_simulation.jpg"), format='jpg', dpi=200)
plt.close()

# -------------------------------------------------------------
# 6. CONSOLIDATED EXECUTIVE COCKPIT MOCKUP (LIGHT THEME)
# -------------------------------------------------------------
fig = plt.figure(figsize=(14, 8.5), dpi=200)
fig.patch.set_facecolor('#F8FAFC') # Clean Modern Light Theme

# Header
plt.figtext(0.04, 0.945, "DCH Insights | Forecast Accuracy & FVA Cockpit", color='#0F172A', fontsize=16, fontweight='bold')
plt.figtext(0.04, 0.915, "Real-time S&OP Performance Monitoring  •  Target Horizon: Lag 1 to 6  •  Portfolio: All Markets", color='#64748B', fontsize=9.5)

# 4 KPI Summary Cards at top (Light Theme)
kpis_light = [
    ("CONSOLIDATED WAPE", "14.2%", "Accuracy: 85.8% (+1.2% MoM)", "#0284C7", "#E0F2FE", "#BAE6FD"),
    ("PORTFOLIO BIAS", "+2.1%", "Slight Over-forecast (Controlled)", "#059669", "#D1FAE5", "#A7F3D0"),
    ("FORECAST VALUE ADD", "+3.4%", "Human Edits vs. Machine Baseline", "#7C3AED", "#EDE9FE", "#DDD6FE"),
    ("CAPITAL AT RISK", "€ 142.5K", "Based on Lag 1 Unit Deviations", "#DC2626", "#FEE2E2", "#FECACA")
]

card_w = 0.215
gap = 0.02
card_y = 0.74
card_h = 0.13

for idx, (label, val, sub, text_col, bg_col, border_col) in enumerate(kpis_light):
    x0 = 0.04 + idx * (card_w + gap)
    rect = patches.FancyBboxPatch((x0, card_y), card_w, card_h,
                                  boxstyle=patches.BoxStyle("Round", pad=0.0, rounding_size=0.015),
                                  facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=1.2, transform=fig.transFigure)
    fig.patches.append(rect)
    
    # Left accent strip inside card
    accent = patches.FancyBboxPatch((x0, card_y), 0.006, card_h,
                                    boxstyle=patches.BoxStyle("Round", pad=0.0, rounding_size=0.003),
                                    facecolor=text_col, edgecolor=text_col, transform=fig.transFigure)
    fig.patches.append(accent)

    plt.figtext(x0 + 0.015, card_y + 0.095, label, color='#475569', fontsize=8.5, fontweight='bold')
    plt.figtext(x0 + 0.015, card_y + 0.045, val, color=text_col, fontsize=19, fontweight='bold')
    plt.figtext(x0 + 0.015, card_y + 0.016, sub, color='#64748B', fontsize=7.8)

# Panel 1: Funnel mini (Light)
ax1 = fig.add_axes([0.04, 0.10, 0.43, 0.56])
ax1.set_facecolor('#FFFFFF')
ax1.plot([6, 5, 4, 3, 2, 1], [32.5, 27.8, 22.4, 18.2, 14.8, 11.5], marker='o', color='#0284C7', lw=2.5, label='Portfolio Avg')
ax1.plot([6, 5, 4, 3, 2, 1], [24.0, 21.2, 17.5, 14.0, 11.2, 8.5], marker='^', color='#059669', lw=2, label='Core Fast Moving')
ax1.invert_xaxis()
ax1.set_title("The Accuracy Funnel (Error % by Lag)", color='#0F172A', fontsize=11, fontweight='bold', pad=10)
ax1.set_xlabel("Planning Lag (Periods Ahead)", color='#475569', fontsize=9)
ax1.set_ylabel("WAPE Error (%)", color='#475569', fontsize=9)
ax1.tick_params(colors='#475569')
for spine in ax1.spines.values():
    spine.set_color('#CBD5E1')
ax1.grid(True, linestyle='--', alpha=0.5, color='#E2E8F0')
ax1.legend(facecolor='#FFFFFF', edgecolor='#CBD5E1', labelcolor='#1E293B', fontsize=8)

# Panel 2: FVA Waterfall mini (Light)
ax2 = fig.add_axes([0.53, 0.10, 0.43, 0.56])
ax2.set_facecolor('#FFFFFF')
w_stages = ['SO99 Base', 'Sales KAM', 'Demand Plan', 'Consensus']
w_vals = [17.8, 16.3, 14.2, 14.4]
bars = ax2.bar(w_stages, w_vals, color=['#0284C7', '#059669', '#059669', '#7C3AED'], width=0.5, edgecolor='#E2E8F0')
for bar, val in zip(bars, w_vals):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 0.3, f"{val:.1f}%", ha='center', color='#0F172A', fontsize=9, fontweight='bold')
ax2.set_title("Forecast Value Add (WAPE % by Workflow Level)", color='#0F172A', fontsize=11, fontweight='bold', pad=10)
ax2.set_ylabel("WAPE Error (%)", color='#475569', fontsize=9)
ax2.tick_params(colors='#475569')
for spine in ax2.spines.values():
    spine.set_color('#CBD5E1')
ax2.set_ylim(0, 22)
ax2.grid(True, axis='y', linestyle='--', alpha=0.5, color='#E2E8F0')

plt.savefig(os.path.join(output_dir, "00_executive_cockpit_simulation_light.jpg"), format='jpg', dpi=200)
plt.close()

# -------------------------------------------------------------
# 7. TOUCHLESS PLANNING & FVA LEAGUE TABLE (05_touchless_matrix.jpg)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.8), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#FFFFFF')

categories = [
    'Dry Grocery & Cereals',
    'Core Mineral Waters',
    'Standard Sauces & Oils',
    'Confectionery & Treats',
    'Seasonal Beverages',
    'Fresh Dairy & Yogurts',
    'Promotional Limited Ed.'
]
so99_base_acc = np.array([92.5, 91.0, 88.5, 84.0, 78.5, 75.0, 68.0])
final_consensus_acc = np.array([91.8, 91.2, 88.0, 86.8, 83.2, 81.5, 77.5])
fva_gain = final_consensus_acc - so99_base_acc

y_pos = np.arange(len(categories))
bar_height = 0.35

rects1 = ax.barh(y_pos - bar_height/2, so99_base_acc, bar_height, label='SO99 Statistical Baseline', color='#93C5FD', edgecolor='#3B82F6')
rects2 = ax.barh(y_pos + bar_height/2, final_consensus_acc, bar_height, label='Final Human Consensus', color='#10B981', edgecolor='#059669')

# Annotate FVA badges on the right
for i in range(len(categories)):
    val = fva_gain[i]
    if val >= 2.0:
        badge_text = f"+{val:.1f}% FVA (High Value Added)"
        b_color = '#065F46'
        bg = '#D1FAE5'
        edge = '#6EE7B7'
    elif val > 0:
        badge_text = f"+{val:.1f}% FVA (Moderate)"
        b_color = '#047857'
        bg = '#ECFDF5'
        edge = '#A7F3D0'
    else:
        badge_text = f"{val:.1f}% FVA (Touchless Candidate)"
        b_color = '#991B1B'
        bg = '#FEE2E2'
        edge = '#FCA5A5'
    
    ax.text(max(so99_base_acc[i], final_consensus_acc[i]) + 1.2, y_pos[i], badge_text,
            va='center', fontsize=8.5, fontweight='bold', color=b_color,
            bbox=dict(boxstyle="round,pad=0.25", fc=bg, ec=edge, lw=0.9))

# Dividing line between touchless and human zones
ax.axhline(2.5, color='#DC2626', linestyle=':', linewidth=1.5, alpha=0.7)
ax.text(62, 1.2, "TOUCHLESS PLANNING ZONE\n(High machine accuracy, human edits add zero/negative value)",
        fontsize=8.5, fontweight='bold', color='#B91C1C', bbox=dict(boxstyle="square,pad=0.3", fc="#FEF2F2", ec="#FECACA"))
ax.text(62, 4.5, "HUMAN COLLABORATION FOCUS ZONE\n(Volatile/Seasonal, human overrides add +3% to +9% FVA)",
        fontsize=8.5, fontweight='bold', color='#047857', bbox=dict(boxstyle="square,pad=0.3", fc="#F0FDF4", ec="#BBF7D0"))

ax.set_yticks(y_pos)
ax.set_yticklabels(categories, fontsize=9.5, fontweight='semibold', color='#334155')
ax.invert_yaxis()
ax.set_xlim(60, 105)
ax.set_xlabel("Accuracy Rate % [Higher is Better]", fontsize=10.5, fontweight='semibold', labelpad=10, color='#334155')
ax.set_title("Touchless Planning Candidate Matrix: SO99 Baseline vs. Human S&OP", fontsize=13, fontweight='bold', pad=15, color='#0F172A')
ax.grid(True, axis='x', linestyle='--', alpha=0.5, color='#E2E8F0')
ax.legend(loc='lower right', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "05_touchless_matrix.jpg"), format='jpg', dpi=200)
plt.close()

# -------------------------------------------------------------
# 8. WORKING CAPITAL & FINANCIAL EXPOSURE (06_economic_exposure.jpg)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.8), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#FFFFFF')

cat_fin = ['Soft Drinks', 'Dairy Products', 'Snacks & Crisps', 'Pasta & Cereal', 'Frozen Foods', 'Personal Care']
over_exp = np.array([420, 280, 190, 85, 340, 110])    # Excess Stock / Holding Risk (k€)
under_exp = np.array([180, 310, 120, 60, 150, 195])   # Stockout / Lost Sales Risk (k€)

x = np.arange(len(cat_fin))
width = 0.38

rects_over = ax.bar(x - width/2, over_exp, width, label='Over-forecast: Working Capital Bloat (Excess Inventory)', color='#F87171', edgecolor='#DC2626')
rects_under = ax.bar(x + width/2, under_exp, width, label='Under-forecast: Revenue at Risk (Potential Stockout)', color='#FB923C', edgecolor='#EA580C')

for bar in rects_over:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 8, f"€{h}K", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#991B1B')

for bar in rects_under:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 8, f"€{h}K", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#9A3412')

ax.set_xticks(x)
ax.set_xticklabels(cat_fin, fontsize=9.5, fontweight='semibold', color='#334155')
ax.set_ylabel("Monetary Exposure (Thousands of €)", fontsize=10.5, fontweight='semibold', labelpad=10, color='#334155')
ax.set_ylim(0, 500)
ax.set_title("Economic Impact & Working Capital Exposure by Product Family", fontsize=13, fontweight='bold', pad=15, color='#0F172A')
ax.grid(True, axis='y', linestyle='--', alpha=0.5, color='#E2E8F0')
ax.legend(loc='upper right', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9)

# Summary badge
total_risk = (np.sum(over_exp) + np.sum(under_exp)) / 1000.0
ax.text(0.03, 0.92, f"Total S&OP Financial Exposure: €{total_risk:.2f} Million",
        transform=ax.transAxes, fontsize=10, fontweight='bold', color='#1E293B',
        bbox=dict(boxstyle="round,pad=0.4", fc="#EFF6FF", ec="#93C5FD"))

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "06_economic_exposure.jpg"), format='jpg', dpi=200)
plt.close()

# -------------------------------------------------------------
# 9. ABC / XYZ ACCURACY MATRIX (07_abc_xyz_matrix.jpg)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5.8), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#FFFFFF')

# Matrix: Rows = A, B, C; Cols = X, Y, Z
# Values: Average WAPE (%)
abc_labels = ['A (Top 80% Rev)', 'B (Next 15% Rev)', 'C (Tail 5% Rev)']
xyz_labels = ['X (Low Volatility)', 'Y (Seasonal / Cyclical)', 'Z (Erratic / Intermittent)']

# Simulated WAPE matrix
matrix_wape = np.array([
    [7.8,  14.2, 26.5],   # A items
    [12.4, 19.8, 34.0],   # B items
    [18.5, 29.0, 48.2]    # C items
])

cmap = plt.cm.RdYlGn_r # Red = High Error, Green = Low Error
im = ax.imshow(matrix_wape, cmap=cmap, vmin=5, vmax=50, aspect='auto')

ax.set_xticks(np.arange(len(xyz_labels)))
ax.set_yticks(np.arange(len(abc_labels)))
ax.set_xticklabels(xyz_labels, fontsize=10, fontweight='semibold', color='#334155')
ax.set_yticklabels(abc_labels, fontsize=10, fontweight='semibold', color='#334155')

for i in range(len(abc_labels)):
    for j in range(len(xyz_labels)):
        val = matrix_wape[i, j]
        tc = '#FFFFFF' if val > 30 or val < 10 else '#1E293B'
        status = "Target: <10%" if (i==0 and j==0) else ("High Risk" if (i==0 and j>0) else "Tolerable Tail")
        ax.text(j, i, f"{val:.1f}% WAPE\n({status})", ha='center', va='center',
                fontsize=9, fontweight='bold', color=tc)

cbar = ax.figure.colorbar(im, ax=ax, orientation='vertical', pad=0.03, fraction=0.046)
cbar.set_label('Error Rate - WAPE (%)', rotation=90, labelpad=12, fontweight='semibold', color='#334155')

ax.set_title("ABC / XYZ Portfolio Accuracy Matrix: Segmentation Diagnostic", fontsize=13, fontweight='bold', pad=15, color='#0F172A')
ax.set_xlabel("Demand Volatility (XYZ Segmentation)", fontsize=10.5, fontweight='semibold', labelpad=10, color='#334155')
ax.set_ylabel("Revenue Importance (ABC)", fontsize=10.5, fontweight='semibold', labelpad=10, color='#334155')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "07_abc_xyz_matrix.jpg"), format='jpg', dpi=200)
plt.close()

# -------------------------------------------------------------
# 10. PROMOTION VS BASELINE SPLIT (08_promo_split.jpg)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.8), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#FFFFFF')

months_promo = ['Jan 26', 'Feb 26', 'Mar 26 (Easter Promo)', 'Apr 26', 'May 26', 'Jun 26 (Summer Promo)']
base_wape = np.array([11.2, 12.0, 11.5, 12.4, 11.8, 12.1])
promo_wape = np.array([np.nan, np.nan, 29.5, np.nan, np.nan, 34.2])
total_wape = np.array([11.2, 12.0, 19.8, 12.4, 11.8, 23.4])

x = np.arange(len(months_promo))

ax.plot(x, total_wape, marker='o', color='#3B82F6', linewidth=2.8, label='Consolidated WAPE (Blended Portfolio)')
ax.plot(x, base_wape, marker='s', color='#10B981', linewidth=2.5, linestyle='--', label='Baseline Non-Promotional Accuracy')

# Bar indicator for promo error spikes
promo_bars = [p if not np.isnan(p) else 0 for p in promo_wape]
ax.bar(x, promo_bars, width=0.35, color='#F87171', alpha=0.6, label='Isolated Promotional Uplift Error', edgecolor='#DC2626')

for i in range(len(months_promo)):
    if not np.isnan(promo_wape[i]):
        ax.annotate(f"Promo Error:\n{promo_wape[i]:.1f}% WAPE", xy=(x[i], promo_wape[i]), xytext=(0, 10),
                    textcoords='offset points', ha='center', fontsize=8.5, fontweight='bold', color='#991B1B',
                    bbox=dict(boxstyle="round,pad=0.25", fc="#FEE2E2", ec="#FCA5A5"))
    ax.text(x[i], base_wape[i] - 2.0, f"{base_wape[i]:.1f}%", ha='center', fontsize=8.5, color='#065F46', fontweight='semibold')

ax.set_xticks(x)
ax.set_xticklabels(months_promo, fontsize=9.5, fontweight='semibold', color='#334155')
ax.set_ylabel("WAPE Error (%)", fontsize=10.5, fontweight='semibold', labelpad=10, color='#334155')
ax.set_ylim(0, 42)
ax.set_title("Promotional vs. Baseline Demand Accuracy Split (IsPromo Effect)", fontsize=13, fontweight='bold', pad=15, color='#0F172A')
ax.grid(True, linestyle='--', alpha=0.5, color='#E2E8F0')
ax.legend(loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "08_promo_split.jpg"), format='jpg', dpi=200)
plt.close()

# -------------------------------------------------------------
# 11. MULTI-LAG HORIZON HEATMAP / TRIANGLE REPORT (09_vintage_triangle.jpg)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.8), dpi=200)
fig.patch.set_facecolor('#F8FAFC')
ax.set_facecolor('#FFFFFF')

n_months = 7
triangle_data = np.full((n_months, n_months), np.nan)
month_names = ['Jan 26', 'Feb 26', 'Mar 26', 'Apr 26', 'May 26', 'Jun 26', 'Jul 26']

for i in range(n_months): # Cycle
    for j in range(i, n_months): # Target
        lag = (j - i) + 1
        acc = max(94.0 - (lag - 1) * 3.8 + np.random.uniform(-1.0, 1.0), 65.0)
        triangle_data[i, j] = acc

im = ax.imshow(triangle_data, cmap=plt.cm.YlGn, vmin=70, vmax=95, aspect='auto')

ax.set_xticks(np.arange(n_months))
ax.set_yticks(np.arange(n_months))
ax.set_xticklabels(month_names, fontsize=9.5, fontweight='semibold', color='#334155')
ax.set_yticklabels([f"Cycle {m}" for m in month_names], fontsize=9.5, fontweight='semibold', color='#334155')

for i in range(n_months):
    for j in range(n_months):
        val = triangle_data[i, j]
        if not np.isnan(val):
            lag = (j - i) + 1
            ax.text(j, i, f"Lag {lag}\n{val:.1f}%", ha='center', va='center',
                    fontsize=8.5, fontweight='bold', color='#1E293B')
        else:
            ax.text(j, i, "—", ha='center', va='center', color='#CBD5E1')

cbar = ax.figure.colorbar(im, ax=ax, orientation='vertical', pad=0.03, fraction=0.046)
cbar.set_label('Forecast Accuracy (%)', rotation=90, labelpad=12, fontweight='semibold', color='#334155')

ax.set_title("Multi-Lag Horizon Triangle Report (Forecast Vintage Aging)", fontsize=13, fontweight='bold', pad=15, color='#0F172A')
ax.set_xlabel("Target Forecasted Period", fontsize=10.5, fontweight='semibold', labelpad=10, color='#334155')
ax.set_ylabel("S&OP Creation Cycle", fontsize=10.5, fontweight='semibold', labelpad=10, color='#334155')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "09_vintage_triangle.jpg"), format='jpg', dpi=200)
plt.close()

print("All simulation images (including light cockpit and advanced roadmap views) successfully generated!")
