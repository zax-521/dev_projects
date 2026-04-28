import os
import re
import shutil
import uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from bs4 import BeautifulSoup
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

app = FastAPI(title="SlideToEditable")

BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

SYSTEM_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
]

CHROME_PATH = None
for cp in SYSTEM_CHROME_PATHS:
    if os.path.isfile(cp):
        CHROME_PATH = cp
        break

BROWSER_LAUNCH_OPTIONS = {"headless": True, "args": ["--no-sandbox"]}
if CHROME_PATH:
    BROWSER_LAUNCH_OPTIONS["executable_path"] = CHROME_PATH


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="index.html not found")
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


def convert_to_pdf(html_path: str, output_path: str, lang: str):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(**BROWSER_LAUNCH_OPTIONS)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            device_scale_factor=2,
        )
        page = context.new_page()

        file_url = "file:///" + html_path.replace("\\", "/")
        page.goto(file_url, wait_until="load")

        try:
            page.evaluate(f"""
                (() => {{
                    // 1. Direct DOM class manipulation (most reliable)
                    document.querySelectorAll('.content-ru, .content-en, .content-zh').forEach(el => {{
                        el.classList.remove('active');
                    }});
                    document.querySelectorAll('.content-{lang}').forEach(el => {{
                        el.classList.add('active');
                    }});
                    // 2. Try clicking the corresponding language button too
                    const langTextMap = {{'ru': ['ru','рус','рос'], 'en': ['en','eng','анг'], 'zh': ['zh','cn','chi','中文','кит']}};
                    const texts = langTextMap['{lang}'] || ['{lang}'];
                    document.querySelectorAll('.lang-btn').forEach(b => {{
                        const lower = b.textContent.toLowerCase().trim();
                        if (texts.some(t => lower.includes(t))) {{
                            b.dispatchEvent(new MouseEvent('click', {{bubbles: true}}));
                        }}
                    }});
                }})();
            """)
            page.wait_for_timeout(500)
        except Exception:
            pass

        hide_script = """
        (() => {
            const selectors = [
                '.nav-btn', '.nav-button', '.navigation',
                '.download-btn', '.download-button', '.download',
                '.progress-bar', '.progress',
                '.control-btn', '.controls',
                'button', '.btn',
                '.lang-btn', '.language-selector',
                '.toolbar', '.menu',
            ];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.style.opacity = '0';
                    el.style.pointerEvents = 'none';
                });
            });
        })();
        """
        page.evaluate(hide_script)
        page.wait_for_timeout(300)

        page.evaluate("""
            (() => {
                const slides = document.querySelectorAll('.slide');
                if (!slides.length) return;
                // Make all slides visible
                slides.forEach(el => {
                    el.style.setProperty('display', 'flex', 'important');
                    el.style.setProperty('visibility', 'visible', 'important');
                    el.style.setProperty('opacity', '1', 'important');
                    el.style.setProperty('width', '100%', 'important');
                    el.style.setProperty('max-width', '100%', 'important');
                    el.style.setProperty('overflow', 'hidden', 'important');
                    el.style.setProperty('overflow-y', 'hidden', 'important');
                    el.classList.add('active');
                });
                // Move all slides into a clean container to avoid flex layout issues
                const pdfBox = document.createElement('div');
                pdfBox.id = 'pdf-container';
                pdfBox.style.setProperty('display', 'block', 'important');
                pdfBox.style.setProperty('width', '100%', 'important');
                slides.forEach(el => pdfBox.appendChild(el));
                // Clear body and append
                document.body.innerHTML = '';
                document.body.appendChild(pdfBox);
                document.body.style.setProperty('overflow', 'visible', 'important');
                document.body.style.setProperty('height', 'auto', 'important');
                document.body.style.setProperty('display', 'block', 'important');
                document.body.style.setProperty('margin', '0', 'important');
                document.body.style.setProperty('padding', '0', 'important');
                // Add page-break CSS
                const style = document.createElement('style');
                style.textContent = '.slide:not(:first-child) { page-break-before: always !important; }';
                document.head.appendChild(style);
            })();
        """)
        page.wait_for_timeout(200)

        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"},
        )

        context.close()
        browser.close()


