import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "        # ── 3) 버블차트 SVG 생성 함수 ──"
end_marker = "        st.markdown(_chart_html, unsafe_allow_html=True)"

idx_start = content.find(start_marker)
idx_end = content.find(end_marker, idx_start)

if idx_start != -1 and idx_end != -1:
    new_block = """        # ── 3) 콤보차트 SVG 생성 함수 ──
        def _make_combo_svg(bar_dict, line_dict, color_pos, color_neg, bar_label, line_label, fmt_bar, fmt_line):
            W, H = 460, 220
            PAD_L, PAD_R, PAD_T, PAD_B = 24, 16, 40, 32
            plot_w = W - PAD_L - PAD_R
            plot_h = H - PAD_T - PAD_B

            months_with_data = [m for m in range(1, 13) if bar_dict.get(m, 0) != 0 or line_dict.get(m, 0) != 0]
            if not months_with_data:
                return f'<svg width="{W}" height="{H}"><text x="{W//2}" y="{H//2}" fill="#666" text-anchor="middle" font-size="13">데이터 없음</text></svg>'

            bar_vals = [bar_dict.get(m, 0) for m in range(1, 13)]
            b_min, b_max = min(bar_vals + [0]), max(bar_vals + [0])
            if b_max == b_min: b_max += 1

            line_vals = [line_dict.get(m, 0) for m in range(1, 13)]
            l_min, l_max = min(line_vals + [0]), max(line_vals + [0])
            if l_max == l_min: l_max += 1

            def x_pos(m):
                return PAD_L + int((m - 1) / 11.0 * plot_w) if len(months_with_data) > 1 else PAD_L + plot_w // 2

            def bar_y_pos(v):
                return PAD_T + int((1 - (v - b_min) / (b_max - b_min)) * plot_h)

            def line_y_pos(v):
                return PAD_T + 10 + int((1 - (v - l_min) / (l_max - l_min)) * (plot_h - 20))

            svg = f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
            svg += f'<rect width="{W}" height="{H}" fill="#111" rx="10"/>'
            
            y0_bar = bar_y_pos(0)
            svg += f'<line x1="{PAD_L}" y1="{y0_bar}" x2="{W-PAD_R}" y2="{y0_bar}" stroke="#444" stroke-width="1" stroke-dasharray="4,3"/>'
            
            bar_width = 18
            
            for m in range(1, 13):
                bv = bar_dict.get(m, 0)
                lv = line_dict.get(m, 0)
                if bv == 0 and lv == 0:
                    svg += f'<text x="{x_pos(m)}" y="{H-PAD_B+16}" fill="#555" text-anchor="middle" font-size="10">{m}</text>'
                    continue
                    
                cx = x_pos(m)
                clr = color_pos if bv >= 0 else color_neg
                
                y_b = bar_y_pos(bv)
                if bv >= 0:
                    rect_y, rect_h = y_b, y0_bar - y_b
                else:
                    rect_y, rect_h = y0_bar, y_b - y0_bar
                rect_h = max(rect_h, 2)
                
                svg += f'<rect x="{cx - bar_width//2}" y="{rect_y}" width="{bar_width}" height="{rect_h}" fill="{clr}" fill-opacity="0.3" stroke="{clr}" stroke-width="1.5" rx="3"/>'
                
                lbl_b = fmt_bar(bv)
                if lbl_b:
                    text_y = rect_y - 4 if bv >= 0 else rect_y + rect_h + 10
                    svg += f'<text x="{cx}" y="{text_y}" fill="{clr}" fill-opacity="0.8" text-anchor="middle" font-size="9" font-weight="bold">{lbl_b}</text>'
                
                svg += f'<text x="{cx}" y="{H-PAD_B+16}" fill="#aaa" text-anchor="middle" font-size="10">{m}월</text>'

            pts = []
            for m in range(1, 13):
                if bar_dict.get(m, 0) == 0 and line_dict.get(m, 0) == 0: continue
                pts.append(f"{x_pos(m)},{line_y_pos(line_dict.get(m, 0))}")
            if pts:
                svg += f'<polyline points="{" ".join(pts)}" fill="none" stroke="white" stroke-width="2" stroke-opacity="0.9"/>'

            for m in range(1, 13):
                lv = line_dict.get(m, 0)
                if bar_dict.get(m, 0) == 0 and lv == 0: continue
                cx = x_pos(m)
                cy = line_y_pos(lv)
                clr = color_pos if lv >= 0 else color_neg
                
                svg += f'<circle cx="{cx}" cy="{cy}" r="4" fill="{clr}" stroke="white" stroke-width="1.5"/>'
                lbl_l = fmt_line(lv)
                if lbl_l:
                    svg += f'<text x="{cx}" y="{cy - 8}" fill="white" text-anchor="middle" font-size="10" font-weight="900">{lbl_l}</text>'

            svg += f'<text x="{W-PAD_R}" y="{PAD_T-20}" fill="white" text-anchor="end" font-size="10" font-weight="bold">● {line_label}</text>'
            svg += f'<text x="{W-PAD_R - 80}" y="{PAD_T-20}" fill="{color_pos}" text-anchor="end" font-size="10" font-weight="bold">■ {bar_label}</text>'

            svg += '</svg>'
            return svg

        # ── 4) 차트1 콤보 SVG (수익금=Bar, 건수=Line) ──
        _svg1 = _make_combo_svg(
            _monthly_profits_c, _monthly_counts_c2,
            "#FF6B00", "#4B9FFF",
            "수익금", "매도건수",
            lambda v: f"{int(v/10000):,}만" if abs(v) >= 10000 else f"{int(v):,}",
            lambda v: f"{int(v)}건" if v > 0 else ""
        )

        # ── 5) 차트2 콤보 SVG (실현규모=Bar, 수익률=Line) ──
        _profit_as_count = {m: max(int(abs(_monthly_profits_c.get(m, 0)) / 100000), 1)
                            if _monthly_avg_rates2.get(m, 0) != 0 else 0
                            for m in range(1, 13)}
        _svg2 = _make_combo_svg(
            _profit_as_count, _monthly_avg_rates2,
            "#8A2BE2", "#4B9FFF",
            "실현규모", "평균수익률",
            lambda v: "",
            lambda v: f"{v:.1f}%"
        )

        # ── 6) 좌우 병렬 HTML 렌더링 ──
        _chart_html = f\"\"\"
<div style='display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;'>
  <div style='flex:1;min-width:300px;background:#111;border-radius:12px;padding:18px 16px 12px 16px;'>
    <div style='color:#FF6B00;font-size:13px;font-weight:bold;margin-bottom:4px;'>&#128200; 올해 팔아서 실제로 번 돈은</div>
    <div style='color:white;font-size:22px;font-weight:900;margin-bottom:12px;'>{_year_profit_c:,}원 이에요</div>
    {_svg1}
  </div>
  <div style='flex:1;min-width:300px;background:#111;border-radius:12px;padding:18px 16px 12px 16px;'>
    <div style='color:#8A2BE2;font-size:13px;font-weight:bold;margin-bottom:4px;'>&#128201; 올해 평균 수익률은</div>
    <div style='color:white;font-size:22px;font-weight:900;margin-bottom:12px;'>{_ytd} 이에요</div>
    {_svg2}
  </div>
</div>
\"\"\"\n"""
    new_content = content[:idx_start] + new_block + content[idx_end:]
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Replaced successfully")
else:
    print("Markers not found")
