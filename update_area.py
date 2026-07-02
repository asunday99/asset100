import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "        # ── 3) 콤보차트 SVG 생성 함수 ──"
end_marker = "        st.markdown(_chart_html, unsafe_allow_html=True)"

idx_start = content.find(start_marker)
idx_end = content.find(end_marker, idx_start)

if idx_start != -1 and idx_end != -1:
    new_block = """        # ── 3) 에리어차트 SVG 생성 함수 (대시보드와 동일한 스타일) ──
        def _make_area_svg(data_dict, c_left, c_right, y_fmt, chart_idx, c_bottom_right=None):
            W, H = 460, 200
            PAD_L, PAD_R, PAD_T, PAD_B = 48, 16, 20, 36
            plot_w = W - PAD_L - PAD_R
            plot_h = H - PAD_T - PAD_B
            months = sorted([m for m in range(1, 13) if data_dict.get(m, 0) != 0])
            if not months:
                return f'<svg width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="transparent" rx="10"/><text x="{W//2}" y="{H//2}" fill="#555" text-anchor="middle" font-size="13">데이터 없음</text></svg>'
            
            vals = [data_dict.get(m, 0) for m in months]
            y_max = max(vals) if max(vals) > 0 else 0
            y_min = min(vals) if min(vals) < 0 else 0
            
            y_range = max(y_max - y_min, 1)
            y_max = y_max + y_range * 0.15
            y_min = y_min - y_range * 0.15
            y_range = max(y_max - y_min, 1)
            
            def xp(idx): return PAD_L + int(idx / max(len(months) - 1, 1) * plot_w)
            def yp(v): return PAD_T + int((1 - (v - y_min) / y_range) * plot_h)
            
            pts = [(xp(i), yp(data_dict.get(m, 0))) for i, m in enumerate(months)]
            y0 = yp(0) if y_min < 0 else H - PAD_B
            area_pts = f"{PAD_L},{y0} " + " ".join(f"{x},{y}" for x, y in pts) + f" {pts[-1][0]},{y0}"
            line_pts = " ".join(f"{x},{y}" for x, y in pts)
            
            grad_id = f"grad_trade_{chart_idx}"
            mask_id = f"mask_trade_{chart_idx}"
            svg = f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
            svg += f'<defs>'
            svg += f'  <linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="0%">'
            svg += f'    <stop offset="0%" stop-color="{c_left}"/>'
            svg += f'    <stop offset="100%" stop-color="{c_right}"/>'
            svg += f'  </linearGradient>'
            svg += f'  <radialGradient id="light_trade_{chart_idx}" cx="100%" cy="0%" r="80%">'
            svg += f'    <stop offset="0%" stop-color="#ffffff" stop-opacity="0.85"/>'
            svg += f'    <stop offset="100%" stop-color="transparent" stop-opacity="0.0"/>'
            svg += f'  </radialGradient>'
            if c_bottom_right:
                svg += f'  <radialGradient id="mint_trade_{chart_idx}" cx="90%" cy="65%" r="60%">'
                svg += f'    <stop offset="0%" stop-color="{c_bottom_right}" stop-opacity="0.42"/>'
                svg += f'    <stop offset="100%" stop-color="transparent" stop-opacity="0.0"/>'
                svg += f'  </radialGradient>'
            svg += f'  <linearGradient id="fade_{mask_id}" x1="0%" y1="0%" x2="0%" y2="100%">'
            svg += f'    <stop offset="0%" stop-color="white" stop-opacity="1.0"/>'
            svg += f'    <stop offset="40%" stop-color="white" stop-opacity="0.7"/>'
            svg += f'    <stop offset="85%" stop-color="white" stop-opacity="0.0"/>'
            svg += f'    <stop offset="100%" stop-color="white" stop-opacity="0.0"/>'
            svg += f'  </linearGradient>'
            svg += f'  <mask id="{mask_id}">'
            svg += f'    <rect width="{W}" height="{H}" fill="url(#fade_{mask_id})" />'
            svg += f'  </mask>'
            svg += f'</defs>'
            svg += f'<rect width="{W}" height="{H}" fill="transparent" rx="10"/>'
            for gi in range(5):
                gy = PAD_T + int(gi / 4 * plot_h)
                svg += f'<line x1="{PAD_L}" y1="{gy}" x2="{W-PAD_R}" y2="{gy}" stroke="#333" stroke-width="1"/>'
            svg += f'<polygon points="{area_pts}" fill="url(#{grad_id})" mask="url(#{mask_id})"/>'
            if c_bottom_right:
                svg += f'<polygon points="{area_pts}" fill="url(#mint_trade_{chart_idx})" mask="url(#{mask_id})"/>'
            svg += f'<polygon points="{area_pts}" fill="url(#light_trade_{chart_idx})" mask="url(#{mask_id})"/>'
            svg += f'<polyline points="{line_pts}" fill="none" stroke="#ffffff" stroke-width="2.0" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 0 4px rgba(255,255,255,0.6))"/>'
            
            for i, (m, (x, y)) in enumerate(zip(months, pts)):
                svg += f'<circle cx="{x}" cy="{y}" r="4" fill="#ffffff" stroke="#111" stroke-width="1.5"/>'
                lbl = y_fmt(data_dict.get(m, 0))
                svg += f'<text x="{x}" y="{y-8}" fill="#ffffff" text-anchor="middle" font-size="11" font-weight="bold">{lbl}</text>'
                svg += f'<text x="{x}" y="{H-PAD_B+14}" fill="#888" text-anchor="middle" font-size="11">{m}월</text>'
            svg += '</svg>'
            return svg

        # ── 4) 차트1 에리어 SVG (수익금) ──
        _svg1 = _make_area_svg(_monthly_profits_c, "#A555C8", "#7ECBEE", lambda v: f"{int(v/10000):,}만" if abs(v) >= 10000 else f"{int(v):,}", 1)

        # ── 5) 차트2 에리어 SVG (평균수익률) ──
        _svg2 = _make_area_svg(_monthly_avg_rates2, "#BB5FED", "#CEACC0", lambda v: f"{v:.1f}%", 2, "#98FF98")

        # ── 6) 좌우 병렬 HTML 렌더링 ──
        _chart_html = f\"\"\"
<div style='display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;'>
  <div style='flex:1;min-width:300px;background:#000000;border:1px solid rgba(255, 218, 185, 0.5);border-radius:12px;padding:18px 16px 12px 16px;'>
    <div style='color:#FFDAB9;font-size:14px;font-weight:300;margin-bottom:4px;'>&#128200; 올해 확정된 수익은</div>
    <div style='color:rgba(245, 245, 245, 0.85);font-size:22px;font-weight:900;margin-bottom:12px;'>{_year_profit_c:,}원 이에요</div>
    {_svg1}
  </div>
  <div style='flex:1;min-width:300px;background:#000000;border:1px solid rgba(255, 218, 185, 0.5);border-radius:12px;padding:18px 16px 12px 16px;'>
    <div style='color:#FFDAB9;font-size:14px;font-weight:300;margin-bottom:4px;'>&#128201; 올해 매매 평균수익률은</div>
    <div style='color:rgba(245, 245, 245, 0.85);font-size:22px;font-weight:900;margin-bottom:12px;'>{_ytd} 이에요</div>
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