def extract_hex_color(style_value: str) -> str | None:
    if not style_value:
        return None
    match = re.search(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})', style_value)
    if match:
        code = match.group(1)
        if len(code) == 3:
            code = "".join(c * 2 for c in code)
        return "#" + code
    match = re.search(r'background(?:-color)?\s*:\s*rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', style_value, re.IGNORECASE)
    if match:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return f"#{r:02x}{g:02x}{b:02x}"
    return None


def convert_to_pptx(html_path: str, output_path: str, lang: str):
    from playwright.sync_api import sync_playwright

    # First, extract text content via BeautifulSoup for editable text overlay
    with open(html_path, "r", encoding="utf-8", errors="replace") as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, "lxml")
    soup_slides = soup.find_all(class_="slide")

    with sync_playwright() as p:
        browser = p.chromium.launch(**BROWSER_LAUNCH_OPTIONS)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            device_scale_factor=2,
        )
        page = context.new_page()

        file_url = "file:///" + html_path.replace("\\", "/")
        page.goto(file_url, wait_until="load")

        # Language switching
        try:
            page.evaluate(f"""
                (() => {{
                    document.querySelectorAll('.content-ru, .content-en, .content-zh').forEach(el => {{
                        el.classList.remove('active');
                    }});
                    document.querySelectorAll('.content-{lang}').forEach(el => {{
                        el.classList.add('active');
                    }});
                    const langTextMap = {{'ru': ['ru','рус','рос'], 'en': ['en','eng','анг'], 'zh': ['zh','cn','chi','中文','кит']}};
                    const texts = langTextMap['{lang}'] || ['{lang}'];
                    document.querySelectorAll('.lang-btn').forEach(b => {{
                        const lower = b.textContent.toLowerCase().trim();
                        if (texts.some(t => lower.includes(t))) {{
                            b.dispatchEvent(new MouseEvent('click', {{bubbles: true}}));
                        }}
                    }});
                }})();
            """)
            page.wait_for_timeout(500)
        except Exception:
            pass

        # Hide interference elements
        page.evaluate("""
            (() => {
                const selectors = [
                    '.nav-btn', '.nav-button', '.navigation',
                    '.download-btn', '.download-button', '.download',
                    '.progress-bar', '.progress',
                    '.control-btn', '.controls',
                    '.lang-btn', '.language-selector',
                    '.toolbar', '.menu',
                ];
                selectors.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                        el.style.opacity = '0';
                        el.style.pointerEvents = 'none';
                    });
                });
            })();
        """)
        page.wait_for_timeout(300)

        # Get slide count
        slide_count = page.evaluate("document.querySelectorAll('.slide').length")
        if not slide_count:
            context.close()
            browser.close()
            raise ValueError("未在 HTML 中找到任何 class='slide' 的元素")

        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)

        blank_layout = prs.slide_layouts[6]

        for i in range(slide_count):
            # Show only current slide, hide others
            page.evaluate(f"""
                (() => {{
                    document.querySelectorAll('.slide').forEach((el, idx) => {{
                        if (idx === {i}) {{
                            el.style.setProperty('display', 'flex', 'important');
                            el.style.setProperty('visibility', 'visible', 'important');
                            el.style.setProperty('opacity', '1', 'important');
                            el.style.setProperty('position', 'relative', 'important');
                            el.style.setProperty('left', '0', 'important');
                            el.style.setProperty('top', '0', 'important');
                            el.classList.add('active');
                        }} else {{
                            el.style.setProperty('display', 'none', 'important');
                            el.style.setProperty('visibility', 'hidden', 'important');
                        }}
                    }});
                }})();
            """)
            page.wait_for_timeout(300)

            # Screenshot the current slide
            clip = page.evaluate(f"""
                (() => {{
                    const el = document.querySelectorAll('.slide')[{i}];
                    const rect = el.getBoundingClientRect();
                    return {{x: rect.x, y: rect.y, width: rect.width, height: rect.height}};
                }})();
            """)

            screenshot_path = str(UPLOAD_DIR / f"{uuid.uuid4().hex}_slide_{i}.png")
            page.screenshot(path=screenshot_path, clip=clip)

            # Add to PPTX
            new_slide = prs.slides.add_slide(blank_layout)

            # 1. Add screenshot as full-slide background image
            pic = new_slide.shapes.add_picture(
                screenshot_path,
                Inches(0), Inches(0),
                Inches(10), Inches(5.625),
            )

            # 2. Extract text from this slide for editable overlay
            slide_texts = []
            if i < len(soup_slides):
                slide_elem = soup_slides[i]
                # Try language-specific content first
                content_blocks = slide_elem.select(f".content-{lang}")
                if not content_blocks:
                    content_blocks = slide_elem.select('[class*="content-"]')
                if not content_blocks:
                    content_blocks = [slide_elem]

                for block in content_blocks:
                    for el in block.find_all(["h1", "h2", "h3", "p", "li"]):
                        text = el.get_text(strip=True)
                        if text:
                            slide_texts.append(text)

            # 3. Add editable text overlay (transparent text box)
            if slide_texts:
                txBox = new_slide.shapes.add_textbox(
                    Inches(0.3), Inches(0.2),
                    Inches(9.4), Inches(5.2),
                )
                tf = txBox.text_frame
                tf.word_wrap = True

                for j, text in enumerate(slide_texts):
                    if j == 0:
                        p = tf.paragraphs[0]
                    else:
                        p = tf.add_paragraph()
                    p.text = text
                    p.font.size = Pt(12)
                    p.font.color.rgb = RGBColor(0, 0, 0)
                    p.space_after = Pt(4)

            # Cleanup screenshot
            try:
                os.unlink(screenshot_path)
            except Exception:
                pass

        context.close()
        browser.close()

    prs.save(output_path)


