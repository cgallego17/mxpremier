"""Styled Excel export utilities for the backoffice."""
from io import BytesIO
from django.http import HttpResponse
import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter

# Brand colours
GREEN_DK  = '0D3B1E'
GREEN_MD  = '1A6B35'
GOLD      = 'C8A830'
RED       = 'C41230'
CREAM     = 'F2EDDA'
GREY_ROW  = 'F7FAF7'
WHITE     = 'FFFFFF'

_thin = Side(style='thin', color='D0D0D0')
_border = Border(left=_thin, right=_thin, top=_thin, bottom=_thin)


def _fill(hex_color):
    return PatternFill('solid', fgColor=hex_color)


def _font(bold=False, color=WHITE, size=10):
    return Font(bold=bold, color=color, size=size, name='Calibri')


def _align(horizontal='left', vertical='center', wrap=False):
    return Alignment(
        horizontal=horizontal, vertical=vertical,
        wrap_text=wrap, shrink_to_fit=False,
    )


def workbook_response(filename):
    """Return an HttpResponse configured for an .xlsx download."""
    resp = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-officedocument'
            '.spreadsheetml.sheet'
        )
    )
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


def build_workbook(title, headers, rows, col_widths=None):
    """
    Build a styled openpyxl Workbook.

    headers : list of str
    rows    : list of lists (one per data row)
    col_widths : optional list of int column widths
    Returns (wb, ws).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = title[:31]

    n_cols = len(headers)

    # ── Title row (row 1) ──────────────────────────────────────
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols)
    title_cell = ws.cell(row=1, column=1, value=f'Estado 33 — {title}')
    title_cell.fill      = _fill(GREEN_DK)
    title_cell.font      = Font(bold=True, color=GOLD, size=13, name='Calibri')
    title_cell.alignment = _align('center')
    ws.row_dimensions[1].height = 26

    # ── Header row (row 2) ────────────────────────────────────
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=2, column=col_idx, value=header)
        cell.fill      = _fill(GREEN_MD)
        cell.font      = _font(bold=True, color=WHITE, size=10)
        cell.alignment = _align('center')
        cell.border    = _border
    ws.row_dimensions[2].height = 18

    # ── Data rows ──────────────────────────────────────────────
    for row_idx, row_data in enumerate(rows, start=3):
        fill = _fill(GREY_ROW) if row_idx % 2 == 1 else _fill(WHITE)
        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.fill      = fill
            cell.font      = _font(color='1A1A1A', size=10)
            cell.alignment = _align(wrap=True)
            cell.border    = _border
        ws.row_dimensions[row_idx].height = 16

    # ── Column widths ─────────────────────────────────────────
    if col_widths:
        for i, w in enumerate(col_widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
    else:
        # Auto-size: cap between 10 and 40 chars
        for col_idx in range(1, n_cols + 1):
            col_letter = get_column_letter(col_idx)
            max_len = max(
                (
                    len(str(ws.cell(row=r, column=col_idx).value or ''))
                    for r in range(2, ws.max_row + 1)
                ),
                default=10,
            )
            ws.column_dimensions[col_letter].width = min(max(max_len + 2, 10), 42)

    # Freeze panes below header
    ws.freeze_panes = 'A3'

    return wb, ws


def wb_to_response(wb, response):
    """Write workbook bytes into an HttpResponse."""
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    response.write(buf.read())
    return response