def safe_unlink(path: Path):
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass


def cleanup_files(input_path: Path, output_path: Path):
    safe_unlink(input_path)
    safe_unlink(output_path)


@app.post("/convert")
def convert(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    type: str = Form(...),
    lang: str = Form("ru"),
):
    if not (file.filename or "").lower().endswith((".html", ".htm")):
        raise HTTPException(status_code=400, detail="仅支持 .html 文件")

    if type not in ("pdf", "pptx"):
        raise HTTPException(status_code=400, detail="type 必须是 pdf 或 pptx")

    input_filename = f"{uuid.uuid4().hex}_{file.filename}"
    input_path = UPLOAD_DIR / input_filename

    ext = ".pdf" if type == "pdf" else ".pptx"
    output_filename = f"{uuid.uuid4().hex}{ext}"
    output_path = OUTPUT_DIR / output_filename

    try:
        content = file.file.read()
        input_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件读取失败: {e}")
    finally:
        file.file.close()

    try:
        if type == "pdf":
            convert_to_pdf(str(input_path), str(output_path), lang)
        else:
            convert_to_pptx(str(input_path), str(output_path), lang)
    except ValueError as e:
        safe_unlink(input_path)
        safe_unlink(output_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        safe_unlink(input_path)
        safe_unlink(output_path)
        raise HTTPException(status_code=500, detail=f"转换失败: {e}")

    if not output_path.exists():
        safe_unlink(input_path)
        raise HTTPException(status_code=500, detail="转换失败：未生成输出文件")

    download_name = file.filename.rsplit(".", 1)[0] + ext

    background_tasks.add_task(cleanup_files, input_path, output_path)

    return FileResponse(
        path=str(output_path),
        filename=download_name,
        media_type="application/octet-stream",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)